from flask import Flask, jsonify, request, send_file
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token, get_jwt_identity
)
from datetime import timedelta
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import os
import zipfile
import io

# Ruta de la carpeta de logs
log_folder = Path(__file__).resolve().parent / "log"
os.makedirs(log_folder, exist_ok=True)

# Configuración del logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        TimedRotatingFileHandler(
            log_folder / "app.log",  # Nombre base del archivo
            when="midnight",  # Rotación diaria a medianoche
            #backupCount=7  # Mantener logs de los últimos 7 días
        ),
        logging.StreamHandler()  # Mostrar logs en la consola
    ]
)

logger = logging.getLogger(__name__)
app = Flask(__name__)

# Configuración de JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', os.urandom(24).hex())
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)  # 15 minutos
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)     # 7 días
jwt = JWTManager(app)

''' INICIO SECCION LOGIN '''
# Ruta de login
@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        from classes.login import login
        login = login()
        login = login.checkuser(username, password)

        if not login or login == 'false':
            return jsonify({"error": "Usurio o contraseña invalidos."}), 401
        
        # Crear tokens
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return jsonify(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        logging.error(f"Endpoint /login: {e}")
        return jsonify(error=f"Error interno: {e}"), 500

# Ruta para refrescar el token
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # Asegúrate de usar refresh=True
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token)

# Ruta protegida
@app.route('/test')
def test():
    return jsonify(mensaje="Hola, si podes leer esto es porque la API funciona!")

''' FINAL SECCION LOGIN '''

''' INICIO SECCION EMPLEADO '''

# Ruta para obtener los empleados.
@app.route('/employees', methods=['GET'])
def eployees():
    try:
        from classes.employees import employees
        employees = employees()
        employees = employees.getemployees()
        return employees, 200
    except Exception as e:
        logging.error(f"Endpoint /employees: {e}")
        return jsonify(error=str(e)), 500
    
# Insertar empleado.
@app.route('/addemployee', methods=['POST'])
def addemployee():
    try:
        name = request.json.get('name')
        identification_num = request.json.get('identification_num')
        status = request.json.get('status')

         # Validar que los datos estén presentes
        if not all([name, identification_num, status]):
            return jsonify(error="Faltan campos obligatorios"), 400
        
        from classes.employees import employees
        employees = employees()
        employees = employees.insertemployees(name, identification_num, status)
        return jsonify(mensaje=True), 200
    except Exception as e:
        logging.error(f"Endpoint /employees: {e}")
        return jsonify(error=str(e)), 500

# Editar empleado.
@app.route('/updateemployee', methods=['POST'])
def updateemployee():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.json
        id = data.get('id')
        name = data.get('name')
        identification_num = data.get('identification_num')
        status = data.get('status')

        # Validar que los datos estén presentes
        if not all([id, name, identification_num, status is not None]):
            return jsonify(error="Faltan campos obligatorios"), 400

        # Llamar a la lógica de negocio para actualizar el empleado
        from classes.employees import employees
        employee_manager = employees()
        employee_manager.updateemployees(id, name, identification_num, status)

        # Retornar una respuesta exitosa
        return jsonify(mensaje=True), 200
    except Exception as e:
        logging.error(f"Endpoint /employees: {e}")
        return jsonify(error=str(e)), 500

''' FINAL SECCION EMPLEADO '''

''' INICIO SECCION PROMOCIONES'''

# Ruta para obtener los tipos de promociones.
@app.route('/getpromotionstypes', methods=['GET']) ### TABLA EMPLEADO PROMOCIONES ####
def promotionstypes():
    try:
        from classes.promotions import promotions
        promotions = promotions()
        promotions = promotions.getpromotionstypes()
        return promotions, 200
    except Exception as e:
        logging.error(f"Endpoint /employees: {e}")
        return jsonify(error=str(e)), 500
    
# Insertar tipo promociones.
@app.route('/addpromotiontype', methods=['POST'])
def addpromotiontype():
    try:
        data = request.json
        description = data.get('description')

        # Validar que los datos estén presentes
        if not all([description]):
            return jsonify(error="Faltan campos obligatorios"), 400
        
        from classes.promotions import promotions
        promotions = promotions()
        promotions.insertpromotionstype(description)
        return jsonify(mensaje=True), 200
    except Exception as e:
        logging.error(f"Endpoint /employees: {e}")
        return jsonify(error=str(e)), 500

# Insertar promociones.
@app.route('/addpromotion', methods=['POST']) # tengo que hacer tabla empleados promociones porque una promocion puede tener varios empleados.
def addpromotion():
    try:
        data = request.json
        description = data.get('description')
        type = data.get('type')
        qrtype = data.get('qrtype')
        expiration_date = data.get('expiration_date')
        amount_qr = data.get('amount_qr')
        status = data.get('status')

        # Validar que los datos estén presentes
        if not all([description, type, qrtype, expiration_date, amount_qr, status is not None]):
            return jsonify(error="Faltan campos obligatorios"), 400
        
        from classes.promotions import promotions
        promotions = promotions()
        promotions.insertpromotions(description, type, qrtype, expiration_date, amount_qr, status)
        return jsonify(mensaje=True), 200
    except Exception as e:
        logging.error(f"Endpoint /addpromotion: {e}")
        return jsonify(error=str(e)), 500

# Ruta para obtener las promociones.
@app.route('/getpromotions', methods=['GET'])
def getpromotions():
    try:
        from classes.promotions import promotions
        promotions = promotions()
        promotions = promotions.getpromotions()
        return promotions, 200
    except Exception as e:
        logging.error(f"Endpoint /getpromotions: {e}")
        return jsonify(error=str(e)), 500

# Editar empleado.
@app.route('/updatepromotions', methods=['POST'])
def updatepromotions():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.json
        id = data.get('id')
        expiration_date = data.get('expiration_date')
        status = data.get('status')

        # Validar que los datos estén presentes
        # if not all([id, expiration_date, id_employee, status]):
        #     return jsonify(error="Faltan campos obligatorios"), 400

        # Llamar a la lógica de negocio para actualizar el empleado
        from classes.promotions import promotions
        promotions_manager = promotions()
        promotions_manager.updatepromotions(id, expiration_date, status)

        # Retornar una respuesta exitosa
        return jsonify(mensaje=True), 200
    except Exception as e:
        logging.error(f"Endpoint /employees: {e}")
        return jsonify(error=str(e)), 500

@app.route('/addpromotionemployee', methods=['POST']) # tengo que hacer tabla empleados promociones porque una promocion puede tener varios empleados.
def addpromotionemployee():
    try:
        data = request.json
        id_promotion = data.get('id_promotion')
        id_employee = data.get('id_employee')
        amount = data.get('amount')

        # Validar que los datos estén presentes
        if not all([id_promotion, id_employee, amount]):
            return jsonify(error="Faltan campos obligatorios"), 400
        
        from classes.promotions import promotions
        promotions = promotions()
        response = promotions.insertpromotionemployee(id_promotion, id_employee, amount)
        if response:
            return jsonify(mensaje=True), 200
        else:
            return jsonify(mensaje=f"No es posible asignar, la cantidad {amount} excede limite. Intente asignar menos."), 200
    except Exception as e:
        logging.error(f"Endpoint /addpromotion: {e}")
        return jsonify(error=str(e)), 500
    
''' FINAL SECCION PROMOCIONES'''

''' INICIO SECCION PRODUCTOS '''

# Generear productos de promocion
@app.route('/addproduct', methods=['POST']) # tengo que hacer tabla empleados promociones porque una promocion puede tener varios empleados.
def addproduct():
    try:
        data = request.json
        id_promotion = data.get('id_promotion')
        id_product = data.get('id_product')
        description_prod = data.get('description_prod')
        amount_prod = data.get('amount_prod')
        price_prod = data.get('price_prod')

        # Validar que los datos estén presentes
        if not all([id_promotion, id_product, description_prod, amount_prod, price_prod]):
            return jsonify(error="Faltan campos obligatorios"), 400
        
        from classes.products import products
        product = products()
        resp = product.insertproducts(id_promotion, id_product, description_prod, amount_prod, price_prod)
        if(resp):
            return jsonify(mensaje=True), 200
        else:
            return jsonify(mensaje=f"La promocion {id_promotion} no existe."), 200
    except Exception as e:
        logging.error(f"Endpoint /addpromotion: {e}")
        return jsonify(error=str(e)), 500

# Ruta para obtener los productos de las promociones.
@app.route('/getproducts/<string:textQR>', methods=['GET'])
def getproducts(textQR):
    try:
        from classes.products import products
        product = products()
        product = product.getproducts(textQR)
        return product[0], 200
    except Exception as e:
        logging.error(f"Endpoint /getproducts: {e}")
        return jsonify(error=str(e)), 500
    
''' INICIO SECCION QR '''

# Generar Qr para descargar
@app.route('/generate_qr', methods=['POST'])  # Cambiado a POST para recibir JSON
def generate_qr():
    # Obtener el JSON del cuerpo de la solicitud
    data = request.json

    if not data or not isinstance(data, dict):
        return jsonify(error="Se esperaba un diccionario JSON"), 400

    # Crear un archivo ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for beneficiario, productos in data.items():
            # Si el nombre del beneficiario está vacío, usar un nombre genérico
            folder_name = beneficiario if beneficiario.strip() else "Sin_Nombre"

            for index, producto_info in enumerate(productos):
                producto = producto_info.get('producto')
                codigo = producto_info.get('codigo')
                vencimiento = producto_info.get('vencimiento')

                if not all([producto, codigo, vencimiento]):
                    return jsonify(error=f"Faltan datos en el producto {index + 1} de {beneficiario}"), 400

                # Generar el QR
                from classes.generateQr import qr
                qr_generator = qr()
                img_buffer = qr_generator.generateQr(producto, codigo, vencimiento, beneficiario)

                if img_buffer:
                    # Agregar la imagen al ZIP dentro de la carpeta del beneficiario
                    zip_file.writestr(f'{folder_name}/qr_generated_{index + 1}.jpg', img_buffer.getvalue())
                else:
                    return jsonify(error=f"Error al generar el QR para el producto {index + 1} de {beneficiario}"), 500

    zip_buffer.seek(0)  # Rebobinar el buffer al inicio

    # Devolver el ZIP como respuesta para descargar
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='qr_images.zip'  # Nombre del archivo ZIP al descargar
    )

# Insertar Qr.
@app.route('/addqr', methods=['POST'])
def addqr():
    try:
        data = request.json
        #type = data.get('type')
        idpromocion = data.get('idpromocion')
        #id_employee = data.get('id_employee')

        # Validar que los datos estén presentes
        if not all([idpromocion]):
            return jsonify(error="Faltan campos obligatorios", json=data), 400
        
        from classes.generateQr import qr
        from classes.promotions import promotions
        promotions = promotions()
        promotionsget = promotions.getpromotions(idpromocion)[0]
        
        type = promotionsget["qrtype"]
        amount_qr = promotionsget["amount_qr"]
        qr_amount_generated = promotionsget["qr_amount_generated"]

        reimprimir = None
        if type == 1:
            if qr_amount_generated == 1:
                reimprimir = True
        elif type == 2:
            if not qr_amount_generated < amount_qr:
                reimprimir = True

        vencimiento = promotionsget["expiration_date"]
        employee_amount = promotions.getpromotionemployee(idpromocion)

        insertQr = qr()
        # # resp = insertQr.insertQr(textQR, type, idpromocion, id_employee)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i in employee_amount:
                for e in range(int(i["amount"])):
                    if type == 1:
                        [img_buffer, name_employee, textQR] = insertQr.insertQr(type, idpromocion, i["id_employee"], vencimiento, reimprimir)
                    else:
                        [img_buffer, name_employee, textQR] = insertQr.insertQr(type, idpromocion, i["id_employee"], vencimiento, reimprimir, e)

                    if img_buffer:
                        # Agregar la imagen al ZIP dentro de la carpeta del beneficiario
                        zip_file.writestr(f'{name_employee}/{textQR}.jpg', img_buffer.getvalue())
                    else:
                        return jsonify(error=f"Error al generar el QR para el {name_employee}"), 500
        zip_buffer.seek(0)  # Rebobinar el buffer al inicio

        # Devolver el ZIP como respuesta para descargar
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='qr_images.zip'  # Nombre del archivo ZIP al descargar
        )
    except Exception as e:
        logging.error(f"Endpoint /addqr: {e}")
        return jsonify(error=str(e)), 500

### MAS ENDPOINT QUE NO TENGAN QUE VER CON EL LOG ####

# Insertar log de QR, esto se utiliza cuando queman el QR.
@app.route('/logqr', methods=['POST'])
def logqr():
    try:
        data = request.json
        store = data.get('store')
        cash_desk = data.get('cash_desk')
        id_qr = data.get('id_qr')

        # Validar que los datos estén presentes
        if not all([store, cash_desk, id_qr]):
            return jsonify(error="Faltan campos obligatorios", json=data), 400
        
        from classes.generateQr import qr
        insertQr = qr()
        result = insertQr.insertQrlog(store, cash_desk, id_qr)

        if result == True:
            return jsonify(mensaje=True), 200
        else:
            return jsonify(mensaje=result), 200
    except Exception as e:
        logging.error(f"Endpoint /addqr: {e}")
        return jsonify(error=str(e)), 500

# Obtener los QR generados de X promocion.
@app.route('/getQr/<string:textQR>', methods=['GET'])
@app.route('/getQr/<string:textQR>/<int:id_promotion>', methods=['GET']) 
def getQr(textQR, id_promotion=None):
    try:
        from classes.generateQr import qr
        getQr = qr()
        getQr = getQr.getQR(idpromocion=id_promotion, textQr=textQR)
        return getQr, 200
    except Exception as e:
        logging.error(f"Endpoint /getQr: {e}")
        return jsonify(error=str(e)), 500
   

''' FINAL SECCION QR '''

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)