# Task API

A CRUD API for managing a to-do list, built with FastAPI. **Data persists across server restarts.**

## A2: SQLite (Local Development)

A CRUD API built with FastAPI and SQLite. Supports creating, reading, updating, and deleting tasks.

### Why SQLite?

SQLite is a lightweight, serverless database stored in a single file. No installation or setup required — it creates itself on first run. Tasks survive server restarts because they're saved to disk, not kept in memory.

### How to run

```bash
py main.py
```

Server runs at `http://localhost:8000`. The database file `tasks.db` is created automatically in your project folder.

### Database

- **File:** `tasks.db` (created automatically on first run)
- **Table:** `tasks` with columns `id` (primary key), `title` (text), `done` (boolean)
- **Seed:** 3 example tasks inserted only on first run

---

## BE-04: Containerization & Persistence (Docker + Postgres)

Production-ready stack with Postgres in Docker. Same routes, swappable storage backend.

### Architecture

- **Repository pattern:** Abstract `TaskRepository` interface with `PostgresRepository` implementation
- Routes use dependency injection (`Depends(get_repo)`) — storage backend is swappable
- Service layer unchanged: only repository swapped from SQLite to Postgres

### Setup

1. Copy `.env.example` to `.env` (already in repo)
2. Run: `docker compose up`
3. API available at `http://localhost:8000`

### Persistence Test

```bash
# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test persistence"}'

# Verify it exists
curl http://localhost:8000/tasks

# Stop and restart everything
docker compose down
docker compose up

# Task still exists after restart
curl http://localhost:8000/tasks
```

### Files

- `main.py` — FastAPI routes (unchanged)
- `repository.py` — Abstract interface + Postgres implementation
- `Dockerfile` — Build app container
- `docker-compose.yml` — Orchestrate app + Postgres
- `.env.example` — Environment template (committed)
- `.env` — Actual secrets (gitignored)

---

## Endpoints

| Method | Path           | Description      |
|--------|----------------|------------------|
| GET    | `/tasks`       | List all tasks   |
| GET    | `/tasks/{id}`  | Get one task     |
| POST   | `/tasks`       | Create a task    |
| PUT    | `/tasks/{id}`  | Update a task    |
| DELETE | `/tasks/{id}`  | Delete a task    |

## Example SQL query

```sql
SELECT COUNT(*) FROM tasks;
```

**Result:** Returns the count of all tasks in the database.

## Screenshot

![DB Browser showing tasks.db](db-browser-screenshot.png)