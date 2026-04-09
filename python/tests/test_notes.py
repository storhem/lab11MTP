import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import restnotes
from restnotes import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_notes():
    restnotes.notes.clear()
    restnotes.next_id = 1
    yield


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_notes_empty():
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_add_note():
    response = client.post("/notes", params={"text": "Тестовая заметка"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["text"] == "Тестовая заметка"


def test_add_note_returns_correct_structure():
    response = client.post("/notes", params={"text": "Структура"})
    data = response.json()
    assert set(data.keys()) == {"id", "text"}


def test_get_notes_after_add():
    client.post("/notes", params={"text": "Заметка 1"})
    client.post("/notes", params={"text": "Заметка 2"})
    response = client.get("/notes")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_notes_returns_list():
    response = client.get("/notes")
    assert isinstance(response.json(), list)


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


def test_delete_note():
    client.post("/notes", params={"text": "Удаляемая заметка"})
    response = client.delete("/notes/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

    response = client.get("/notes")
    assert response.json() == []


def test_delete_note_not_found():
    response = client.delete("/notes/999")
    assert response.status_code == 404


def test_delete_note_not_found_detail():
    response = client.delete("/notes/42")
    assert "detail" in response.json()


def test_ids_increment():
    client.post("/notes", params={"text": "Первая"})
    client.post("/notes", params={"text": "Вторая"})
    response = client.get("/notes")
    ids = [n["id"] for n in response.json()]
    assert ids == [1, 2]


def test_ids_continue_after_delete():
    client.post("/notes", params={"text": "Первая"})
    client.delete("/notes/1")
    client.post("/notes", params={"text": "Вторая"})
    response = client.get("/notes")
    assert response.json()[0]["id"] == 2


def test_add_multiple_notes_and_get_each():
    texts = ["Alpha", "Beta", "Gamma"]
    for t in texts:
        client.post("/notes", params={"text": t})
    for i, t in enumerate(texts, start=1):
        response = client.get(f"/notes/{i}")
        assert response.status_code == 200
        assert response.json()["text"] == t


def test_delete_one_of_many():
    client.post("/notes", params={"text": "Первая"})
    client.post("/notes", params={"text": "Вторая"})
    client.post("/notes", params={"text": "Третья"})
    client.delete("/notes/2")
    response = client.get("/notes")
    ids = [n["id"] for n in response.json()]
    assert 2 not in ids
    assert len(ids) == 2


def test_get_deleted_note_returns_404():
    client.post("/notes", params={"text": "Заметка"})
    client.delete("/notes/1")
    response = client.get("/notes/1")
    assert response.status_code == 404


def test_add_note_with_long_text():
    long_text = "А" * 1000
    response = client.post("/notes", params={"text": long_text})
    assert response.status_code == 200
    assert response.json()["text"] == long_text


def test_add_note_with_special_characters():
    text = "Заметка с символами: !@#$%^&*()_+"
    response = client.post("/notes", params={"text": text})
    assert response.status_code == 200
    assert response.json()["text"] == text
