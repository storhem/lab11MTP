from fastapi import FastAPI, HTTPException
from typing import List

app = FastAPI()

notes = []
next_id = 1

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
    return note

@app.delete("/notes/{note_id}", response_model=dict)
def delete_note(note_id: int):
    global notes
    note = next((n for n in notes if n["id"] == note_id), None)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    notes = [n for n in notes if n["id"] != note_id]
    return {"message": "Заметка удалена", "id": note_id}
