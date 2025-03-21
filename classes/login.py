from flask import jsonify
import logging

logger = logging.getLogger(__name__)

class login:
    def __init__(self):
        from classes.load_configuration import configuration
        self.conf = configuration() 
        self.conf = self.conf.cargar_configuracion()

    def checkuser(self, user, password):
        try:
            import classes.connectionSQL as cs

            conn = cs.SQLServerConnection(self.conf.server, self.conf.database, self.conf.username, self.conf.password, self.conf.port)
            conn.connect()
            pyodbc_connection = conn.connection
            QueryExecutor = cs.SQLServerQueryExecutor(pyodbc_connection)
            result = QueryExecutor.execute_query(
                f"SELECT CASE WHEN COUNT(id) > 0 THEN 'true' ELSE 'false' END AS users,"
                f"CASE WHEN COUNT(id) > 0 THEN MAX(id) ELSE 'false' END AS ids "
                f"FROM [users] WHERE status = 1 AND [user] = '{user}' AND [password] = '{password}'"
            )

            id = result[0][1]
            result = result[0][0]
            
            if result == 'true':
                DataManipulator = cs.SQLServerDataManipulator(pyodbc_connection)
                #logger.info(f"UPDATE [users] SET lastlogin = GETDATE() WHERE id = {id}")
                DataManipulator.update(f"UPDATE [users] SET lastlogin = GETDATE() WHERE id = {id}")
            conn.disconnect()
            
            return result
        except Exception as e:
            logger.error(f"Checkuser - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500