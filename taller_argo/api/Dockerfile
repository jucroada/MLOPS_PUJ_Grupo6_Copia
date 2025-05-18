# Imagen base
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente y script de entrenamiento
COPY app/main.py app/main.py
COPY app/model.pkl app/model.pkl

# Exponer el puerto donde correrá la API
EXPOSE 8989

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8989"]
