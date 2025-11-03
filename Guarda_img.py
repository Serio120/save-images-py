import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar
import mysql.connector
from PIL import Image, ImageTk
import io
import os

# Configuración de conexión MySQL (ajusta según tu entorno)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'imagenes_db'
}

# Conexión global
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Crear tabla si no existe (con restricción UNIQUE para evitar duplicados)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS imagenes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE,
        imagen LONGBLOB
    )
''')
conn.commit()

# Función para convertir imagen a binario
def convertir_a_binario(ruta):
    with open(ruta, 'rb') as f:
        return f.read()

# Insertar imágenes evitando duplicados
def insertar_imagenes():
    rutas = filedialog.askopenfilenames(title="Selecciona imágenes", filetypes=[("Imágenes", "*.jpg *.png *.jpeg")])
    if not rutas:
        return
    insertadas = 0
    duplicadas = []
    for ruta in rutas:
        nombre = os.path.basename(ruta)
        cursor.execute("SELECT COUNT(*) FROM imagenes WHERE nombre=%s", (nombre,))
        if cursor.fetchone()[0] > 0:
            duplicadas.append(nombre)
            continue
        imagen_binaria = convertir_a_binario(ruta)
        cursor.execute("INSERT INTO imagenes (nombre, imagen) VALUES (%s, %s)", (nombre, imagen_binaria))
        insertadas += 1
    conn.commit()
    mensaje = f"Se insertaron {insertadas} imágenes."
    if duplicadas:
        mensaje += f"\nDuplicadas no insertadas: {', '.join(duplicadas)}"
    messagebox.showinfo("Resultado", mensaje)
    listar_imagenes()

# Listar imágenes en la base de datos
def listar_imagenes():
    lista.delete(0, tk.END)
    cursor.execute("SELECT nombre FROM imagenes ORDER BY id DESC")
    for (nombre,) in cursor.fetchall():
        lista.insert(tk.END, nombre)

# Ver imagen seleccionada con vista previa más grande
def ver_imagen():
    seleccion = lista.curselection()
    if not seleccion:
        messagebox.showwarning("Aviso", "Selecciona una imagen.")
        return
    nombre = lista.get(seleccion[0])
    cursor.execute("SELECT imagen FROM imagenes WHERE nombre=%s", (nombre,))
    resultado = cursor.fetchone()
    if resultado:
        imagen_binaria = resultado[0]
        img = Image.open(io.BytesIO(imagen_binaria))
        img.thumbnail((600, 600))  # Vista previa más grande
        img_tk = ImageTk.PhotoImage(img)
        panel.config(image=img_tk)
        panel.image = img_tk

# Descargar imagen seleccionada
def descargar_imagen():
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
            with open(ruta_guardar, 'wb') as f:
                f.write(imagen_binaria)
            messagebox.showinfo("Éxito", f"Imagen guardada en {ruta_guardar}")

# Eliminar imagen seleccionada
def eliminar_imagen():
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

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Imágenes en MySQL")
ventana.geometry("700x600")

# Botones
btn_insertar = tk.Button(ventana, text="Insertar Imágenes", command=insertar_imagenes)
btn_insertar.pack(pady=5)

btn_ver = tk.Button(ventana, text="Ver Imagen", command=ver_imagen)
btn_ver.pack(pady=5)

btn_descargar = tk.Button(ventana, text="Descargar Imagen", command=descargar_imagen)
btn_descargar.pack(pady=5)

btn_eliminar = tk.Button(ventana, text="Eliminar Imagen", command=eliminar_imagen)
btn_eliminar.pack(pady=5)

# Lista de imágenes
frame_lista = tk.Frame(ventana)
frame_lista.pack(pady=10)

scrollbar = Scrollbar(frame_lista)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

lista = Listbox(frame_lista, width=50, height=15, yscrollcommand=scrollbar.set)
lista.pack(side=tk.LEFT)
scrollbar.config(command=lista.yview)

# Panel para mostrar imagen
panel = tk.Label(ventana)
panel.pack(pady=10)

# Cargar lista inicial
listar_imagenes()

ventana.mainloop()

# Cerrar conexión al salir
cursor.close()
conn.close()