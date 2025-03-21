/* USUARIOS */
CREATE TABLE users(
    id INT IDENTITY(1,1),
    name VARCHAR(50),
    [user] VARCHAR(50),
    password VARCHAR(50),
    status BIT,
    lastlogin DATETIME,
    PRIMARY KEY (id)
)

/* EMPLEADO */
CREATE TABLE employees(
    id INT IDENTITY(1,1),
    name VARCHAR(50),
    identification_num VARCHAR(8) NULL,
    status BIT,
    PRIMARY KEY (id)
)

/* PROMOTIONS TYPE*/
CREATE TABLE promotions_type(
    id INT IDENTITY(1, 1),
    description VARCHAR(50),
    PRIMARY KEY (id)
)

/* PROMOCIONES */
CREATE TABLE promotions(
    id INT IDENTITY(1, 1),
    description VARCHAR(50),
    amount_qr INT, 
    qr_amount_assigned INT,
    qr_amount_generated INT,
    burned_qr INT DEFAULT 0,
    creation_date DATETIME,
    expiration_date DATETIME,
    type INT,
    qrtype INT, -- "1" Qr unico "2" Qr diferentes
    status BIT,
    PRIMARY KEY (id),
    FOREIGN KEY (type) REFERENCES promotions_type(id)
)

/* EMPLEADO_PROMOCION */
CREATE TABLE employee_promotion(
    id_employee INT,
    id_promotion INT,
    amount INT,
    PRIMARY KEY (id_employee, id_promotion),
    FOREIGN KEY (id_employee) REFERENCES employees(id),
    FOREIGN KEY (id_promotion) REFERENCES promotions(id)
)

/* PRODUCTOS DE LAS PROMOCIONES */
CREATE TABLE product_promotions(
    id INT IDENTITY(1, 1),
    id_promotion INT,
    id_product VARCHAR(10),
    description_prod VARCHAR(50),
    amount_prod INT, 
    price_prod FLOAT,
    creation_date DATETIME,
    status BIT,
    PRIMARY KEY (id),
    FOREIGN KEY (id_promotion) REFERENCES promotions(id),
)

/* QR DATA */
CREATE TABLE qr_data(
    textQR VARCHAR(8),
    type INT, -- "1" Qr unico "2" Qr diferentes
    amount_burn INT,
    creation_date DATETIME,
    idpromocion INT,
    id_employee INT NULL,
    status BIT,
    PRIMARY KEY (textQR),
    FOREIGN KEY (idpromocion) REFERENCES promotions(id),
    FOREIGN KEY (id_employee) REFERENCES employees(id)
)

/* QR LOG */
CREATE TABLE qr_log(
    id INT IDENTITY(1, 1),
    date DATETIME,
    store VARCHAR(50),
    cash_desk VARCHAR(50),
    textQR VARCHAR(8),
    PRIMARY KEY (id),
    FOREIGN KEY (textQR) REFERENCES qr_data(textQR)
)
