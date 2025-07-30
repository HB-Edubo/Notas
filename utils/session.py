import json
import os

SESSION_FILE = "session.json"

def guardar_estado_sesion():
    with open(SESSION_FILE, "w") as f:
        json.dump({"key_activated": True}, f)

def cargar_estado_sesion():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
            return data.get("key_activated", False)
    return False
