# FastAPI + Postgres CRUD

![CI](https://github.com/Auth3nticAI/fastapi-postgres-crud/actions/workflows/ci.yml/badge.svg)

> A clean FastAPI/SQLAlchemy/Postgres reference — `database.py` / `models.py` / `schemas.py` / `main.py` split, Pydantic validation at the boundary, full CRUD over a `books` resource. Data persists across server restarts via a Docker named volume.

![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.13-E92063?style=flat&logo=pydantic&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)

UI repo: [nextjs-fullstack-crud-ui](https://github.com/Auth3nticAI/nextjs-fullstack-crud-ui)

---

![data persists across server restart](screenshots/persistence-proof.png)

## What's interesting

- **File split that scales** — engine + session + `get_db` dependency in `database.py`, ORM in `models.py`, request/response shapes in `schemas.py`, routes in `main.py`. Each file does one thing.
- **`Depends(get_db)`** on every endpoint — per-request session lifecycle, closes cleanly via `try/yield/finally`.
- **`from_attributes: True`** on the Pydantic response models so SQLAlchemy rows serialize without manual copying.
- **CORS configured** for the Next.js frontend so the browser actually sees the JSON.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/books` | List (filter by `?status=`) |
| `POST` | `/books` | Create |
| `GET` | `/books/stats` | Aggregate counts + average rating |
| `GET` | `/books/{id}` | Read one |
| `PUT` | `/books/{id}` | Partial update (status, rating) |
| `DELETE` | `/books/{id}` | Delete |

## Run

```bash
docker compose up -d db
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cat > .env <<EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/booktracker
EOF

uvicorn main:app --reload
```

Swagger: http://localhost:8000/docs

![Swagger UI showing all routes](screenshots/swagger-docs.png)

## Layout

```
.
├── main.py             # FastAPI routes
├── database.py         # Engine, SessionLocal, Base, get_db dependency
├── models.py           # SQLAlchemy ORM (Book)
├── schemas.py          # Pydantic — BookCreate, BookUpdate, BookResponse
├── docker-compose.yml  # Postgres + (optional) backend service
└── requirements.txt
```

## Background

Built as the Week 4 lab for **CSE552 — Fullstack Software Development in the Age of AI Agents**. Same domain extended with AI in later weeks ([claude-rag-recommendations](https://github.com/Auth3nticAI/claude-rag-recommendations), [claude-tool-use-agent](https://github.com/Auth3nticAI/claude-tool-use-agent)) and capstoned at [book-tracker-ai](https://github.com/Auth3nticAI/book-tracker-ai).
