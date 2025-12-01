FROM python:3.11-slim

WORKDIR /app

# Opcional: menos ruido
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# FastAPI server para /run
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
