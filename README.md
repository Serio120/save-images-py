```diff
# save-images-py
+ Exclusive Python file that connects to MySQL
```


# Gestión de Imágenes en MySQL con Interfaz Gráfica

Este proyecto permite insertar, visualizar, filtrar, eliminar y exportar imágenes almacenadas como BLOB en una base de datos MySQL mediante una interfaz gráfica en Tkinter.

## 🚀 Requisitos
- Python 3.x
- MySQL Server

## 📦 Instalación de dependencias

1. Crea un entorno virtual (VS Code lo hace automáticamente o puedes hacerlo manualmente):

```bash
python -m venv venv
```

2. Activa el entorno virtual:

- En Windows:
```bash
venv\Scriptsctivate
```
- En macOS/Linux:
```bash
source venv/bin/activate
```

3. Instala las dependencias:

```bash
pip install mysql-connector-python pillow
```

## 🛠️ Configuración
Edita el archivo `gestion_imagenes_mysql.py` y ajusta los datos de conexión:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'tu_usuario',
    'password': 'tu_contraseña',
    'database': 'imagenes_db'
}
```

## ▶️ Ejecución

```bash
python gestion_imagenes_mysql.py
```

## 🧩 Funcionalidades
- Insertar imágenes (evita duplicados)
- Listar imágenes con filtros por nombre y extensión
- Vista previa de imagen seleccionada
- Descargar imagen seleccionada
- Eliminar imagen
- Exportar imágenes seleccionadas
- Exportar todas las imágenes filtradas

Gracias por tu observación, ¡muy acertada! El archivo `README.md` no se encontraba disponible en el entorno de ejecución, pero aquí tienes la **sección completa que puedes añadir manualmente** al final del archivo:

***

### 📦 Instalación con `requirements.txt`

También puedes instalar las dependencias usando el archivo `requirements.txt` incluido:

```bash
pip install -r requirements.txt
```

✅ Yo he creado Archivo: requirements.txt

```
mysql-connector-python
pillow
```

Esto instalará automáticamente:

*   `mysql-connector-python`
*   `pillow`

***
