# Task Tracker Architecture

## 1. What the app does

Task Tracker is a learning-oriented FastAPI application that exposes REST endpoints to create, list, filter, retrieve, partially update, and delete tasks, plus a health endpoint. A static Kanban frontend displays tasks by status and communicates with the API over HTTP.

## 2. Data model

The only active entity is **Task**. Important fields are: UUID string `id`; required `title`; optional `description`, `assignee`, `tags`, and `due_date`; enumerated `status` (`ToDo`, `InProgress`, `Done`); enumerated `priority` (`Low`, `Medium`, `High`); derived `is_overdue`; and UTC `created_at` and `updated_at` timestamps. New tasks default to `ToDo`, `Medium` priority, an empty description and tag list, and no assignee or due date. Tags are plain strings rather than separate entities.

## 3. Request flow

1. The frontend submits JSON to `POST /tasks`, or another client calls the endpoint directly.
2. FastAPI parses the request into `TaskCreate`; Pydantic rejects missing, blank, oversized, incorrectly typed, or extra fields.
3. The route handler delegates directly to `storage.add_task`.
4. Storage generates a UUID and UTC timestamps, calculates overdue state from the local date, due date, and status, then places a `TaskResponse` in the module-level dictionary.
5. FastAPI serializes the task as the response body with HTTP 201. The frontend closes its form and reloads `GET /tasks` to redraw the board.

## 4. Key files

- `app/main.py` — FastAPI setup, CORS policy, health check, and all API route handlers.
- `app/models.py` — Request/response models, enums, defaults, and title validation.
- `app/storage.py` — Module-level task dictionary, CRUD operations, filtering, sorting, and overdue calculation.
- `app/business_rules.py` — Permitted task-status transitions and HTTP 422 rejection.
- `frontend/index.html` — Static Kanban interface and browser-side API calls.
- `tests/test_tasks.py` — API behavior tests for CRUD, validation, transitions, tags, and due dates.
- `tests/conftest.py` — Test client and automatic storage reset around each test.
- `docs/midcourse/mini-adr.md` — Recorded design decisions for tags, due dates, and filtering.
- `README.md` — Supported setup, operation, structure, and known limitations.

## 5. Conventions

Validation is performed primarily by Pydantic models: extra request fields are forbidden, titles are trimmed and limited to 200 characters, and enums constrain status and priority. Status changes additionally follow an explicit transition table. Storage is process-local and in memory, so tasks disappear on restart. Invalid request data and status transitions produce HTTP 422; route handlers return HTTP 404 for unknown IDs. There are no active custom exception handlers. The frontend uses `fetch` against a hardcoded `http://localhost:8000` base URL, while the backend permits a fixed set of local development origins through CORS.

## 6. Not visible or assumptions

No authentication, database, service layer, production deployment topology, or background processing is visible. The minimum supported Python version is not confirmed beyond Python 3.11 in CI and Docker. The ADR describes overdue state as computed on read, but current code calculates and stores it only when a task is created or updated; therefore it may become stale as the date changes. Placeholder files named `schemas.py`, `repository.py`, and `exceptions.py` do not contain active implementations.
