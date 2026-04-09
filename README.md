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
│   ├── main.go
│   ├── main_test.go
│   ├── go.mod
│   └── Dockerfile
├── python-rust/              # Н7 — Python + Rust расширение
│   ├── src/
│   ├── app/
│   ├── Cargo.toml
│   ├── pyproject.toml
│   └── Dockerfile
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

## Н7 — Запуск Python + Rust

```bash
cd python-rust
docker build -t py-rust-app .
docker run -p 8002:8002 py-rust-app
```
