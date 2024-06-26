# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

"""
Thin wrapper around pypika with methods to perform subsetting and helpers in sqlite databases.
"""
import re
import sys

import pypika
import sqlite3

Table = pypika.Table
Query = pypika.Query
Column = pypika.Column
Parameter = pypika.Parameter


def _sqlite3_regexp_search(pattern, input):
    return bool(re.search(pattern, input))


_threadsafety = None


def _sqlite3_is_threadsafe():
    global _threadsafety

    if _threadsafety is None:
        if (sys.version_info.major, sys.version_info.minor) >= (3, 11):
            # Python >= 3.11 populates sqlite3.threadsafety dynamically
            _threadsafety = sqlite3.threadsafety
        else:
            # Python < 3.11 hard-codes sqlite3.threadsafety, so query the database.
            conn = sqlite3.connect(':memory:')
            res = conn.execute(
                "SELECT * FROM pragma_compile_options WHERE compile_options LIKE 'THREADSAFE%'"
            ).fetchone()[0]
            conn.close()

            SQLITE_THREADSAFE = int(res.split('=')[1])
            # This mapping defined under sqlite3.threadsafety in the Python docs.
            _threadsafety = {0: 0, 2: 1, 1: 3}.get(SQLITE_THREADSAFE, 0)

    return _threadsafety == 3


def sqlite3_connect(db_path, uri=False):
    """
    Connect to an sqlite3 database and add support for regular expression matching.
    If db_path is a file: URI, then set uri=True
    """
    # We current do not, but in future may, support caching connections across threads.
    check_same_thread = False

    if uri is False and db_path.startswith('file:'):
        raise ValueError(f"Supplied a URI-looking db_path of {db_path} but uri is False")

    if not _sqlite3_is_threadsafe():
        raise RuntimeError("RIME requires a thread-safe sqlite3 module (sqlite3.threadsafety == 3)")

    try:
        conn = sqlite3.connect(db_path, uri=uri, check_same_thread=check_same_thread)
        conn.create_function('REGEXP', 2, _sqlite3_regexp_search)
    except sqlite3.OperationalError as e:
        print(f"Error connecting to database {db_path} (uri={uri}): {e}", file=sys.stderr)
        raise

    return conn


def sqlite3_connect_filename(path, read_only=True):
    params = "?mode=ro&immutable=1" if read_only else ""
    return sqlite3_connect(f"file://{path}{params}", uri=True)


def get_field_indices(query):
    return {select.alias or select.name: idx for idx, select in enumerate(query._selects)}
