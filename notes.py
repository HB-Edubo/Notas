import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Leer archivo Excel con notas y asistencia
df = pd.read_excel('notas.xlsx')

# Conectarse a Chrome ya abierto con debugging
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(options=chrome_options)

# Esperar unos segundos por si acaso
time.sleep(2)

# Recorrer cada fila del Excel
for _, row in df.iterrows():
    nombre = row['Nombre']
    nota = row['Nota']
    asistencia = row['Asistencia']

    try:
        # Rellenar campo de nota
        nota_input = driver.find_element(By.CSS_SELECTOR, f'input[name="nota"][data-nombre="{nombre}"]')
        nota_input.clear()
        nota_input.send_keys(str(nota))

        # Rellenar campo de asistencia
        asistencia_input = driver.find_element(By.CSS_SELECTOR, f'input[name="asistencia"][data-nombre="{nombre}"]')
        asistencia_input.clear()
        asistencia_input.send_keys(str(asistencia))

        print(f"✅ Datos ingresados para {nombre}")
    except Exception as e:
        print(f"❌ Error al ingresar datos para {nombre}: {e}")

print("🎯 Proceso completado.")


