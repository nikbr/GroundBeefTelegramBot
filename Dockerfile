FROM python:3.10.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY server.py .
COPY client.py .

# Entrypoint can be either server or client as default. Command overridden in docker-compose.
CMD ["python", "server.py"]