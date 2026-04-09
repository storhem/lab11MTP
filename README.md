# Лабораторная работа №11
Контейнеризация мультиязычных приложений

Студент: Евланичев Максим Юрьевич

Группа: 221131

Вариант: 7

## Задания

Средняя сложность
- М1 — Dockerfile для Python-приложения (FastAPI)
- М7 — Volume для обмена данными между контейнерами
- М9 — Ограничение ресурсов (CPU, память)

Повышенная сложность
- Н1 — Go-приложение со статической компиляцией в scratch-образе
- Н7 — Multi-stage сборка для Python-приложения с Rust-расширением

## Описание

Проект демонстрирует контейнеризацию приложений на трёх языках с оптимизацией размера образов:

- **Python-сервис (FastAPI)** — REST API для управления заметками, двухстадийная Docker-сборка, персистентность через shared volume.
- **Reader-сервис (FastAPI)** — read-only API, читает заметки из того же shared volume.
- **Go-сервис (scratch-образ)** — статически скомпилированный HTTP-сервис в минимальном образе.
- **Python + Rust расширение** — Python-приложение с вычислительным модулем на Rust (PyO3/maturin), multi-stage сборка.

## Структура проекта

```
.
├── python/                   # М1 — FastAPI приложение (notes-api)
│   ├── restnotes.py          # CRUD API для заметок с персистентностью
│   ├── requirements.txt
│   ├── Dockerfile            # Двухстадийная сборка (builder + slim)
│   └── tests/
│       └── test_notes.py     # 24 unit-тестов
├── reader/                   # М7 — read-only сервис (notes-reader)
│   ├── reader.py             # GET /notes, /notes/{id}, /notes/count
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│       └── test_reader.py    # 14 unit-тестов
├── go/                       # Н1 — Go сервис (scratch-образ)
│   ├── main.go               # HTTP-сервис: GET /, /ping, /health, /info
│   ├── main_test.go          # 42 теста через httptest
│   ├── go.mod
│   └── Dockerfile            # CGO_ENABLED=0, ldflags static → scratch
├── python-rust/              # Н7 — Python + Rust расширение
│   ├── src/
│   │   └── lib.rs            # Rust модуль texttools (PyO3)
│   ├── app/
│   │   ├── main.py           # FastAPI: /word-count /reverse /palindrome /fibonacci
│   │   └── tests/
│   │       ├── test_api.py       # 35 тестов FastAPI эндпоинтов
│   │       └── test_texttools.py # 48 тестов Rust-функций напрямую
│   ├── Cargo.toml
│   ├── pyproject.toml        # maturin конфигурация
│   ├── requirements.txt
│   └── Dockerfile            # builder (Rust→wheel) + python:3.12-slim
├── tests/                    # М9 — валидация docker-compose конфигурации
│   ├── test_compose_resources.py  # 36 тестов лимитов ресурсов
│   └── requirements.txt
├── docker-compose.yml        # М7, М9 — оркестрация, volumes, лимиты ресурсов
├── .gitignore
├── PROMPT_LOG.md
└── README.md
```

## Технологии

- Python 3.12 + FastAPI + Uvicorn
- Go 1.22 (CGO_ENABLED=0, scratch-образ)
- Rust + PyO3 + maturin
- Docker multi-stage build

## М1 — Запуск Python-сервиса (notes-api)

```bash
cd python
docker build -t notes-api .
docker run -p 8000:8000 notes-api
```

Сервис запустится на `http://localhost:8000`, документация — `http://localhost:8000/docs`.

### Эндпоинты notes-api

| Метод  | Путь             | Описание             |
|--------|------------------|----------------------|
| GET    | `/`              | Приветствие          |
| GET    | `/notes`         | Список всех заметок  |
| GET    | `/notes/{id}`    | Заметка по ID        |
| POST   | `/notes?text=…`  | Создать заметку      |
| DELETE | `/notes/{id}`    | Удалить заметку      |

### Примеры запросов notes-api

```bash
# Создать заметку
curl -X POST "http://localhost:8000/notes?text=Hello"

# Получить все заметки
curl http://localhost:8000/notes

# Получить заметку по ID
curl http://localhost:8000/notes/1

# Удалить заметку
curl -X DELETE http://localhost:8000/notes/1
```

### Тесты notes-api

```bash
cd python
pip install -r requirements.txt
pytest tests/ -v
```

## М7 — Reader-сервис (notes-reader)

Читает заметки из того же shared volume, что и notes-api. Монтируется read-only.

```bash
cd reader
docker build -t notes-reader .
docker run -e NOTES_FILE=/data/notes.json -p 8001:8001 notes-reader
```

### Эндпоинты notes-reader

| Метод | Путь              | Описание              |
|-------|-------------------|-----------------------|
| GET   | `/`               | Приветствие           |
| GET   | `/notes`          | Список заметок        |
| GET   | `/notes/count`    | Количество заметок    |
| GET   | `/notes/{id}`     | Заметка по ID         |

### Примеры запросов notes-reader

```bash
# Список заметок
curl http://localhost:8001/notes

# Количество заметок
curl http://localhost:8001/notes/count

# Заметка по ID
curl http://localhost:8001/notes/1
```

### Тесты notes-reader

```bash
cd reader
pip install -r requirements.txt
pytest tests/ -v
```

## М7 + М9 — Docker Compose (volumes + лимиты)

```bash
docker compose up
```

- `notes-api` — порт 8000, read-write доступ к volume `notes-data`
- `notes-reader` — порт 8001, read-only доступ к тому же volume

## Н1 — Запуск Go-сервиса (scratch)

```bash
cd go
docker build -t go-app .
docker run -p 8080:8080 go-app
```

### Эндпоинты go-service

| Метод | Путь      | Описание                            |
|-------|-----------|-------------------------------------|
| GET   | `/`       | Приветствие и список маршрутов      |
| GET   | `/ping`   | Pong с временной меткой             |
| GET   | `/health` | Статус сервиса                      |
| GET   | `/info`   | Hostname, Go version, OS, arch      |

### Примеры запросов go-service

```bash
curl http://localhost:8080/
curl http://localhost:8080/ping
curl http://localhost:8080/health
curl http://localhost:8080/info
```

### Тесты

```bash
cd go
go test ./... -v
```

## Н7 — Запуск Python + Rust

```bash
cd python-rust
docker build -t py-rust-app .
docker run -p 8002:8002 py-rust-app
```

### Эндпоинты python-rust

| Метод | Путь             | Описание                            |
|-------|------------------|-------------------------------------|
| GET   | `/`              | Приветствие и список маршрутов      |
| GET   | `/word-count`    | Подсчёт слов (Rust)                 |
| GET   | `/reverse`       | Переворот строки (Rust)             |
| GET   | `/palindrome`    | Проверка палиндрома (Rust)          |
| GET   | `/fibonacci`     | Числа Фибоначчи (Rust)              |

### Примеры запросов python-rust

```bash
# Подсчёт слов
curl "http://localhost:8002/word-count?text=hello+world"

# Переворот строки
curl "http://localhost:8002/reverse?text=hello"

# Проверка палиндрома
curl "http://localhost:8002/palindrome?text=racecar"

# Числа Фибоначчи
curl "http://localhost:8002/fibonacci?n=7"
```

### Локальный запуск тестов

```bash
cd python-rust
maturin build --release
pip install target/wheels/*.whl
pip install -r requirements.txt
pytest app/tests/ -v
```
