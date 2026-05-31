# Book Tracker API — Week 4

Backend for the Book Tracker app. Upgrade from Week 3's in-memory Python list to a real Postgres-backed service.

## Stack

- **FastAPI** for the HTTP layer
- **SQLAlchemy** ORM
- **PostgreSQL 16** via Docker Compose
- **Pydantic** for request/response validation
- `python-dotenv` for env loading

## Layout

```
.
├── main.py            # FastAPI app + route handlers
├── database.py        # Engine, SessionLocal, Base, get_db dependency
├── models.py          # SQLAlchemy ORM models
├── schemas.py         # Pydantic request/response schemas
├── docker-compose.yml # Postgres service
└── requirements.txt
```

## Run

```bash
# 1. Start Postgres
docker compose up -d db

# 2. Activate venv and start the API
source venv/bin/activate
uvicorn main:app --reload
```

Open http://localhost:8000/docs for the Swagger UI.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/books` | List all books (filter by `?status=`) |
| POST | `/books` | Create a book |
| GET | `/books/stats` | Aggregate stats (count, by status, avg rating) |
| GET | `/books/{id}` | Read one book |
| PUT | `/books/{id}` | Update status / rating |
| DELETE | `/books/{id}` | Delete a book |

## Environment

Create `.env` (gitignored):

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/booktracker
```
