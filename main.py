from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Book
from schemas import BookCreate, BookResponse, BookUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Tracker API", version="2.0.0")


@app.get("/")
def read_root():
    return {"message": "Welcome to Book Tracker API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/books", response_model=list[BookResponse])
def get_books(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Book)
    if status:
        query = query.filter(Book.status == status)
    return query.all()


@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


# Literal route must come before the dynamic /books/{book_id},
# otherwise FastAPI matches "stats" as a book_id and 422s on int parsing.
@app.get("/books/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Book).count()

    by_status_rows = (
        db.query(Book.status, func.count(Book.id))
        .group_by(Book.status)
        .all()
    )
    by_status = {status: count for status, count in by_status_rows}

    rated_query = db.query(Book).filter(
        Book.status == "read", Book.rating.isnot(None)
    )
    rated_count = rated_query.count()
    avg = (
        db.query(func.avg(Book.rating))
        .filter(Book.status == "read", Book.rating.isnot(None))
        .scalar()
    )
    average_rating = round(float(avg), 2) if avg is not None else None

    return {
        "total": total,
        "by_status": by_status,
        "average_rating": average_rating,
        "rated_count": rated_count,
    }


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updates: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    if updates.status is not None:
        book.status = updates.status
    if updates.rating is not None:
        book.rating = updates.rating

    db.commit()
    db.refresh(book)
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    title = book.title
    db.delete(book)
    db.commit()
    return {"message": f"Deleted '{title}'", "id": book_id}
