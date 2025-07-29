import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time
from PIL import Image, ImageTk

# Configuración global de CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

excel_path = None
logo_ref = None  # Mantener referencia al logo

# Funciones principales
def abrir_chrome():
    ruta_chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(ruta_chrome):
        messagebox.showerror("Error", "No se encontró Chrome en la ruta especificada.")
        return
    # Avanzar barra al inicio de carga
    progressbar.set(0.1)
    comando = f'"{ruta_chrome}" --remote-debugging-port=9222 --user-data-dir="C:\\chrome-temp"'
    try:
        subprocess.Popen(comando, shell=True)
        ventana.after(2000, lambda: progressbar.set(0.33))
        messagebox.showinfo("Éxito", "Chrome se abrió correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir Chrome:\n{e}")


def seleccionar_excel():
    global excel_path
    path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
    if path:
        excel_path = path
        label_excel.configure(text=os.path.basename(path), text_color="#ffffff")
        # Barra al abrir Excel
        progressbar.set(0.66)


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
        total = len(filas)
        if total == 0:
            messagebox.showinfo("Información", "No se encontraron filas en la página web.")
            return

        # Iterar y actualizar barra proporcionalmente
        for idx, fila in enumerate(filas):
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
                        return False
                    campo.clear()
                    campo.send_keys(str(value))
                    return True
                except:
                    return False

            set_input("TXTP1", nota)
            set_input("TXTF1", faltas)
            # Actualizar barra: desde 0.66 a 1.0
            progressbar.set(0.66 + 0.34 * ((idx + 1) / total))

        messagebox.showinfo("Éxito", "Todos los datos fueron ingresados.")
        progressbar.set(1.0)
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

# Ventana principal
ventana = ctk.CTk()
ventana.title("Formulario Automático Universidad")
ventana.geometry("480x360")
ventana.resizable(False, False)
ventana.configure(fg_color="#cc0605")

# Header con logo y título
header_frame = ctk.CTkFrame(ventana, fg_color="#1d1d1b", height=100, corner_radius=0)
header_frame.pack(fill="x", side="top")

logo_path = os.path.join(os.path.dirname(__file__), "edubo.png")
logo_img = Image.open(logo_path).resize((70, 20), resample=Image.LANCZOS)
logo = ImageTk.PhotoImage(logo_img)
logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
logo_label.place(x=10, y=10)

ctk.CTkLabel(
    header_frame,
    text="Formulario Automático Universidad",
    text_color="#ffffff",
    font=("Helvetica", 20, "bold")
).place(relx=0.5, rely=0.6, anchor="center")

# Cuerpo
body_frame = ctk.CTkFrame(ventana, fg_color="#cc0605")
body_frame.pack(expand=True, fill="both", padx=20, pady=(20,10))
body_frame.grid_columnconfigure(0, weight=1)

btn1 = ctk.CTkButton(
    body_frame,
    text="🌐 ABRIR CHROME",
    text_color="#cc0605",
    font=("Helvetica", 12),
    corner_radius=12,
    fg_color="#ffffff",
    hover_color="#b7b7b7",
    width=220,
    height=40,
    command=abrir_chrome
)
btn1.grid(row=0, column=0, pady=6)

btn2 = ctk.CTkButton(
    body_frame,
    text="📂 SELECCIONAR EXCEL",
    corner_radius=12,
    text_color="#cc0605",
    font=("Helvetica", 12),
    fg_color="#ffffff",
    hover_color="#b7b7b7",
    width=220,
    height=40,
    command=seleccionar_excel
)
btn2.grid(row=1, column=0, pady=6)

label_excel = ctk.CTkLabel(
    body_frame,
    text="Ningún archivo seleccionado",
    text_color="#ffffff",
    font=("Helvetica", 14)
)
label_excel.grid(row=2, column=0, pady=4)

btn3 = ctk.CTkButton(
    body_frame,
    text="🚀 LLENAR FORMULARIO",
    corner_radius=12,
    font=("Helvetica", 12),
    fg_color="#434343",
    hover_color="#232323",
    width=220,
    height=40,
    command=llenar_formulario
)
btn3.grid(row=3, column=0, pady=10)

action_frame = ctk.CTkFrame(ventana, fg_color="#cc0605")
action_frame.pack(fill="x", side="bottom", pady=(2, 5))
progressbar = ctk.CTkProgressBar(action_frame, orientation="horizontal", width=350, progress_color="#ffffff")
progressbar.pack(pady=5)
progressbar.set(0)

ventana.mainloop()
