from fastapi import FastAPI, HTTPException
import texttools

app = FastAPI(
    title="Python + Rust Extension",
    description="FastAPI-приложение с вычислительным модулем на Rust (PyO3/maturin)",
)


@app.get("/")
def root():
    return {
        "message": "Python + Rust extension service. Документация: /docs",
        "routes": "GET /word-count  GET /reverse  GET /palindrome  GET /fibonacci",
    }


@app.get("/word-count")
def word_count(text: str):
    return {"text": text, "count": texttools.word_count(text)}


@app.get("/reverse")
def reverse(text: str):
    return {"text": text, "reversed": texttools.reverse_string(text)}


@app.get("/palindrome")
def palindrome(text: str):
    return {"text": text, "is_palindrome": texttools.is_palindrome(text)}


@app.get("/fibonacci")
def fibonacci(n: int):
    if n < 0:
        raise HTTPException(status_code=422, detail="n должно быть >= 0")
    return {"n": n, "sequence": texttools.fibonacci(n)}
