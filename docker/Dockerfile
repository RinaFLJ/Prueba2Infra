FROM python:3.10-slim

WORKDIR /app

# Copiar e instalar requerimientos
COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY appAsync/ ./appAsync/
COPY blockchainAudit/ ./blockchainAudit/

# Establecer la variable de entorno para que Python no genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1