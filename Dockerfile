FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para Playwright/Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar Flask y Playwright
RUN pip install flask playwright

# Instalar Chromium y sus dependencias
RUN playwright install chromium
RUN playwright install-deps chromium

# Copiar el código
COPY server.py .

# Puerto que usa Flask
EXPOSE 8000

# Arrancar el servidor
CMD ["python", "server.py"]
