import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import restnotes
from restnotes import app
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=True)


@pytest.fixture(autouse=True)
def reset_notes(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_FILE", str(tmp_path / "notes.json"))
    restnotes.notes.clear()
    restnotes.next_id = 1
    yield
    restnotes.notes.clear()
    restnotes.next_id = 1


# ── Базовые эндпоинты ─────────────────────────────────────────────────────────

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_notes_empty():
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_get_notes_returns_list():
    response = client.get("/notes")
    assert isinstance(response.json(), list)


# ── Создание заметок ─────────────────────────────────────────────────────────

def test_add_note():
    response = client.post("/notes", params={"text": "Тестовая заметка"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["text"] == "Тестовая заметка"


def test_add_note_returns_correct_structure():
    response = client.post("/notes", params={"text": "Структура"})
    assert set(response.json().keys()) == {"id", "text"}


def test_add_multiple_notes_count():
    client.post("/notes", params={"text": "Первая"})
    client.post("/notes", params={"text": "Вторая"})
    response = client.get("/notes")
    assert len(response.json()) == 2


def test_add_note_with_long_text():
    long_text = "А" * 1000
    response = client.post("/notes", params={"text": long_text})
    assert response.status_code == 200
    assert response.json()["text"] == long_text


def test_add_note_with_special_characters():
    text = "Заметка: !@#$%^&*()_+"
    response = client.post("/notes", params={"text": text})
    assert response.status_code == 200
    assert response.json()["text"] == text


# ── Получение заметки по ID ──────────────────────────────────────────────────

def test_get_note_by_id():
    client.post("/notes", params={"text": "Моя заметка"})
    response = client.get("/notes/1")
    assert response.status_code == 200
    assert response.json()["text"] == "Моя заметка"


def test_get_note_not_found():
    response = client.get("/notes/999")
    assert response.status_code == 404


def test_get_note_not_found_detail():
    response = client.get("/notes/42")
    assert "detail" in response.json()


def test_get_multiple_notes_by_id():
    texts = ["Alpha", "Beta", "Gamma"]
    for t in texts:
        client.post("/notes", params={"text": t})
    for i, t in enumerate(texts, start=1):
        response = client.get(f"/notes/{i}")
        assert response.status_code == 200
        assert response.json()["text"] == t


# ── Удаление заметок ─────────────────────────────────────────────────────────

def test_delete_note():
    client.post("/notes", params={"text": "Удаляемая"})
    response = client.delete("/notes/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert client.get("/notes").json() == []


def test_delete_note_not_found():
    response = client.delete("/notes/999")
    assert response.status_code == 404


def test_delete_note_not_found_detail():
    response = client.delete("/notes/42")
    assert "detail" in response.json()


def test_delete_one_of_many():
    client.post("/notes", params={"text": "Первая"})
    client.post("/notes", params={"text": "Вторая"})
    client.post("/notes", params={"text": "Третья"})
    client.delete("/notes/2")
    ids = [n["id"] for n in client.get("/notes").json()]
    assert 2 not in ids
    assert len(ids) == 2


def test_get_deleted_note_returns_404():
    client.post("/notes", params={"text": "Заметка"})
    client.delete("/notes/1")
    assert client.get("/notes/1").status_code == 404


# ── ID-инкремент ─────────────────────────────────────────────────────────────

def test_ids_increment():
    client.post("/notes", params={"text": "Первая"})
    client.post("/notes", params={"text": "Вторая"})
    ids = [n["id"] for n in client.get("/notes").json()]
    assert ids == [1, 2]


def test_ids_continue_after_delete():
    client.post("/notes", params={"text": "Первая"})
    client.delete("/notes/1")
    client.post("/notes", params={"text": "Вторая"})
    assert client.get("/notes").json()[0]["id"] == 2


# ── Персистентность (volume) ─────────────────────────────────────────────────

def test_save_creates_file(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    monkeypatch.setenv("NOTES_FILE", str(path))
    client.post("/notes", params={"text": "Сохранить"})
    assert path.exists()


def test_persistence_survives_reload(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    monkeypatch.setenv("NOTES_FILE", str(path))
    client.post("/notes", params={"text": "Заметка"})
    # эмулируем перезапуск контейнера: сбрасываем память и перечитываем файл
    restnotes.notes.clear()
    restnotes.next_id = 1
    restnotes._load()
    assert len(restnotes.notes) == 1
    assert restnotes.notes[0]["text"] == "Заметка"


def test_persistence_delete_survives_reload(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    monkeypatch.setenv("NOTES_FILE", str(path))
    client.post("/notes", params={"text": "Первая"})
    client.post("/notes", params={"text": "Вторая"})
    client.delete("/notes/1")
    restnotes.notes.clear()
    restnotes.next_id = 1
    restnotes._load()
    assert len(restnotes.notes) == 1
    assert restnotes.notes[0]["id"] == 2


def test_file_contains_valid_json(tmp_path, monkeypatch):
    import json
    path = tmp_path / "notes.json"
    monkeypatch.setenv("NOTES_FILE", str(path))
    client.post("/notes", params={"text": "JSON-тест"})
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "notes" in data
    assert "next_id" in data
    assert data["notes"][0]["text"] == "JSON-тест"


def test_load_from_existing_file(tmp_path, monkeypatch):
    import json
    path = tmp_path / "notes.json"
    path.write_text(
        json.dumps({"notes": [{"id": 5, "text": "Из файла"}], "next_id": 6}),
        encoding="utf-8",
    )
    monkeypatch.setenv("NOTES_FILE", str(path))
    restnotes.notes.clear()
    restnotes.next_id = 1
    restnotes._load()
    assert restnotes.notes[0]["text"] == "Из файла"
    assert restnotes.next_id == 6
