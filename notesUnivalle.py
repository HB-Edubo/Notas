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
import firebase_admin
from firebase_admin import credentials, firestore
import socket
from PIL import Image

key_validated = False  # estado global de la key

# Configuración global de CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

excel_path = None
logo_ref = None  # Mantener referencia al logo

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate("key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def hay_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False
    
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
        #messagebox.showinfo("Éxito", "Chrome se abrió correctamente.")
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



def validar_codigo():
    from customtkinter import CTkInputDialog
    dialog = CTkInputDialog(text="Ingresa tu código de acceso:", title="Verificación")
    codigo = dialog.get_input()

    if not codigo:
        return

    try:
        doc_ref = db.collection("keys").document(codigo)
        doc = doc_ref.get()
        if doc.exists:
            messagebox.showinfo("Éxito", "✅ Usuario aceptado")
        else:
            messagebox.showwarning("Código inválido", "❌ El código no está registrado.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al validar:\n{e}")



def ventana_codigo_verificacion():
    ventana_pin = ctk.CTkToplevel()
    ventana_pin.title("Código de Verificación")
    ventana_pin.geometry("380x300")
    ventana_pin.resizable(False, False)
    ventana_pin.configure(fg_color="#ffffff")

    # Posicionar al costado derecho de la ventana principal
    try:
        ventana.update_idletasks()
        main_x = ventana.winfo_x()
        main_y = ventana.winfo_y()
        main_w = ventana.winfo_width()
        main_h = ventana.winfo_height()

        # Posicionar la ventana nueva al costado derecho
        nueva_x = main_x + main_w + 10
        nueva_y = main_y + 50
        ventana_pin.geometry(f"+{nueva_x}+{nueva_y}")
    except Exception as e:
        print(f"No se pudo posicionar al costado: {e}")


    # Iconos: candado cerrado y abierto
    closed_icon_img = Image.open(os.path.join(os.path.dirname(__file__), "images", "closed_key.png")).resize((70, 80))
    open_icon_img = Image.open(os.path.join(os.path.dirname(__file__), "images", "open_key.png")).resize((70, 80))

    closed_icon = ImageTk.PhotoImage(closed_icon_img)
    open_icon = ImageTk.PhotoImage(open_icon_img)

    # Mostrar icono inicial (cerrado)
    icon_label = ctk.CTkLabel(ventana_pin, image=closed_icon, text="")
    icon_label.image = closed_icon  # mantener referencia
    icon_label.pack(pady=(20, 10))

    # Título
    titulo = ctk.CTkLabel(ventana_pin, text="Código de verificación", text_color="#000000", font=("Helvetica", 20, "bold"))
    titulo.pack()

    # Subtítulo
    subtitulo = ctk.CTkLabel(ventana_pin, text="Por favor ingresa el código de 8 dígitos", text_color="#555555", font=("Helvetica", 14))
    subtitulo.pack(pady=(0, 10))

    # Cuadro de entrada dividido (8 dígitos)
    entry_frame = ctk.CTkFrame(ventana_pin, fg_color="transparent")
    entry_frame.pack(pady=10)

    entries = []

    def on_key(event, index):
        char = event.char
        key = event.keysym

        if key == "BackSpace":
            entries[index].delete(0, 'end')
            if index > 0 and entries[index].get() == '':
                entries[index - 1].focus()
            return

        if not char.isalnum() or len(char) != 1:
            return "break"

        entries[index].delete(0, 'end')
        entries[index].insert(0, char)

        if index < 7:
            entries[index + 1].focus()

        return "break"

    for i in range(8):
        e = ctk.CTkEntry(entry_frame, width=30, height=40, font=("Helvetica", 18), justify="center")
        e.grid(row=0, column=i, padx=3)
        e.bind("<Key>", lambda event, index=i: on_key(event, index))
        entries.append(e)



    # Mensaje dinámico
    resultado_label = ctk.CTkLabel(ventana_pin, text="", font=("Helvetica", 14))
    resultado_label.pack(pady=10)

    # Función verificar
    def verificar_codigo():
        global key_validated
        codigo = ''.join(entry.get() for entry in entries).strip()
        if len(codigo) != 8:
            resultado_label.configure(text="Debe ingresar los 8 dígitos", text_color="red")
            return

        try:
            doc_ref = db.collection("keys").document(codigo)
            doc = doc_ref.get()

            if not doc.exists:
                resultado_label.configure(text="❌ Código no válido", text_color="red")
                return

            data = doc.to_dict()
            activated = data.get("activated", False)
            uses = data.get("uses", 0)

            if activated:
                resultado_label.configure(text="❌ Código ya fue activado", text_color="red")
                return

            if uses <= 0:
                resultado_label.configure(text="❌ Código sin usos disponibles", text_color="red")
                return

            # ✅ Si pasa todas las validaciones
            doc_ref.update({
                "activated": True,
                "uses": uses - 1
            })

            resultado_label.configure(text="✅ Usuario aceptado", text_color="green")
            icon_label.configure(image=open_icon)
            icon_label.image = open_icon

            key_validated = True

            # Habilitar botones principales
            btn1.configure(state="normal")
            btn2.configure(state="normal")
            btn3.configure(state="normal")

        except Exception as e:
            resultado_label.configure(text=f"Error: {e}", text_color="red")

    # Botón VERIFICAR
    btn_verificar = ctk.CTkButton(
        ventana_pin,
        text="VERIFY",
        font=("Helvetica", 14, "bold"),
        fg_color="#cc0605",
        hover_color="#a00404",
        text_color="#ffffff",
        width=160,
        height=45,
        command=verificar_codigo
    )
    btn_verificar.pack(pady=5)


def verificar_conexion_periodica():
    conectado = hay_internet()

    # Ruta dinámica
    icono_path = os.path.join(os.path.dirname(__file__), "images", "con-internet.png" if conectado else "sin-internet.png")
    nueva_img = ctk.CTkImage(light_image=Image.open(icono_path).resize((25, 25), resample=Image.LANCZOS))

    # Actualizar ícono
    internet_label.configure(image=nueva_img)
    internet_label.image = nueva_img

    # Habilitar o deshabilitar botón
    if conectado:
        btn3.configure(state="normal", fg_color="#434343", hover_color="#232323")
    else:
        btn3.configure(state="disabled", fg_color="#999999", hover_color="#999999")

    # Repetir cada 5 segundos
    ventana.after(5000, verificar_conexion_periodica)


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

btn1.configure(state="disabled")
btn2.configure(state="disabled")
btn3.configure(state="disabled")

action_frame = ctk.CTkFrame(ventana, fg_color="#cc0605")
action_frame.pack(fill="x", side="bottom", pady=(2, 5))
progressbar = ctk.CTkProgressBar(action_frame, orientation="horizontal", width=350, progress_color="#ffffff")
progressbar.pack(pady=5)
progressbar.set(0)

#Ventana de la key
# Botón de acceso con imagen en la esquina superior derecha
key_icon_path = os.path.join(os.path.dirname(__file__), "./images/key_icon.png")
key_img = Image.open(key_icon_path).resize((25, 25), resample=Image.LANCZOS)
key_photo = ImageTk.PhotoImage(key_img)

key_button = ctk.CTkButton(
    header_frame,
    image=key_photo,
    text="",
    width=25,
    height=25,
    fg_color="transparent",
    hover_color="#333333",
    command=ventana_codigo_verificacion
)
key_button.image = key_photo  # evitar que se pierda referencia
key_button.place(relx=1.0, x=-20, y=10, anchor="ne")  # esquina superior derecha con margen

# Ícono de conexión a internet
internet_icon_path = os.path.join(os.path.dirname(__file__), "images", "con-internet.png" if hay_internet() else "sin-internet.png")
internet_icon_img = Image.open(internet_icon_path).resize((7, 10), resample=Image.LANCZOS)
internet_photo = ctk.CTkImage(light_image=internet_icon_img)

internet_label = ctk.CTkLabel(
    header_frame,
    image=internet_photo,
    text=""
)
internet_label.image = internet_photo
internet_label.place(relx=1.0, x=-60, y=7, anchor="ne")  # al lado izquierdo del botón llave


verificar_conexion_periodica()
ventana.mainloop()
