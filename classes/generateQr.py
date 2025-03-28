import qrcode
from PIL import Image, ImageDraw, ImageFont
from flask import jsonify
import logging
import io

logger = logging.getLogger(__name__)

class qr:
    def __init__(self):
        from classes.load_configuration import configuration
        self.conf = configuration() 
        self.conf = self.conf.cargar_configuracion()
        import classes.connectionSQL as cs
        self.cs = cs
        self.conn = self.cs.SQLServerConnection(self.conf.server, self.conf.database, self.conf.username, self.conf.password, self.conf.port)
        from classes.promotions import promotions
        self.promotions = promotions()
        from classes.employees import employees
        self.employees = employees()

    def generateQr(self, producto, codigo, vencimiento, beneficiario):
        try:
            # Generar QR
            qr = qrcode.QRCode(version=1, box_size=9, border=0)
            qr.add_data(codigo)  # Usar el código proporcionado
            qr.make(fit=True)
            img_qr = qr.make_image(fill='black', back_color='white')

            # Cargar plantilla
            plantilla = Image.open("C:\\Users\\Emilian\\Documents\\Proyecto Python\\ApiSubwayQr\\resources\\plantilla_qr_subway.JPG")
            draw = ImageDraw.Draw(plantilla)

            # Fuente (ajusta el tamaño y tipo de fuente según necesites)
            try:
                font = ImageFont.truetype("ariblk.ttf", 12)
            except IOError:
                font = ImageFont.load_default()

            # Posiciones y textos (ajusta estas coordenadas según la plantilla)
            draw.text((225, 250), producto, font=font, fill="black")
            draw.text((225, 272), codigo, font=font, fill="black")
            draw.text((245, 292), vencimiento, font=font, fill="black")
            draw.text((245, 312), beneficiario, font=font, fill="black")

            # Pegar QR en la plantilla (ajusta la posición del QR)
            posicion_qr = (157, 35)  # Ajusta según la plantilla
            plantilla.paste(img_qr, posicion_qr)

            # Guardar la imagen en un buffer en lugar de en el disco
            img_buffer = io.BytesIO()
            plantilla.save(img_buffer, format="JPEG")
            img_buffer.seek(0)  # Rebobinar el buffer al inicio

            return img_buffer

        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    
    def insertQr(self, type, idpromocion, id_employee, vencimiento, reimprimir, posicion=None):
        try:
            import random
            from classes.products import products
            products = products()
              
            products = products.getproducts(id_promotion=idpromocion)
            logger.info(f"{products}")
            beneficiario = self.employees.getemployees(id=id_employee)[0]["name"]            

            logger.info(f"{len(products)}")
            if(len(products) > 0): # Tambien me falta validar si la promocion no esta vencida y que su status sea 1
                logger.info(products)
                producto = products[0]["description_prod"]
                if not reimprimir:
                    textQR = list("A47B3F7NG34DFS345ASBLJKD4560985NF")
                    random.shuffle(textQR)
                    textQR = ''.join(textQR)[11:19]
                    self.conn.connect()
                    pyodbc_connection = self.conn.connection
                    DataManipulator = self.cs.SQLServerDataManipulator(pyodbc_connection)
                    DataManipulator.insert(f"INSERT INTO qr_data VALUES ('{textQR}', {type}, 0, GETDATE(), {idpromocion}, {id_employee}, 1)")
                    DataManipulator.update(f"UPDATE promotions SET qr_amount_generated = qr_amount_generated + 1 WHERE id = {idpromocion}")
                    self.conn.disconnect()
                else:
                    if type == 1:
                        textQR = self.getQR(idpromocion = idpromocion, id_employee = id_employee)[0]["textQR"]
                    else:
                        textQR = self.getQR(idpromocion = idpromocion, id_employee = id_employee)[posicion]["textQR"]

                buffer = self.generateQr(producto, textQR, vencimiento[:-9], beneficiario)
                return [buffer, beneficiario, textQR]
            else:
                return [False, False, False]
        except Exception as e:
            logger.error(f"InsertQr - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500

    def getQR(self, idpromocion = None, id_employee = None, textQr = None):
        try:
            if idpromocion:
                promotions = self.promotions.getpromotions(idpromocion)
                if len(promotions) == 1:
                    if not promotions[0]["status"]:
                        return jsonify(mensaje=f"La promocion {idpromocion} no se encuentra activa."), 404
                else:
                    return jsonify(mensaje=f"La promocion {idpromocion} no existe."), 404
                          
            if id_employee:
                employee = self.employees.getemployees(id=id_employee)
                if len(employee) == 1:
                    if not employee[0]["status"]:
                        return jsonify(mensaje=f"El empleado {id_employee} no se encuentra activo."),
                else:
                    return jsonify(mensaje=f"El empleado {id_employee} no existe."), 404

            self.conn.connect()
            pyodbc_connection = self.conn.connection
            QueryExecutor = self.cs.SQLServerQueryExecutor(pyodbc_connection)
            if id_employee:
                result = QueryExecutor.execute_query(f"SELECT textQR FROM qr_data WHERE idpromocion = {idpromocion} AND id_employee = {id_employee}")
                self.conn.disconnect()
                columns = ["textQR"]
                result = [{**dict(zip(columns, row))} for row in result]
                return result
            elif textQr != 'ALL':
                result = QueryExecutor.execute_query(f"SELECT idpromocion, status, amount_burn FROM qr_data WHERE textQr = '{textQr}'")
                self.conn.disconnect()
                columns = ["idpromocion", "status", "amount_burn"]
                result = [{**dict(zip(columns, row))} for row in result]
                if result:
                    return result[0], 200
                else:
                    return jsonify(error=f"El QR {textQr} no existe."), 404
            else:
                if idpromocion:
                    result = QueryExecutor.execute_query(f"SELECT * FROM qr_data WHERE idpromocion = {idpromocion}")
                else:
                    result = QueryExecutor.execute_query(f"SELECT * FROM qr_data")
                self.conn.disconnect()
                columns = ["textQR", "type", "amount_burn", "creation_date", "idpromocion", "id_employee", "status"]
                result = [
                    {
                        **dict(zip(columns, row)),  # Crear el diccionario con todas las columnas
                        "creation_date": row[columns.index("creation_date")].strftime("%d-%m-%Y %H:%M:%S"),  # Formatear creation_date
                    }
                    for row in result
                ]
                return result, 200
        except Exception as e:
            logger.error(f"GetQR - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500
        
    def insertQrlog(self, store, cash_desk, id_qr):
        try:
            id_promotion_result = self.getQR(textQr=id_qr)
            logger.info(id_promotion_result[0])
            
            if id_promotion_result:
                from datetime import datetime
                id_promotion = id_promotion_result[0]["idpromocion"]
                status_qr = id_promotion_result[0]["status"]
                burned_qr = id_promotion_result[0]["amount_burn"]

                from classes.promotions import promotions
                promotions = promotions()
                promotion = promotions.getpromotions(id_promotion)
                amount_qr = promotion[0]["amount_qr"]
                qr_type = promotion[0]["qrtype"]
                expiration_date = datetime.strptime(promotion[0]["expiration_date"], "%d-%m-%Y %H:%M:%S")
                current_date = datetime.now()
                burned_qr_promotion = promotion[0]["burned_qr"]
                
                self.conn.connect()
                pyodbc_connection = self.conn.connection
                DataManipulator = self.cs.SQLServerDataManipulator(pyodbc_connection)
                
                #logger.info(expiration_date)
                if (status_qr == True and current_date <= expiration_date):
                    if( (qr_type == 1 and burned_qr <= amount_qr) or (qr_type == 2 and burned_qr < 1) ): #1 unico, 2 diferentes
                        DataManipulator.insert(f"INSERT INTO qr_log VALUES (GETDATE(), '{store}', '{cash_desk}', '{id_qr}')")
                        DataManipulator.update(f"UPDATE qr_data SET amount_burn = amount_burn + 1 WHERE textQR = '{id_qr}'")
                        DataManipulator.update(f"UPDATE promotions SET burned_qr = burned_qr + 1 WHERE id = {id_promotion}")

                        # Query para bloquear la promocion.
                        if burned_qr_promotion == amount_qr-1:
                            DataManipulator.update(f"UPDATE promotions SET status = 0  WHERE id = {id_promotion}")
                            if qr_type == 1:
                                DataManipulator.update(f"UPDATE qr_data SET status = 0 WHERE textQR = '{id_qr}'")

                        # Query para bloquear el QR.
                        if qr_type == 2:
                            DataManipulator.update(f"UPDATE qr_data SET status = 0 WHERE textQR = '{id_qr}'")

                        self.conn.disconnect()
                        
                        return True
                else:
                    return "QR Vencido o bloqueado."
            else:
                return "No se encontró QR."            
        except Exception as e:
            logger.error(f"InsertQr - Error: {e}", exc_info=True)  # Log del error con traza
            return jsonify(error=f"Error interno: {e}"), 500        