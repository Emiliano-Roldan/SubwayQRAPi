import pyodbc
import logging

logger = logging.getLogger(__name__)

class SQLServerConnection:
    def __init__(self, server, database, username, password, port):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = pyodbc.connect(
                'DRIVER={ODBC Driver 11 for SQL Server};'
                f'SERVER={self.server},{self.port};' 
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password}'
            )
        except pyodbc.Error as e:
            logger.error(f"(SQLServerConnection - connect) - Error connecting to SQL Server: {str(e)}")

    def disconnect(self):
        if self.connection:
            self.connection.close()

class SQLServerQueryExecutor:
    def __init__(self, connection):
        self.connection = connection
    
    def execute_query(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except pyodbc.Error as e:
            logger.error(f"(SQLServerQueryExecutor - execute_query) - Error executing query: {str(e)}")

class SQLServerDataManipulator:
    def __init__(self, connection):
        self.connection = connection
    
    def execute_non_query(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
        except pyodbc.Error as e:
            logger.error(f"(SQLServerDataManipulator - execute_non_query) - Error executing non-query: {str(e)}")

    def insert(self, query):
        self.execute_non_query(query)

    def update(self, query):
        self.execute_non_query(query)

    def delete(self, query):
        self.execute_non_query(query)