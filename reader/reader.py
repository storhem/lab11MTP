import json
import os
from fastapi import FastAPI, HTTPException
from typing import List

app = FastAPI(title="Notes Reader", description="Read-only доступ к заметкам из shared volume")

def _read_notes() -> List[dict]:
    path = os.environ.get("NOTES_FILE", "/data/notes.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("notes", [])


@app.get("/")
def root():
    return {"message": "Notes Reader — read-only API. Документация: /docs"}


@app.get("/notes", response_model=List[dict])
def get_notes():
    return _read_notes()


@app.get("/notes/count", response_model=dict)
def count_notes():
    return {"count": len(_read_notes())}


@app.get("/notes/{note_id}", response_model=dict)
def get_note(note_id: int):
    note = next((n for n in _read_notes() if n["id"] == note_id), None)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return note
