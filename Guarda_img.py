import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, Entry, Label
import mysql.connector
from PIL import Image, ImageTk
import io
import os

# Configuración de conexión MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'imagenes_db'
}

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS imagenes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE,
        imagen LONGBLOB
    )
""")
conn.commit()

def convertir_a_binario(ruta):
    with open(ruta, 'rb') as f:
        return f.read()

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

def listar_imagenes(filtro_nombre='', filtro_extension=''):
    lista.delete(0, tk.END)
    query = "SELECT nombre FROM imagenes"
    condiciones = []
    valores = []
    if filtro_nombre:
        condiciones.append("nombre LIKE %s")
        valores.append(f"%{filtro_nombre}%")
    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)
    query += " ORDER BY id DESC"
    cursor.execute(query, valores)
    resultados = cursor.fetchall()
    for (nombre,) in resultados:
        if filtro_extension and not nombre.lower().endswith(filtro_extension):
            continue
        lista.insert(tk.END, nombre)
    contador_label.config(text=f"Total imágenes: {len(resultados)}")

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
        img.thumbnail((600, 600))
        img_tk = ImageTk.PhotoImage(img)
        panel.config(image=img_tk)
        panel.image = img_tk

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

def aplicar_filtros():
    filtro_nombre = entrada_busqueda.get().strip()
    filtro_extension = entrada_extension.get().strip().lower()
    listar_imagenes(filtro_nombre, filtro_extension)

ventana = tk.Tk()
ventana.title("Gestión Avanzada de Imágenes en MySQL")
ventana.geometry("800x700")

btn_insertar = tk.Button(ventana, text="Insertar Imágenes", command=insertar_imagenes)
btn_insertar.pack(pady=5)

btn_ver = tk.Button(ventana, text="Ver Imagen", command=ver_imagen)
btn_ver.pack(pady=5)

btn_descargar = tk.Button(ventana, text="Descargar Imagen", command=descargar_imagen)
btn_descargar.pack(pady=5)

btn_eliminar = tk.Button(ventana, text="Eliminar Imagen", command=eliminar_imagen)
btn_eliminar.pack(pady=5)

frame_filtros = tk.Frame(ventana)
frame_filtros.pack(pady=10)
Label(frame_filtros, text="Buscar por nombre:").grid(row=0, column=0)
entrada_busqueda = Entry(frame_filtros)
entrada_busqueda.grid(row=0, column=1)
Label(frame_filtros, text="Filtrar por extensión (.jpg/.png):").grid(row=1, column=0)
entrada_extension = Entry(frame_filtros)
entrada_extension.grid(row=1, column=1)
btn_filtrar = tk.Button(frame_filtros, text="Aplicar filtros", command=aplicar_filtros)
btn_filtrar.grid(row=2, column=0, columnspan=2, pady=5)

frame_lista = tk.Frame(ventana)
frame_lista.pack(pady=10)
scrollbar = Scrollbar(frame_lista)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
lista = Listbox(frame_lista, width=50, height=15, yscrollcommand=scrollbar.set)
lista.pack(side=tk.LEFT)
scrollbar.config(command=lista.yview)

contador_label = Label(ventana, text="Total imágenes: 0")
contador_label.pack(pady=5)

panel = tk.Label(ventana)
panel.pack(pady=10)

listar_imagenes()
ventana.mainloop()

cursor.close()
conn.close()