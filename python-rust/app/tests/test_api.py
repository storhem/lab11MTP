"""Тесты FastAPI эндпоинтов (используют Rust-расширение texttools)."""
import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)


# ── GET / ─────────────────────────────────────────────────────────────────────

def test_root_status():
    assert client.get("/").status_code == 200

def test_root_has_message():
    assert "message" in client.get("/").json()

def test_root_has_routes():
    assert "routes" in client.get("/").json()


# ── GET /word-count ───────────────────────────────────────────────────────────

def test_word_count_two_words():
    r = client.get("/word-count", params={"text": "hello world"})
    assert r.status_code == 200
    assert r.json()["count"] == 2

def test_word_count_empty():
    r = client.get("/word-count", params={"text": ""})
    assert r.status_code == 200
    assert r.json()["count"] == 0

def test_word_count_returns_text():
    r = client.get("/word-count", params={"text": "test"})
    assert r.json()["text"] == "test"

def test_word_count_five_words():
    r = client.get("/word-count", params={"text": "one two three four five"})
    assert r.json()["count"] == 5


# ── GET /reverse ──────────────────────────────────────────────────────────────

def test_reverse_simple():
    r = client.get("/reverse", params={"text": "hello"})
    assert r.status_code == 200
    assert r.json()["reversed"] == "olleh"

def test_reverse_empty():
    r = client.get("/reverse", params={"text": ""})
    assert r.json()["reversed"] == ""

def test_reverse_returns_original():
    r = client.get("/reverse", params={"text": "abc"})
    assert r.json()["text"] == "abc"

def test_reverse_double_reverse():
    text = "python"
    r1 = client.get("/reverse", params={"text": text})
    reversed_text = r1.json()["reversed"]
    r2 = client.get("/reverse", params={"text": reversed_text})
    assert r2.json()["reversed"] == text


# ── GET /palindrome ───────────────────────────────────────────────────────────

def test_palindrome_true():
    r = client.get("/palindrome", params={"text": "racecar"})
    assert r.status_code == 200
    assert r.json()["is_palindrome"] is True

def test_palindrome_false():
    r = client.get("/palindrome", params={"text": "hello"})
    assert r.json()["is_palindrome"] is False

def test_palindrome_returns_text():
    r = client.get("/palindrome", params={"text": "racecar"})
    assert r.json()["text"] == "racecar"

def test_palindrome_case_insensitive():
    r = client.get("/palindrome", params={"text": "Racecar"})
    assert r.json()["is_palindrome"] is True

def test_palindrome_with_spaces():
    r = client.get("/palindrome", params={"text": "A man a plan a canal Panama"})
    assert r.json()["is_palindrome"] is True


# ── GET /fibonacci ────────────────────────────────────────────────────────────

def test_fibonacci_seven():
    r = client.get("/fibonacci", params={"n": 7})
    assert r.status_code == 200
    assert r.json()["sequence"] == [0, 1, 1, 2, 3, 5, 8]

def test_fibonacci_zero():
    r = client.get("/fibonacci", params={"n": 0})
    assert r.json()["sequence"] == []

def test_fibonacci_returns_n():
    r = client.get("/fibonacci", params={"n": 5})
    assert r.json()["n"] == 5

def test_fibonacci_length():
    r = client.get("/fibonacci", params={"n": 10})
    assert len(r.json()["sequence"]) == 10

def test_fibonacci_negative_returns_422():
    r = client.get("/fibonacci", params={"n": -1})
    assert r.status_code == 422
