# Stage 1: сборка зависимостей
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: финальный образ
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY reader.py .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/')" || exit 1

CMD ["uvicorn", "reader:app", "--host", "0.0.0.0", "--port", "8001"]
