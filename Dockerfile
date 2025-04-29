# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --target=/app/dependencies

COPY . .

# Final stage
FROM python:3.12-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /app/dependencies /app/dependencies
COPY --from=builder /app/app ./app
COPY --from=builder /app/web ./web
COPY --from=builder /app/run.py .

ENV PYTHONPATH=/app/dependencies
ENV FLASK_APP=web
ENV FLASK_ENV=production

VOLUME ["/app/db"]
RUN mkdir -p /app/db && \
    chown -R appuser:appuser /app && \
    chmod 777 /app/db

USER appuser

EXPOSE 5000

CMD ["python", "run.py"]
