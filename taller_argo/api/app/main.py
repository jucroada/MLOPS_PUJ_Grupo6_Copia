from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from prometheus_client import (
    Counter, generate_latest, CONTENT_TYPE_LATEST,
    Summary, Gauge
)
from fastapi.responses import Response
import time

# Cargar modelo entrenado
model = joblib.load("app/model.pkl")

# Mapeo fijo de clases (ligero)
species_names = ["Adelie", "Chinstrap", "Gentoo"]

# Crear app
app = FastAPI(
    title="API de Predicción de especie de Pingüinos",
    description="Predice especie de pingüino según características morfológicas",
    version="1.0.1"
)

# Métricas Prometheus
PREDICTION_COUNTER = Counter("predict_requests_total", "Número de predicciones realizadas")
PREDICTION_LATENCY = Summary("predict_latency_seconds", "Latencia del endpoint /predict (segundos)")
UPTIME = Gauge("api_uptime", "API activa (1 si está corriendo)")

# Activamos la métrica de uptime en tiempo de carga
UPTIME.set(1)

# Entrada esperada
class PenguinInput(BaseModel):
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

# Endpoint de predicción
@app.post("/predict")
async def predict(penguin: PenguinInput):
    PREDICTION_COUNTER.inc()
    start_time = time.time()
    data = np.array([[penguin.bill_length_mm, penguin.bill_depth_mm,
                      penguin.flipper_length_mm, penguin.body_mass_g]])
    prediction_index = model.predict(data)[0]
    latency = time.time() - start_time
    PREDICTION_LATENCY.observe(latency)
    return {"prediction": species_names[int(prediction_index)]}

# Endpoint de métricas
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
# Trigger
# otro trigger
# otro trigger