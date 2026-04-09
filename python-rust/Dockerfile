# Stage 1: сборка Rust-расширения
FROM python:3.12-slim AS builder

WORKDIR /app

# Устанавливаем системные зависимости для компиляции Rust
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем Rust через rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Устанавливаем maturin
RUN pip install maturin

# Копируем файлы сборки и исходники Rust
COPY Cargo.toml pyproject.toml ./
COPY src/ ./src/

# Собираем wheel с Rust-расширением
RUN maturin build --release --out /wheels

# Устанавливаем расширение и зависимости для тестов
COPY requirements.txt .
RUN pip install /wheels/*.whl
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение и запускаем тесты
COPY app/ ./app/
RUN python -m pytest app/tests/ -v

# Stage 2: финальный образ
FROM python:3.12-slim

WORKDIR /app

# Копируем собранный wheel из builder-стадии и устанавливаем
COPY --from=builder /wheels/*.whl /tmp/
RUN pip install /tmp/*.whl && rm /tmp/*.whl

# Устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY app/ ./app/

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
