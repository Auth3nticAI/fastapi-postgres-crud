from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Book Tracker API", version="1.0.0")


class BookCreate(BaseModel):
    title: str
    author: str
    status: str = "want_to_read"  # "reading", "read", "want_to_read"
    rating: Optional[int] = None  # 1-5, only if status is "read"


class BookUpdate(BaseModel):
    status: Optional[str] = None
    rating: Optional[int] = None


books_db: list[dict] = []
next_id = 1


@app.get("/")
def read_root():
    return {"message": "Welcome to Book Tracker API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/books")
def get_books(status: Optional[str] = None):
    if status:
        return [b for b in books_db if b["status"] == status]
    return books_db


@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    global next_id
    new_book = {"id": next_id, **book.model_dump()}
    books_db.append(new_book)
    next_id += 1
    return new_book


# Literal route must come before the dynamic /books/{book_id},
# otherwise FastAPI matches "stats" as a book_id and 422s on int parsing.
@app.get("/books/stats")
def get_stats():
    total = len(books_db)
    by_status: dict[str, int] = {}
    for b in books_db:
        by_status[b["status"]] = by_status.get(b["status"], 0) + 1

    rated = [b["rating"] for b in books_db if b["status"] == "read" and b["rating"] is not None]
    average_rating = round(sum(rated) / len(rated), 2) if rated else None

    return {
        "total": total,
        "by_status": by_status,
        "average_rating": average_rating,
        "rated_count": len(rated),
    }


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for b in books_db:
        if b["id"] == book_id:
            return b
    raise HTTPException(status_code=404, detail="Book not found")


@app.put("/books/{book_id}")
def update_book(book_id: int, updates: BookUpdate):
    for b in books_db:
        if b["id"] == book_id:
            if updates.status is not None:
                b["status"] = updates.status
            if updates.rating is not None:
                b["rating"] = updates.rating
            return b
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for i, b in enumerate(books_db):
        if b["id"] == book_id:
            removed = books_db.pop(i)
            return {"message": f"Deleted '{removed['title']}'", "id": book_id}
    raise HTTPException(status_code=404, detail="Book not found")
