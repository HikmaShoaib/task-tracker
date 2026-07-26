# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Setup (Windows PowerShell):
```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Run the API:
```
uvicorn app.main:app --reload
```
Starts on http://127.0.0.1:8000; Swagger UI at /docs; health check at GET /health.

Run tests:
```
pytest tests/test_tasks.py -v
```

Run a single test:
```
pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body -v
```

Run the frontend: open `frontend/index.html` with VS Code's Live Server extension (http://127.0.0.1:5500) while the backend is running — CORS in `app/main.py` is hardcoded to allow that origin plus 127.0.0.1/localhost:8000.

## Architecture

This is a Module 1-4 learning project (FastAPI + Pydantic) with an intentionally minimal, layered structure:

- `app/models.py` — the actual source of truth for domain types: `TaskStatus`/`TaskPriority` enums and the `TaskCreate`/`TaskUpdate`/`TaskResponse` Pydantic models (all `extra="forbid"`). Title validation (strip, non-blank, ≤200 chars) lives here as field validators, duplicated across `TaskCreate` and `TaskUpdate`.
- `app/storage.py` — the actual in-memory repository: a module-level `_tasks: dict[str, TaskResponse]` plus CRUD functions and filtering/sorting for `GET /tasks`. Tasks sort by `created_at`. `_reset()` clears state and is called by the `_reset_storage` autouse fixture in `tests/conftest.py` between tests.
- `app/business_rules.py` — status-transition validation (`validate_status_transition`). Allowed transitions: ToDo→InProgress, InProgress→Done, Done→InProgress. Same-status and any other transition raises HTTP 422.
- `app/main.py` — FastAPI app instance, CORS middleware, and all route handlers (`/health`, `/tasks` CRUD). Route handlers call into `storage` and `business_rules` directly; there's no separate service layer.
- **`app/schemas.py`, `app/repository.py`, `app/exceptions.py` are empty placeholder stubs** (docstring only) — despite the names, they are not where schemas/repository/exception logic actually lives. Don't assume code is missing just because these files are empty; check `models.py`/`storage.py`/`main.py` (and inline `HTTPException` calls) first.

### Key domain behavior
- **Overdue is computed, never stored**: `is_overdue` is derived on every read/write from `due_date < today() and status != Done` (see `storage._compute_is_overdue`). There is no background job and no stored overdue flag — this was a deliberate ADR decision (see `docs/midcourse/mini-adr.md`).
- **Tags** are a bare `list[str]` on the task, no separate Tag entity. Filter via `GET /tasks?tag=...`.
- Data is in-memory only and resets on every app restart (and between tests via the autouse fixture) — this is an accepted Module 1 trade-off, not a bug.

### Docs
`docs/midcourse/` contains the assignment paper trail for the `mid-course-project` branch: `mini-adr.md` (design decisions for tags/due-dates/filtering), `user-stories.md`, `verification.md`, `prompt-log.md`, `reflection.md`. Check `mini-adr.md` before changing overdue/tag/filtering behavior — it documents why simpler alternatives were rejected.
