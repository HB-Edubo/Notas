import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

excel_path = None

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

def seleccionar_excel():
    global excel_path
    path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
    if path:
        excel_path = path
        label_excel.config(text=os.path.basename(path))

def llenar_formulario():
    if not excel_path:
        messagebox.showwarning("Advertencia", "Primero selecciona un archivo Excel.")
        return

    try:
        df = pd.read_excel(excel_path)

        required_cols = {'NOMBRE COMPLETO', 'Faltas 1ºP', '1º Parcial'}
        if not required_cols.issubset(df.columns):
            messagebox.showerror("Error", f"El Excel debe tener columnas: {', '.join(required_cols)}")
            return

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        driver = webdriver.Chrome(options=chrome_options)

        time.sleep(2)

        filas = driver.find_elements(By.CSS_SELECTOR,
            "#ContentPlaceHolder1_CUAcademicoDocente1_CUTranscripcionNotas1_GVEstudianteNotas tbody tr[valign='top']")

        for fila in filas:
            try:
                span_nombre = fila.find_element(By.CSS_SELECTOR, "span[id*='LBLNombreCompleto']")
                nombre_web = span_nombre.text.strip().upper()
            except:
                continue

            fila_excel = df[df['NOMBRE COMPLETO'].str.strip().str.upper() == nombre_web]
            if fila_excel.empty:
                print(f"❌ No hay datos en Excel para {nombre_web}")
                continue

            datos = fila_excel.iloc[0]
            faltas = datos['Faltas 1ºP']
            nota = datos['1º Parcial']

            def set_input(name_part, value):
                try:
                    campo = fila.find_element(By.CSS_SELECTOR, f"input[name*='{name_part}']")
                    if campo.get_attribute("disabled"):
                        print(f"⚠️ Campo {name_part} para {nombre_web} está deshabilitado.")
                        return False
                    campo.clear()
                    campo.send_keys(str(value))
                    return True
                except Exception as e:
                    print(f"❌ No se encontró {name_part} para {nombre_web}: {e}")
                    return False

            ok_nota = set_input("TXTP1", nota)
            ok_faltas = set_input("TXTF1", faltas)

            print(f"✅ {nombre_web}: nota={'✔' if ok_nota else '✘'}, faltas={'✔' if ok_faltas else '✘'}")

        messagebox.showinfo("Éxito", "Todos los datos fueron ingresados.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

ventana = tk.Tk()
ventana.title("Formulario Automático Universidad")
ventana.geometry("400x250")
ventana.resizable(False, False)

tk.Label(ventana, text="Automatizador de notas y asistencia", font=("Arial", 12, "bold")).pack(pady=10)

tk.Button(ventana, text="Abrir Chrome", width=30, command=abrir_chrome).pack(pady=5)

tk.Button(ventana, text="Seleccionar archivo Excel", width=30, command=seleccionar_excel).pack(pady=5)
label_excel = tk.Label(ventana, text="Ningún archivo seleccionado", fg="gray")
label_excel.pack(pady=2)

tk.Button(ventana, text="Llenar Formulario", width=30, bg="#4CAF50", fg="white", command=llenar_formulario).pack(pady=15)

ventana.mainloop()

