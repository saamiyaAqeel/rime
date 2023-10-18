# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

"""
Trace provider data access for subsetting.
"""
from dataclasses import dataclass
from enum import Enum
import re
import shutil
from contextlib import contextmanager

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


SubsetFillOption = Enum('SubsetFillOption', ('MINIMAL', 'UNUSED_TABLES', 'UNUSED_DBS_AND_TABLES'))


@dataclass(frozen=True)
class SubsetOptions:
    """
    Should we copy additional unused tables and databases?
    MINIMAL: Don't copy anything that isn't referenced by the subset.
    UNUSED_TABLES: Create unused tables (but don't copy any data).
    UNUSED_DBS_AND_TABLES: Create unused tables and databases (but don't copy any data).
    """
    fill: SubsetFillOption = SubsetFillOption.MINIMAL

    anonymise: bool = False


class DeviceSubsetter:
    def __init__(self, fs_dest, subset_options: SubsetOptions):
        self._fs_dest = fs_dest

        self.options = subset_options

    def sqlite3_create(self, path):
        return self._fs_dest.sqlite3_create(path)

    def create_file(self, path):
        return self._fs_dest.create_file(path)


class _RowSubset:
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


class _CompleteTable:
    def __init__(self, table_name):
        self.table_name = table_name

    def copy(self, src_conn, dst_conn):
        _copy_table(src_conn, dst_conn, self.table_name, None)


class _DbSubset:
    def __init__(self):
        self.subsets = []

    def row_subset(self, table_name, primary_key):
        row_subset = _RowSubset(table_name, primary_key)
        self.subsets.append(row_subset)
        return row_subset

    def complete_table(self, table_name):
        complete_table = _CompleteTable(table_name)
        self.subsets.append(complete_table)
        return complete_table


class ProviderSubsetter:
    def __init__(self, device_subsetter: DeviceSubsetter, subset_options: SubsetOptions):
        self._device_subsetter = device_subsetter
        self.options = subset_options

    @contextmanager
    def db_subset(self, *, src_conn, new_db_pathname):
        db_subset = _DbSubset()
        yield db_subset
        with self._device_subsetter.sqlite3_create(new_db_pathname) as dst_conn:
            for row_subset in db_subset.subsets:
                row_subset.copy(src_conn, dst_conn)

    def copy_file(self, handle, dst_path):
        with self._device_subsetter.create_file(dst_path) as dest_handle:
            shutil.copyfileobj(handle, dest_handle)
