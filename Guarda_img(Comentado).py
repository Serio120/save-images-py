import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, Entry, Label
import mysql.connector
from PIL import Image, ImageTk
import io
import os

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN (Reutilizable para cualquier DB MySQL)
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'imagenes_db'
}

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Creación de tabla: Útil para entender tipos de datos LONGBLOB (archivos pesados)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS imagenes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE,
        imagen LONGBLOB
    )
""")
conn.commit()

# ==========================================
# 2. LÓGICA DE CONVERSIÓN (Muy reutilizable)
# ==========================================

# Esta función sirve para cualquier archivo (PDF, Imágenes, Música) que quieras subir a una DB
def convertir_a_binario(ruta):
    with open(ruta, 'rb') as f:
        return f.read()

# ==========================================
# 3. OPERACIONES CRUD (Interacción con la DB)
# ==========================================

def insertar_imagenes():
    """Selecciona archivos locales y los guarda en la base de datos."""
    rutas = filedialog.askopenfilenames(title="Selecciona imágenes", filetypes=[("Imágenes", "*.jpg *.png *.jpeg")])
    if not rutas:
        return
    insertadas = 0
    duplicadas = []
    for ruta in rutas:
        nombre = os.path.basename(ruta)
        # Verificación de duplicados antes de insertar
        cursor.execute("SELECT COUNT(*) FROM imagenes WHERE nombre=%s", (nombre,))
        if cursor.fetchone()[0] > 0:
            duplicadas.append(nombre)
            continue
        
        imagen_binaria = convertir_a_binario(ruta)
        cursor.execute("INSERT INTO imagenes (nombre, imagen) VALUES (%s, %s)", (nombre, imagen_binaria))
        insertadas += 1
    
    conn.commit()
    # Feedback al usuario
    mensaje = f"Se insertaron {insertadas} imágenes."
    if duplicadas:
        mensaje += f" Duplicadas no insertadas: {', '.join(duplicadas)}"
    messagebox.showinfo("Resultado", mensaje)
    listar_imagenes()

def listar_imagenes(filtro_nombre='', filtro_extension=''):
    """Consulta con filtros dinámicos. Reutilizable para buscadores."""
    lista.delete(0, tk.END)
    query = "SELECT nombre FROM imagenes"
    condiciones = []
    valores = []
    
    # Construcción dinámica de la consulta SQL
    if filtro_nombre:
        condiciones.append("nombre LIKE %s")
        valores.append(f"%{filtro_nombre}%")
    
    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)
    
    query += " ORDER BY id DESC"
    cursor.execute(query, valores)
    resultados = cursor.fetchall()
    
    for (nombre,) in resultados:
        # Filtrado lógico adicional por extensión
        if filtro_extension and not nombre.lower().endswith(filtro_extension):
            continue
        lista.insert(tk.END, nombre)
    
    contador_label.config(text=f"Total imágenes: {len(lista.get(0, tk.END))}")

def ver_imagen():
    """Recupera el binario de la DB y lo convierte en objeto visible para Tkinter."""
    seleccion = lista.curselection()
    if not seleccion:
        messagebox.showwarning("Aviso", "Selecciona una imagen.")
        return
    
    nombre = lista.get(seleccion[0])
    cursor.execute("SELECT imagen FROM imagenes WHERE nombre=%s", (nombre,))
    resultado = cursor.fetchone()
    
    if resultado:
        imagen_binaria = resultado[0]
        # io.BytesIO convierte los bytes en un 'archivo virtual' que PIL puede leer
        img = Image.open(io.BytesIO(imagen_binaria))
        img.thumbnail((600, 600)) # Redimensionado rápido para visualización
        img_tk = ImageTk.PhotoImage(img)
        panel.config(image=img_tk)
        panel.image = img_tk # Referencia necesaria para que Python no borre la imagen de memoria

def descargar_imagen():
    """Extrae el binario y lo reconstruye como un archivo físico en el disco."""
    seleccion = lista.curselection()
    if not seleccion:
        messagebox.showwarning("Aviso", "Selecciona una imagen.")
        return
    
    nombre = lista.get(seleccion[0])
    cursor.execute("SELECT imagen FROM imagenes WHERE nombre=%s", (nombre,))
    resultado = cursor.fetchone()
    
    if resultado:
        imagen_binaria = resultado[0]
        ruta_guardar = filedialog.asksaveasfilename(defaultextension=".jpg", initialfile=nombre)
        if ruta_guardar:
            # Escribir en modo 'wb' (write binary) para reconstruir el archivo
            with open(ruta_guardar, 'wb') as f:
                f.write(imagen_binaria)
            messagebox.showinfo("Éxito", f"Imagen guardada en {ruta_guardar}")

def eliminar_imagen():
    """Borrado de registros por nombre."""
    seleccion = lista.curselection()
    if not seleccion:
        messagebox.showwarning("Aviso", "Selecciona una imagen.")
        return
    
    nombre = lista.get(seleccion[0])
    if messagebox.askyesno("Confirmar", f"¿Eliminar la imagen '{nombre}'?"):
        cursor.execute("DELETE FROM imagenes WHERE nombre=%s", (nombre,))
        conn.commit()
        messagebox.showinfo("Éxito", f"Imagen '{nombre}' eliminada.")
        listar_imagenes()
        panel.config(image='')
        panel.image = None

# ==========================================
# 4. INTERFAZ GRÁFICA (Estructura Tkinter)
# ==========================================
ventana = tk.Tk()
ventana.title("Gestión Avanzada de Imágenes en MySQL")
ventana.geometry("800x800")

# Botones de acción
btn_insertar = tk.Button(ventana, text="Insertar Imágenes", command=insertar_imagenes)
btn_insertar.pack(pady=5)

# ... (Resto de botones configurados de forma similar) ...

# Sección de Filtros (Grid dentro de un Frame para orden)
frame_filtros = tk.Frame(ventana)
frame_filtros.pack(pady=10)
Label(frame_filtros, text="Buscar por nombre:").grid(row=0, column=0)
entrada_busqueda = Entry(frame_filtros)
entrada_busqueda.grid(row=0, column=1)

# Lista con Scrollbar (Patrón de diseño muy común en apps de escritorio)
frame_lista = tk.Frame(ventana)
frame_lista.pack(pady=10)
scrollbar = Scrollbar(frame_lista)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
lista = Listbox(frame_lista, width=50, height=15, yscrollcommand=scrollbar.set, selectmode=tk.MULTIPLE)
lista.pack(side=tk.LEFT)
scrollbar.config(command=lista.yview)

# Área de previsualización
panel = tk.Label(ventana)
panel.pack(pady=10)

listar_imagenes() # Carga inicial de datos
ventana.mainloop()

# Cierre preventivo de conexiones
cursor.close()
conn.close()