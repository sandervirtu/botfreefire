FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y wget gnupg ca-certificates && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

CMD ["python", "app.py"]