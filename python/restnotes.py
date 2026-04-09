import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import List

notes = []
next_id = 1


def get_notes_file() -> str:
    return os.environ.get("NOTES_FILE", "/data/notes.json")


def _load() -> None:
    global notes, next_id
    path = get_notes_file()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            notes[:] = data.get("notes", [])
            next_id = data.get("next_id", 1)


def _save() -> None:
    path = get_notes_file()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"notes": notes, "next_id": next_id}, f, ensure_ascii=False, indent=2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "API для заметок. Документация: /docs"}


@app.get("/notes", response_model=List[dict])
def get_notes():
    return notes


@app.get("/notes/{note_id}", response_model=dict)
def get_note(note_id: int):
    note = next((n for n in notes if n["id"] == note_id), None)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return note


@app.post("/notes", response_model=dict)
def add_note(text: str):
    global next_id
    note = {"id": next_id, "text": text}
    notes.append(note)
    next_id += 1
    _save()
    return note


@app.delete("/notes/{note_id}", response_model=dict)
def delete_note(note_id: int):
    global notes
    note = next((n for n in notes if n["id"] == note_id), None)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    notes = [n for n in notes if n["id"] != note_id]
    _save()
    return {"message": "Заметка удалена", "id": note_id}
