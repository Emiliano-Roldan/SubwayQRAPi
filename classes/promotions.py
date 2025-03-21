from flask import jsonify
import logging
import json

logger = logging.getLogger(__name__)

class promotions:
    def __init__(self):
        from classes.load_configuration import configuration
        self.conf = configuration() 
        self.conf = self.conf.cargar_configuracion()
        import classes.connectionSQL as cs
        self.cs = cs
        self.conn = self.cs.SQLServerConnection(self.conf.server, self.conf.database, self.conf.username, self.conf.password, self.conf.port)

    def getpromotionstypes(self):
        try:
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            QueryExecutor = self.cs.SQLServerQueryExecutor(pyodbc_connection)
            result = QueryExecutor.execute_query("SELECT * FROM promotions_type")
            self.conn.disconnect()
            columns = ["id", "description"]
            result = [dict(zip(columns, row)) for row in result]
            return result
        except Exception as e:
            logger.error(f"Getpromotionstypes - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500
        
    def insertpromotionstype(self, description):
        try:
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            DataManipulator = self.cs.SQLServerDataManipulator(pyodbc_connection)
            DataManipulator.insert(f"INSERT INTO promotions_type VALUES ('{description}')")
            self.conn.disconnect()
            return True
        except Exception as e:
            logger.error(f"Insertpromotionstype - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500

    def insertpromotions(self, description, type, qrtype, expiration_date, amount_qr, status):
        try:
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            DataManipulator = self.cs.SQLServerDataManipulator(pyodbc_connection)
            DataManipulator.insert(f"INSERT INTO promotions VALUES ('{description}', {amount_qr}, 0, 0, 0, GETDATE(), '{expiration_date}', {type}, {qrtype}, {status})")
            self.conn.disconnect()
            return True
        except Exception as e:
            logger.error(f"Insertpromotions - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500
    
    def getpromotions(self, id=None):
        try:
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            QueryExecutor = self.cs.SQLServerQueryExecutor(pyodbc_connection)
            if id:
                result = QueryExecutor.execute_query(f"SELECT * FROM promotions WHERE id = {id}")
            else:
                result = QueryExecutor.execute_query("SELECT * FROM promotions")
            self.conn.disconnect()
            columns = ["id", "description", "amount_qr", "qr_amount_assigned", "qr_amount_generated", "burned_qr", "creation_date", "expiration_date", "type", "qrtype", "satus"]
            result = [
                {
                    **dict(zip(columns, row)),  # Crear el diccionario con todas las columnas
                    "creation_date": row[columns.index("creation_date")].strftime("%d-%m-%Y %H:%M:%S"),  # Formatear creation_date
                    "expiration_date": row[columns.index("expiration_date")].strftime("%d-%m-%Y %H:%M:%S")  # Formatear creation_date
                }
                for row in result
            ]
            return result
        except Exception as e:
            logger.error(f"Getpromotions - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500
        
    def updatepromotions(self, id, expiration_date, status, qr_amount_assigned=None):
        try:
            strupdate = "SET "
            if(expiration_date):  strupdate += f"expiration_date = '{expiration_date}',"
            if(qr_amount_assigned): strupdate += f"qr_amount_assigned = qr_amount_assigned + {qr_amount_assigned},"
            if(status is not None):
                strupdate += f"status = {status}"
            else: 
                strupdate = strupdate[:-1]
            
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            DataManipulator = self.cs.SQLServerDataManipulator(pyodbc_connection)
            DataManipulator.update(f"UPDATE promotions {strupdate} WHERE id = {id}")
            self.conn.disconnect()
            return True
        except Exception as e:
            logger.error(f"updatepromotions - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500
        
    def insertpromotionemployee(self, id_promotion, id_employee, amount):
        try:
            amount_promotion = self.getpromotions(id_promotion)[0]["amount_qr"]
            qr_amount_assigned = self.getpromotions(id_promotion)[0]["qr_amount_assigned"]
            qr_amount_generated = self.getpromotions(id_promotion)[0]["qr_amount_generated"]
            qrtype = self.getpromotions(id_promotion)[0]["qrtype"]
            
            if((qrtype == 2 and amount <= (amount_promotion-qr_amount_assigned)) or (qrtype == 1 and qr_amount_assigned != 1)):
                self.conn.connect()
                pyodbc_connection = self.conn.connection
                DataManipulator = self.cs.SQLServerDataManipulator(pyodbc_connection)
                DataManipulator.insert(f"INSERT INTO employee_promotion VALUES ({id_employee}, {id_promotion}, {amount})")
                self.conn.disconnect()
                self.updatepromotions(id_promotion, None, None, amount)
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Insertpromotionemployee - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500
    
    def getpromotionemployee(self, id_promotion):
        try:
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            QueryExecutor = self.cs.SQLServerQueryExecutor(pyodbc_connection)
            result = QueryExecutor.execute_query(f"SELECT id_employee, amount FROM employee_promotion WHERE id_promotion = {id_promotion}")
            columns = ["id_employee", "amount"]
            result = [dict(zip(columns, row)) for row in result]
            return result
        except Exception as e:
            logger.error(f"Getpromotionemployee - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500