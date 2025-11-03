import mysql.connector
# Datos de conexión a MySQL
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'imagenes_db'
}

# Conectar a la base de datos
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS imagenes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255),
        imagen LONGBLOB
    )
''')

# Función para convertir imagen a binario
def convertir_a_binario(ruta_imagen):
    with open(ruta_imagen, 'rb') as archivo:
        return archivo.read()

# Función para insertar imagen en la base de datos
def insertar_imagen(nombre, ruta_imagen):
    imagen_binaria = convertir_a_binario(ruta_imagen)
    sql = "INSERT INTO imagenes (nombre, imagen) VALUES (%s, %s)"
    cursor.execute(sql, (nombre, imagen_binaria))
    conn.commit()
    print(f"Imagen '{nombre}' insertada correctamente.")

# Ejemplo de uso
insertar_imagen("Carlo_Acutis", "Carlo_Acutis_.jpg")

# Cerrar conexión
cursor.close()
conn.close()