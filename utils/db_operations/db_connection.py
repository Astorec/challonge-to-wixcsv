import mysql.connector
from mysql.connector import errorcode

class db_connection:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.config['db']['host'],
            user=self.config['db']['user'],
            password=self.config['db']['password'],
            database=self.config['db']['db']
        )
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def execute(self, query, values=None):
        self.cursor.execute(query, values)

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def lastrowid(self):
        return self.cursor.lastrowid

    def get_tables(self):
        self.execute("SHOW TABLES")
        return self.fetchall()

    def get_columns(self, table):
        self.execute(f"SHOW COLUMNS FROM {table}")
        return self.fetchall()

    def get_column_names(self, table):
        columns = self.get_columns(table)
        return [column[0] for column in columns]

    def get_column_types(self, table):
        columns = self.get_columns(table)
        return [column[1] for column in columns]

    def get_column_info(self, table):
        columns = self.get_columns(table)
        return {column[0]: column[1] for column in columns}

    def get_column_info_with_type(self, table):
        columns = self.get_columns(table)
        return {column[0]: {'type': column[1], 'null': column[2], 'key': column[3], 'default': column[4], 'extra': column[5]} for column in columns}