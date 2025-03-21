from flask import jsonify
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class products:
    def __init__(self):
        from classes.load_configuration import configuration
        self.conf = configuration() 
        self.conf = self.conf.cargar_configuracion()
        import classes.connectionSQL as cs
        self.cs = cs
        self.conn = self.cs.SQLServerConnection(self.conf.server, self.conf.database, self.conf.username, self.conf.password, self.conf.port)

    def insertproducts(self, id_promotion, id_product, description_prod, amount_prod, price_prod):
        try:
            from classes.promotions import promotions
            promotions = promotions()
            promotions = promotions.getpromotions()

            if(any(item['id'] == id_promotion for item in promotions)):
                self.conn.connect()
                pyodbc_connection = self.conn.connection
                DataManipulator = self.cs.SQLServerDataManipulator(pyodbc_connection)
                #logger.info(f"INSERT INTO product_promotions VALUES ({id_promotion}, '{id_product}', '{description_prod}', {amount_prod}, {price_prod}, GETDATE(), 1)")
                DataManipulator.insert(f"INSERT INTO product_promotions VALUES ({id_promotion}, '{id_product}', '{description_prod}', {amount_prod}, {price_prod}, GETDATE(), 1)")
                self.conn.disconnect()
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"InsertQr - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500
    
    def getproducts(self, textQR):
        try:
            logger.info(f"Llego {textQR}")
            self.conn.connect()
            pyodbc_connection = self.conn.connection
            QueryExecutor = self.cs.SQLServerQueryExecutor(pyodbc_connection)
            result = QueryExecutor.execute_query(f"SELECT * FROM product_promotions WHERE status = 1 AND id_promotion = (SELECT idpromocion FROM qr_data WHERE textQR = '{textQR}')")
            self.conn.disconnect()
            columns = ["id", "id_promotion", "id_product", "description_prod", "amount_prod", "price_prod", "creation_date" ,"satus"]
            result = [
                {
                    **dict(zip(columns, row)),  # Crear el diccionario con todas las columnas
                    "creation_date": row[columns.index("creation_date")].strftime("%d-%m-%Y %H:%M:%S")  # Formatear creation_date
                }
                for row in result
            ]
            
            return result
        except Exception as e:
            logger.error(f"Getproducts - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500