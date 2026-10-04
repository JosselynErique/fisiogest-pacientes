# Imagen de producción ligera para FisioGest
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FISIOGEST_DATABASE=/data/fisiogest.db \
    FISIOGEST_DEMO=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

COPY run.py .
COPY src ./src

RUN useradd --create-home fisiogest && mkdir -p /data && chown fisiogest /data
USER fisiogest
VOLUME ["/data"]
EXPOSE 5000

# Un solo proceso con hilos: SQLite y la carga inicial de datos no se ejecutan en paralelo.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "run:app"]
