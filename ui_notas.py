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

# Variables globales
excel_path = None
logo_ref = None  # Mantener referencia al logo

# Funciones del programa
def abrir_chrome():
    ruta_chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(ruta_chrome):
        messagebox.showerror("Error", f"No se encontró Chrome en: {ruta_chrome}")
        return
    try:
        progressbar.start()
        subprocess.Popen([
            ruta_chrome,
            "--remote-debugging-port=9222",
            f"--user-data-dir={os.path.join(os.getcwd(), 'chrome-temp')}"
        ])
        ventana.after(2000, progressbar.stop)
        messagebox.showinfo("Éxito", "Chrome se abrió correctamente.")
    except Exception as e:
        progressbar.stop()
        messagebox.showerror("Error", f"No se pudo abrir Chrome:\n{e}")


def seleccionar_excel():
    global excel_path
    path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
    if path:
        excel_path = path
        label_excel.configure(text=os.path.basename(path), text_color="#ffffff")


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
        progressbar.start()
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
            except Exception as ex:
                print(f"❌ No se encontró el campo para {nombre}: {ex}")
        progressbar.stop()
        messagebox.showinfo("Éxito", "Todos los datos fueron ingresados.")
    except Exception as e:
        progressbar.stop()
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

# --- Interfaz gráfica ---
ventana = ctk.CTk()
ventana.title("Formulario Automático Universidad")
ventana.geometry("480x360")  
ventana.resizable(False, False)
ventana.configure(fg_color="#cc0605")

def crear_header(master):
    frame = ctk.CTkFrame(master, fg_color="#1d1d1b", height=100, corner_radius=0)
    frame.pack(fill="x", side="top")
    return frame

header_frame = crear_header(ventana)
# Logo 
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edubo.png")
if os.path.exists(logo_path):
    img = Image.open(logo_path).resize((70, 30), resample=Image.LANCZOS)
    logo_ref = ImageTk.PhotoImage(img)
    logo_label = ctk.CTkLabel(header_frame, image=logo_ref, text="")
    logo_label.place(x=10, y=10)

# Título grande centrado en header
titulo = ctk.CTkLabel(
    header_frame,
    text="Automatizador de notas y asistencia",
    text_color="#ffffff",
    font=("Helvetica", 20, "bold")  # Fuente más grande
)
titulo.place(relx=0.5, rely=0.6, anchor="center")

# Cuerpo principal con botones y margen superior mayor
body_frame = ctk.CTkFrame(ventana, fg_color="#cc0605")
body_frame.pack(expand=True, fill="both", padx=20, pady=(20,0))  # Aumenta margen superior
body_frame.grid_columnconfigure(0, weight=1)

# Botones con fuente reducida
txt_btn = ("Helvetica", 12, "bold")
btn_width, btn_height = 220, 40

btn1 = ctk.CTkButton(
    body_frame,
    text="🌐 ABRIR CHROME",
    text_color="#cc0605",
    corner_radius=12,
    fg_color="#ffffff",
    hover_color="#b7b7b7",
    width=btn_width,
    height=btn_height,
    font=txt_btn,
    command=abrir_chrome
)
btn1.grid(row=0, column=0, pady=6)

btn2 = ctk.CTkButton(
    body_frame,
    text="📂 SELECCIONAR EXCEL",
    corner_radius=12,
    text_color="#cc0605",
    fg_color="#ffffff",
    hover_color="#b7b7b7",
    width=btn_width,
    height=btn_height,
    font=txt_btn,
    command=seleccionar_excel
)
btn2.grid(row=1, column=0, pady=6)

label_excel = ctk.CTkLabel(
    body_frame,
    text="Ningún archivo seleccionado",
    text_color="#ffffff",
    font=("Helvetica", 14)
)
label_excel.grid(row=2, column=0, pady=6)

btn3 = ctk.CTkButton(
    body_frame,
    text="🚀 LLENAR FORMULARIO",
    corner_radius=12,
    fg_color="#434343",
    hover_color="#232323",
    width=btn_width,
    height=btn_height,
    font=txt_btn,
    command=llenar_formulario
)
btn3.grid(row=3, column=0, pady=6)

# Barra de progreso al fondo con menos margen superior
action_frame = ctk.CTkFrame(ventana, fg_color="#cc0605")
action_frame.pack(fill="x", side="bottom", pady=(2,5))
progressbar = ctk.CTkProgressBar(
    action_frame,
    orientation="horizontal",
    width=440,
    progress_color="#ffffff"
)
progressbar.pack(pady=2)
progressbar.set(0)

# Label de resultado opcional
result_label = ctk.CTkLabel(
    ventana,
    text="",
    text_color="#f8f8ff",
    font=("Helvetica", 11, "italic")
)
result_label.pack(pady=(0,5))

ventana.mainloop()
