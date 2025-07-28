import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

# Variables globales
excel_path = None

# Función para abrir Chrome con debugging
def abrir_chrome():
    ruta_chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(ruta_chrome):
        messagebox.showerror("Error", "No se encontró Chrome en la ruta especificada.")
        return
    
    comando = f'"{ruta_chrome}" --remote-debugging-port=9222 --user-data-dir="C:\\chrome-temp"'
    try:
        subprocess.Popen(comando, shell=True)
        messagebox.showinfo("Éxito", "Chrome se abrió correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir Chrome:\n{e}")

# Función para seleccionar el Excel
def seleccionar_excel():
    global excel_path
    path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
    if path:
        excel_path = path
        label_excel.config(text=os.path.basename(path))

# Función para llenar el formulario
def llenar_formulario():
    if not excel_path:
        messagebox.showwarning("Advertencia", "Primero selecciona un archivo Excel.")
        return
    
    try:
        df = pd.read_excel(excel_path)

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        driver = webdriver.Chrome(options=chrome_options)

        time.sleep(2)

        for _, row in df.iterrows():
            nombre = row['Nombre']
            nota = row['Nota']
            asistencia = row['Asistencia']

            try:
                input_nota = driver.find_element(By.CSS_SELECTOR, f'input[name="nota"][data-nombre="{nombre}"]')
                input_nota.clear()
                input_nota.send_keys(str(nota))

                input_asistencia = driver.find_element(By.CSS_SELECTOR, f'input[name="asistencia"][data-nombre="{nombre}"]')
                input_asistencia.clear()
                input_asistencia.send_keys(str(asistencia))

                print(f"✅ Datos ingresados para {nombre}")
            except Exception as e:
                print(f"❌ No se encontró el campo para {nombre}: {e}")

        messagebox.showinfo("Éxito", "Todos los datos fueron ingresados.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Formulario Automático Universidad")
ventana.geometry("400x250")
ventana.resizable(False, False)

tk.Label(ventana, text="Automatizador de notas y asistencia", font=("Arial", 12, "bold")).pack(pady=10)

# Botón abrir Chrome
tk.Button(ventana, text="Abrir Chrome", width=30, command=abrir_chrome).pack(pady=5)

# Botón seleccionar Excel
tk.Button(ventana, text="Seleccionar archivo Excel", width=30, command=seleccionar_excel).pack(pady=5)
label_excel = tk.Label(ventana, text="Ningún archivo seleccionado", fg="gray")
label_excel.pack(pady=2)

# Botón llenar datos
tk.Button(ventana, text="Llenar Formulario", width=30, bg="#4CAF50", fg="white", command=llenar_formulario).pack(pady=15)

ventana.mainloop()

