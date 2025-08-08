# verificacion_key.py
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import tkinter as tk
from utils.session import guardar_estado_sesion

def ventana_codigo_verificacion(ventana, db, btn1, btn2, btn3):
    """
    Mantiene la ventana en 380x300 y asegura que el botón
    'INICIAR SESIÓN' siempre se vea. El scrollbar está oculto/deshabilitado.
    """
    ventana_pin = ctk.CTkToplevel()
    ventana_pin.title("Iniciar sesión con código")

    # Tamaño EXACTO solicitado
    base_w = 380
    base_h = 300
    ventana_pin.geometry(f"{base_w}x{base_h}")
    ventana_pin.resizable(False, False)
    ventana_pin.configure(fg_color="#ffffff")
    ventana_pin.transient(ventana)

    # Intento de posicionamiento al costado como en tu original
    try:
        ventana.update_idletasks()
        main_x = ventana.winfo_x()
        main_y = ventana.winfo_y()
        main_w = ventana.winfo_width()
        nueva_x = main_x + main_w + 10
        nueva_y = main_y + 50
        screen_w = ventana.winfo_screenwidth()
        screen_h = ventana.winfo_screenheight()
        if nueva_x + base_w > screen_w:
            nueva_x = max(20, main_x + (main_w - base_w)//2)
        if nueva_y + base_h > screen_h:
            nueva_y = max(20, main_y + 20)
        ventana_pin.geometry(f"+{nueva_x}+{nueva_y}")
    except Exception as e:
        print(f"No se pudo posicionar al costado: {e}")

    # --- Estructura: área de contenido (sin scroll visible) + bottom_frame con botón ---
    main_container = ctk.CTkFrame(ventana_pin, fg_color="transparent")
    main_container.pack(fill="both", expand=True)

    bottom_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    bottom_frame.pack(side="bottom", fill="x", pady=(6, 10))

    # Content area: canvas sin scrollbar visible
    content_holder = tk.Frame(main_container)
    content_holder.pack(side="top", fill="both", expand=True, padx=8, pady=(8, 4))

    canvas = tk.Canvas(content_holder, highlightthickness=0, bd=0, background="#ffffff")
    canvas.pack(side="left", fill="both", expand=True)

    # inner_frame donde reside el contenido (se crea dentro del canvas)
    inner_frame = ctk.CTkFrame(canvas, fg_color="transparent")
    inner_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Actualiza la scrollregion internamente (aunque no mostramos scrollbar)
    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    inner_frame.bind("<Configure>", _on_frame_configure)

    # Ajustar ancho del inner_frame al ancho del canvas cuando la ventana cambie
    def _on_canvas_configure(event):
        canvas.itemconfigure(inner_id, width=event.width)
    canvas.bind("<Configure>", _on_canvas_configure)

    # NOTA: No se añaden scrollbar widgets ni bindings de rueda del mouse.
    # Si el contenido excede la altura, quedará recortado (como pediste).

    # ------------------ CARGA DE ICONOS ------------------
    closed_icon = None
    open_icon = None
    try:
        closed_icon_img = Image.open(os.path.join("images", "closed_key.png")).resize((70, 80))
        open_icon_img = Image.open(os.path.join("images", "open_key.png")).resize((70, 80))
        closed_icon = ImageTk.PhotoImage(closed_icon_img)
        open_icon = ImageTk.PhotoImage(open_icon_img)
    except Exception:
        closed_icon = None
        open_icon = None

    # ------------------ CONTENIDO (dentro de inner_frame) ------------------
    if closed_icon:
        icon_label = ctk.CTkLabel(inner_frame, image=closed_icon, text="")
        icon_label.image = closed_icon
    else:
        icon_label = ctk.CTkLabel(inner_frame, text="🔐", font=("Helvetica", 30))
    icon_label.pack(pady=(12, 8))

    titulo = ctk.CTkLabel(inner_frame, text="Código de verificación",
                          text_color="#000000", font=("Helvetica", 20, "bold"))
    titulo.pack()

    subtitulo = ctk.CTkLabel(inner_frame, text="Ingresa tu código de 8 dígitos para iniciar sesión",
                             text_color="#555555", font=("Helvetica", 12))
    subtitulo.pack(pady=(2, 10))

    entry_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
    entry_frame.pack(pady=(6, 6))

    entries = []

    def on_key(event, index):
        char = event.char
        key = event.keysym

        if key == "BackSpace":
            if entries[index].get():
                entries[index].delete(0, 'end')
            else:
                if index > 0:
                    entries[index - 1].delete(0, 'end')
                    entries[index - 1].focus()
            return "break"

        if not char or len(char) != 1:
            return "break"

        # Si quieres forzar dígitos, descomenta:
        # if not char.isdigit():
        #     return "break"

        entries[index].delete(0, 'end')
        entries[index].insert(0, char)

        if index < 7:
            entries[index + 1].focus()
        return "break"

    # Crear 8 entradas (grid dentro de entry_frame)
    for i in range(8):
        e = ctk.CTkEntry(entry_frame, width=36, height=40, font=("Helvetica", 18), justify="center")
        e.grid(row=0, column=i, padx=3)
        e.bind("<Key>", lambda event, index=i: on_key(event, index))
        entries.append(e)

    resultado_label = ctk.CTkLabel(inner_frame, text="", font=("Helvetica", 12))
    resultado_label.pack(pady=(8, 6))

    # ------------------ VERIFICAR ------------------
    def verificar_codigo():
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

            if uses <= 0:
                resultado_label.configure(text="❌ Código sin usos disponibles", text_color="red")
                return

            # Activar solo si es la primera vez
            if not activated:
                doc_ref.update({"activated": True})

            # Inicio de sesión exitoso
            resultado_label.configure(text="✅ Sesión iniciada correctamente", text_color="green")
            if open_icon:
                icon_label.configure(image=open_icon)
                icon_label.image = open_icon

            # Habilitar botones de la ventana principal
            try:
                btn1.configure(state="normal")
                btn2.configure(state="normal")
                btn3.configure(state="normal")
            except Exception:
                pass

            name = data.get("name", "Usuario")
            gmail = data.get("gmail", "")

            # Mostrar nombre en ventana principal si se puede
            try:
                nombre_label = ctk.CTkLabel(
                    ventana,
                    text=f"👋 Bienvenido, {name}",
                    text_color="#000000",
                    font=("Helvetica", 16, "bold")
                )
                nombre_label.pack(pady=10)
            except Exception:
                pass

            guardar_estado_sesion(codigo, name, gmail)

            if hasattr(ventana, "set_nombre_usuario"):
                ventana.set_nombre_usuario(name, gmail)

        except Exception as e:
            resultado_label.configure(text=f"Error: {e}", text_color="red")

    # ------------------ BOTÓN (siempre visible en bottom_frame) ------------------
    btn_verificar = ctk.CTkButton(
        bottom_frame,
        text="INICIAR SESIÓN",
        font=("Helvetica", 14, "bold"),
        fg_color="#cc0605",
        hover_color="#a00404",
        text_color="#ffffff",
        width=160,
        height=45,
        command=verificar_codigo
    )
    btn_verificar.pack(pady=6)

    # Forzar actualización del canvas/scrollregion (aunque no mostraremos scrollbar)
    ventana_pin.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    return ventana_pin
