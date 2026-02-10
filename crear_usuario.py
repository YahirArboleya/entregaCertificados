import mysql.connector
from werkzeug.security import generate_password_hash

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="control_certificados"
)

cursor = conexion.cursor()

usuario = "YahirArboleya"
password_plano = "adios987"

password_hash = generate_password_hash(password_plano)

cursor.execute(
    "INSERT INTO usuarios (usuario, password) VALUES (%s, %s)",
    (usuario, password_hash)
)

conexion.commit()

print("Usuario creado correctamente")

cursor.close()
conexion.close()
