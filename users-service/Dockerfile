# Imagen base ligera de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Variables de entorno para ejecucion optimizada de Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalacion de dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia del codigo fuente
COPY . .

# Comando de ejecucion con recarga en desarrollo
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
