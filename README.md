# Лабораторная работа №11 — Контейнеризация мультиязычных приложений

Цель: освоить упаковку в контейнеры приложений на Python, Go и Rust, оптимизировать размер образов.

## Задания

| Код | Сложность | Описание |
|-----|-----------|----------|
| М1  | Средняя   | Dockerfile для Python-приложения (FastAPI) |
| М7  | Средняя   | Volume для обмена данными между контейнерами |
| М9  | Средняя   | Ограничение ресурсов (CPU, память) |
| Н1  | Повышенная | Go-приложение со статической компиляцией в scratch-образе |
| Н7  | Повышенная | Multi-stage сборка Python-приложения с Rust-расширением |

## Структура репозитория

```
.
├── python/             # М1 — FastAPI приложение
│   ├── restnotes.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│       └── test_notes.py
├── go/                 # Н1 — Go приложение (scratch-образ)
│   ├── main.go
│   ├── main_test.go
│   ├── go.mod
│   └── Dockerfile
├── python-rust/        # Н7 — Python + Rust расширение
│   ├── src/
│   ├── Cargo.toml
│   ├── pyproject.toml
│   └── Dockerfile
├── docker-compose.yml  # М7, М9 — оркестрация, volumes, лимиты
├── .gitignore
├── README.md
└── PROMPT_LOG.md
```

## М1 — Python (FastAPI)

REST API для управления заметками.

### Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Приветствие |
| GET | `/notes` | Список всех заметок |
| GET | `/notes/{id}` | Заметка по ID |
| POST | `/notes?text=...` | Создать заметку |
| DELETE | `/notes/{id}` | Удалить заметку |

### Запуск

```bash
cd python
docker build -t notes-api .
docker run -p 8000:8000 notes-api
```

API доступен на `http://localhost:8000`, документация — `http://localhost:8000/docs`.

### Тесты

```bash
cd python
pip install -r requirements.txt
pytest tests/ -v
```

## М7 + М9 — Docker Compose

```bash
docker compose up
```

## Н1 — Go (scratch-образ)

```bash
cd go
docker build -t go-app .
docker run -p 8080:8080 go-app
```

## Н7 — Python + Rust расширение

```bash
cd python-rust
docker build -t py-rust-app .
docker run -p 8001:8001 py-rust-app
```
