# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

"""
Trace provider data access for subsetting.
"""
import re
import shutil

from .sql import Table, Query, Parameter

MATCH_COLLATE = re.compile(r'COLLATE \w+', re.IGNORECASE)


def _sanitise_create_table_sql(sql):
    # Remove custom collation sequences.
    return MATCH_COLLATE.sub('', sql)


def _copy_table(src_conn, dst_conn, table_name, add_where_clause_fn):
    sql = src_conn.execute('select sql from sqlite_master where name = ?', (table_name,)).fetchone()[0]
    sql = _sanitise_create_table_sql(sql)

    dst_conn.execute(sql)

    table = Table(table_name)
    select_query = Query.from_(table) \
        .select('*')

    if add_where_clause_fn is not None:
        select_query = add_where_clause_fn(select_query, table)

    # Recreate each row.
    parameters = None
    for row in src_conn.execute(select_query.get_sql()):
        if parameters is None:
            parameters = [Parameter('?') for _ in row]
        insert_query = Query.into(table_name).insert(*parameters)
        dst_conn.execute(insert_query.get_sql(), row)


class RowSubset:
    def __init__(self, table_name, primary_key):
        self.table_name = table_name
        self.primary_key = primary_key
        self.rows = set()

    def add(self, pk):
        self.rows.add(pk)

    def update(self, pks):
        self.rows.update(pks)

    def copy(self, src_conn, dst_conn):
        _copy_table(
            src_conn,
            dst_conn,
            self.table_name,
            lambda query, table: query.where(table[self.primary_key].isin(self.rows)))


class CompleteTable:
    def __init__(self, table_name):
        self.table_name = table_name

    def copy(self, src_conn, dst_conn):
        _copy_table(src_conn, dst_conn, self.table_name, None)


class Subsetter:
    def __init__(self, fs_dest):
        self._fs_dest = fs_dest

    def row_subset(self, table_name, primary_key):
        return RowSubset(table_name, primary_key)

    def complete_table(self, table_name):
        return CompleteTable(table_name)

    def sqlite3_create(self, path):
        return self._fs_dest.sqlite3_create(path)

    def copy_file(self, handle, dst_path):
        with self._fs_dest.create_file(dst_path) as dest_handle:
            shutil.copyfileobj(handle, dest_handle)

    def create_db_and_copy_rows(self, src_conn, new_db_pathname, row_subsets: list[RowSubset]):
        """
        Convenience method to create a new database and copy row subsets from the source database.
        """
        with self._fs_dest.sqlite3_create(new_db_pathname) as dst_conn:
            for row_subset in row_subsets:
                row_subset.copy(src_conn, dst_conn)
