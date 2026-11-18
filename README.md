# Task Manager API

A REST API for managing tasks, built with **FastAPI** and **SQLite**. Supports full CRUD, filtering, search, pagination and input validation, with automated tests.

## Features

- Create, read, update (partial) and delete tasks
- Filter by `status` and `priority`, search by title, paginate with `limit` / `offset`
- Request validation with Pydantic (invalid input returns `422`)
- Parameterised SQL queries (no string-built user input)
- Auto-generated interactive docs at `/docs`
- Isolated pytest suite using a temporary database

## Project structure

```
task-manager-api/
├── app/
│   ├── main.py       # routes
│   ├── database.py   # SQLite connection + schema
│   └── schemas.py    # Pydantic models and enums
├── tests/test_api.py
├── requirements.txt
└── pytest.ini
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the server

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try the endpoints in your browser.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List tasks (`status`, `priority`, `search`, `limit`, `offset`) |
| GET | `/tasks/{id}` | Get one task |
| PATCH | `/tasks/{id}` | Update only the fields you send |
| DELETE | `/tasks/{id}` | Delete a task |

### Example

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Finish DSA sheet", "priority": "high", "due_date": "2026-12-01"}'

curl "http://127.0.0.1:8000/tasks?priority=high&status=todo"
```

## Run tests

```bash
pytest
```

## Ideas for extending it

- Add user accounts and JWT authentication
- Switch to PostgreSQL with SQLAlchemy
- Add a Dockerfile and GitHub Actions workflow
- Deploy to Render or Railway
