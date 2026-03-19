FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y wget gnupg ca-certificates && rm -rf /var/lib/apt/lists/*

RUN pip install flask playwright requests

RUN playwright install chromium
RUN playwright install-deps chromium

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]
