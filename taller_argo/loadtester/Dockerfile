FROM python:3.9-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script de carga
COPY main.py .

# Ejecutar el script
CMD ["python", "main.py"]
