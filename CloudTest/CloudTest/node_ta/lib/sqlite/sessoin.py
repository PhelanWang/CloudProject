# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Jul 13 2018, 13:06:57) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-28)]
# Embedded file name: /root/git/ovirt/noda_ta/lib/sqlite/session.py
# Compiled at: 2016-05-23 10:39:39
__author__ = 'Henry.K'
import sqlite3

class SqliteSession:

    def __init__(self, connection_string, use_row_factory=(
 False, None)):
        self.connected = False
        self.error = 'null'
        self.connection = None
        self.cursor = None
        self.rowcount = 0
        self.use_row_factory = use_row_factory
        self.connection_string = str(connection_string)
        self.try_connect()
        return

    def __del__(self):
        self.try_close()

    def __enter__(self):
        if self.connected:
            return self
        return

    def __exit__(self, *args):
        return self.try_close()

    def try_connect(self):
        if self.try_close():
            return self.connect()
        return False

    def try_close(self):
        if self.connected:
            return self.close()
        return True

    @staticmethod
    def default_row_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]

        return d

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.connection_string)
            if self.use_row_factory[0]:
                factory = self.use_row_factory[1]
                self.connection.row_factory = factory if factory is not None else self.default_row_factory
            self.cursor = self.connection.cursor()
            self.connected = self.cursor is not None
            self.error = None if self.connected else 'database connect failed'
            return self.connected
        except BaseException as e:
            self.error = e.message
            return False

        return

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.commit()
                self.connection.close()
            self.error = None
        except BaseException as e:
            self.error = e.message
        finally:
            self.cursor = None
            self.connection = None
            self.connected = False
            return True

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def description(self):
        return self.cursor.description()

    def row_count(self):
        if self.connected:
            return self.rowcount
        return -1

    def execute(self, sql_list, data_list=None):
        try:
            if not self.connected:
                raise BaseException('connection not opened')
            if data_list is None:
                self.rowcount = reduce(sum, [ self.cursor.execute(sql).rowcount for sql in sql_list
                                            ])
            else:
                itr = iter(data_list)
                self.rowcount = reduce(sum, [ self.cursor.executemany(sql, itr.next()).rowcount for sql in sql_list
                                            ])
            return True
        except BaseException as e:
            self.error = e.message
            print self.error
            return False

        return

    def execute_and_commit(self, sql_list, data_list=None):
        try:
            if not self.execute(sql_list, data_list):
                return False
            self.connection.commit()
            return True
        except BaseException as e:
            self.error = e.message
            print self.error
            return False

    def script(self, script_list):
        try:
            if not self.connected:
                raise BaseException('connection not opened')
            for script in script_list:
                self.cursor.executescript(script)

            self.connection.commit()
            return True
        except BaseException as e:
            self.error = e.message
            print self.error
            return False

    def query(self, sql, fetch_count=0):
        try:
            if not self.connected:
                raise BaseException('connection not opened')
            self.cursor.execute(sql)
            if fetch_count < 1:
                return self.cursor.fetchall()
            rows = []
            for i in range(fetch_count):
                x = self.cursor.fetchone()
                if x:
                    rows.append(x)

            return rows
        except BaseException as e:
            self.error = e.message
            return

        return