# Week 4 Reflection

## 1. What is the difference between the SQLAlchemy model and the Pydantic schema?

The SQLAlchemy model (`models.Book`) describes the **database row** — column names, types, constraints, indexes. It exists so the ORM knows how to map between Python objects and Postgres tables.

The Pydantic schemas (`schemas.BookCreate`, `BookUpdate`, `BookResponse`) describe the **shape of data crossing the HTTP boundary** — what a client may send, what they may update, what they receive back. They validate request bodies and serialize responses.

They look similar because they're describing the same domain object (a Book), but they answer different questions: *how is it stored* vs. *how is it transmitted*. Keeping them separate means I can have an internal `created_at` column without exposing it in a response, or accept a partial `BookUpdate` that wouldn't be valid as a full DB insert.

## 2. What does `Depends(get_db)` do? Why does every endpoint need it?

`Depends(get_db)` is FastAPI's dependency injection — for each request, FastAPI calls `get_db()`, hands the yielded `Session` to the endpoint, and then runs the `finally:` block to close the session after the response is sent.

Every endpoint needs it because:
- Sessions are **per-request**. Sharing one global session across requests would interleave transactions and corrupt state under concurrency.
- The `try / yield / finally` pattern guarantees the connection is returned to the pool even if the endpoint raises.

It's the database equivalent of "open the file, do work, close the file" — abstracted so I never have to think about the close.

## 3. When you restarted the server and your data was still there — how does that feel compared to storing data in a Python list?

The Python-list version was a toy: every restart wiped everything, every concurrent request risked race conditions, and nothing would scale past one process. The Postgres version is the first time the API has felt like *a real system* — the data has an existence independent of the process serving it.

Architecturally, the big shift is that the API is no longer the source of truth. It's a thin layer that translates HTTP requests into SQL, with the actual state living in a separate process (Postgres) that I can query directly, back up, replicate, or connect a different frontend to. The database becomes the contract; the API becomes a view onto it.

## 4. What was the most confusing part of connecting the frontend to the backend?

_To be added in Part 2 (frontend lab)._

## 5. When does CORS become a problem and why? In your own words.

_To be added in Part 2 (frontend lab)._

## 6. What is the difference between `useEffect` with `[]` and without it?

_To be added in Part 2 (frontend lab)._
