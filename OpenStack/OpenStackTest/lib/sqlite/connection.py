__author__ = 'Henry'

from wrapper import session_wrapper
from sessoin import SqliteSession

singleton_connection_instance = None

class connection:
    def __init__(self, connection_string):
        global singleton_connection_instance
        singleton_connection_instance = self
        self.connection_string = connection_string
        self.connect_1 = None
        self.connect_2 = None

    def prepare(self):
        self.connect_1 = session_wrapper(SqliteSession, self.connection_string)
        self.connect_2 = session_wrapper(SqliteSession, self.connection_string, (True, None))

    @staticmethod
    def connect_db():
        global singleton_connection_instance
        return singleton_connection_instance.connect_1()

    @staticmethod
    def connect_db_row():
        global singleton_connection_instance
        return singleton_connection_instance.connect_2()