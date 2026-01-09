FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default service to run, can be overridden in docker-compose
CMD ["uvicorn", "services.content-service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
