import json
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "python"))

from reader import app
from fastapi.testclient import TestClient

client = TestClient(app)


def write_notes_file(path, notes, next_id=None):
    data = {"notes": notes, "next_id": next_id or (max((n["id"] for n in notes), default=0) + 1)}
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


@pytest.fixture(autouse=True)
def set_notes_file(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_FILE", str(tmp_path / "notes.json"))
    yield tmp_path / "notes.json"


# ── Root ─────────────────────────────────────────────────────────────────────

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# ── GET /notes ────────────────────────────────────────────────────────────────

def test_get_notes_no_file():
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_get_notes_empty_file(set_notes_file):
    write_notes_file(set_notes_file, [])
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_get_notes_returns_list(set_notes_file):
    write_notes_file(set_notes_file, [{"id": 1, "text": "Заметка"}])
    response = client.get("/notes")
    assert isinstance(response.json(), list)


def test_get_notes_one_note(set_notes_file):
    write_notes_file(set_notes_file, [{"id": 1, "text": "Первая"}])
    response = client.get("/notes")
    assert len(response.json()) == 1
    assert response.json()[0]["text"] == "Первая"


def test_get_notes_multiple(set_notes_file):
    notes = [{"id": i, "text": f"Заметка {i}"} for i in range(1, 6)]
    write_notes_file(set_notes_file, notes)
    response = client.get("/notes")
    assert len(response.json()) == 5


# ── GET /notes/{id} ───────────────────────────────────────────────────────────

def test_get_note_by_id(set_notes_file):
    write_notes_file(set_notes_file, [{"id": 3, "text": "Нужная"}])
    response = client.get("/notes/3")
    assert response.status_code == 200
    assert response.json()["text"] == "Нужная"


def test_get_note_not_found_empty():
    response = client.get("/notes/1")
    assert response.status_code == 404


def test_get_note_not_found_wrong_id(set_notes_file):
    write_notes_file(set_notes_file, [{"id": 1, "text": "Есть"}])
    response = client.get("/notes/99")
    assert response.status_code == 404


def test_get_note_not_found_has_detail(set_notes_file):
    write_notes_file(set_notes_file, [])
    response = client.get("/notes/1")
    assert "detail" in response.json()


# ── GET /notes/count ──────────────────────────────────────────────────────────

def test_count_no_file():
    response = client.get("/notes/count")
    assert response.status_code == 200
    assert response.json()["count"] == 0


def test_count_with_notes(set_notes_file):
    write_notes_file(set_notes_file, [{"id": 1, "text": "А"}, {"id": 2, "text": "Б"}])
    response = client.get("/notes/count")
    assert response.json()["count"] == 2


# ── Обмен через volume (интеграционный сценарий) ─────────────────────────────

def test_reader_sees_data_written_by_api(tmp_path, monkeypatch):
    """Читатель видит данные, записанные notes-api в тот же файл."""
    import restnotes
    path = tmp_path / "shared.json"
    monkeypatch.setenv("NOTES_FILE", str(path))

    # notes-api пишет заметку
    restnotes.notes.clear()
    restnotes.next_id = 1
    # Записываем напрямую через _save
    restnotes.notes.append({"id": 1, "text": "Из API"})
    restnotes.next_id = 2
    restnotes._save()

    # reader читает из того же файла
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json()[0]["text"] == "Из API"


def test_reader_count_matches_api_data(tmp_path, monkeypatch):
    """Счётчик reader совпадает с количеством заметок, записанных API."""
    import restnotes
    path = tmp_path / "shared.json"
    monkeypatch.setenv("NOTES_FILE", str(path))

    restnotes.notes.clear()
    restnotes.next_id = 1
    for i in range(3):
        restnotes.notes.append({"id": i + 1, "text": f"Заметка {i + 1}"})
    restnotes.next_id = 4
    restnotes._save()

    response = client.get("/notes/count")
    assert response.json()["count"] == 3
