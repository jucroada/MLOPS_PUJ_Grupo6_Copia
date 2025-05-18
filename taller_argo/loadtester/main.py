import requests
import random
import time
import os

# URL de la API (puede ser inyectada vía variable de entorno)
API_URL = os.getenv("API_URL", "http://api:8989/predict")

# Rango de valores basados en el dataset penguins
def generar_pingüino_aleatorio():
    return {
        "bill_length_mm": round(random.uniform(32.0, 60.0), 1),
        "bill_depth_mm": round(random.uniform(13.0, 21.0), 1),
        "flipper_length_mm": round(random.uniform(170.0, 230.0), 1),
        "body_mass_g": round(random.uniform(2700.0, 6300.0), 1)
    }

# Ciclo principal: enviar peticiones cada segundo
while True:
    datos = generar_pingüino_aleatorio()
    try:
        respuesta = requests.post(API_URL, json=datos)
        print(f"[{respuesta.status_code}] {respuesta.json()} | input: {datos}")
    except Exception as e:
        print(f"Error al hacer request: {e}")
    time.sleep(1)
