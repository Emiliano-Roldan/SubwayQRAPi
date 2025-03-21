from flask import jsonify
import logging
import json

logger = logging.getLogger(__name__)

class employees:
    def __init__(self):
        from classes.load_configuration import configuration
        self.conf = configuration() 
        self.conf = self.conf.cargar_configuracion()
        import classes.connectionSQL as cs
        self.cs = cs
        self.conn = self.cs.SQLServerConnection(self.conf.server, self.conf.database, self.conf.username, self.conf.password, self.conf.port)

    def getemployees(self, id=None):
        try:
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            QueryExecutor = self.cs.SQLServerQueryExecutor(pyodbc_connection)
            if id:
                result = QueryExecutor.execute_query(f"SELECT * FROM employees WHERE status = 1 AND id = {id}")
            else:
                result = QueryExecutor.execute_query("SELECT * FROM employees WHERE status = 1")
            self.conn.disconnect()
            columns = ["id", "name", "identification_num", "status"]
            result = [dict(zip(columns, row)) for row in result]
            return result
        except Exception as e:
            logger.error(f"Getemployees - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500
    
    def insertemployees(self, employeesname, identification_num, status):
        try:
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            DataManipulator = self.cs.SQLServerDataManipulator(pyodbc_connection)
            DataManipulator.insert(f"INSERT INTO employees VALUES ('{employeesname}', '{identification_num}', {status})")
            self.conn.disconnect()
            return True
        except Exception as e:
            logger.error(f"Insertemployees - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500
        
    def updateemployees(self, id, employeesname, identification_num, status):
        try:
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            DataManipulator = self.cs.SQLServerDataManipulator(pyodbc_connection)
            DataManipulator.update(f"UPDATE employees SET name = '{employeesname}', identification_num = '{identification_num}', status = {status} WHERE id = {id}")
            self.conn.disconnect()
            return True
        except Exception as e:
            logger.error(f"Insertemployees - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500