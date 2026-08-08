# Task Tracker Architecture

## What the app does

Task Tracker is a Python/FastAPI learning application that provides a REST API and static Kanban-style frontend for creating, listing, filtering, retrieving, partially updating, and deleting tasks. It also exposes a health endpoint.

## Data model

The main entity is a **Task**, with a generated UUID identifier, title, description, status, priority, assignee, tags, due date, creation/update timestamps, and derived `is_overdue` value.

- Status: `ToDo`, `InProgress`, or `Done`
- Priority: `Low`, `Medium`, or `High`
- Defaults: empty description, `ToDo`, `Medium`, no assignee, no tags, and no due date
- Overdue: due date is before the current local date and status is not `Done`
- Timestamps are generated in UTC

`TaskCreate`, `TaskUpdate`, and `TaskResponse` define the creation, partial-update, and response representations.

## Request flow: creating a task

1. A client, including the static frontend, sends a task-creation request to the FastAPI backend.
2. FastAPI validates the request using `TaskCreate`; extra fields are forbidden, and the required title is trimmed and checked for blank content and a maximum length of 200 characters.
3. The route handler in `app/main.py` passes the validated data to the active in-memory storage implementation.
4. Storage applies defaults, generates the UUID and timestamps, calculates `is_overdue`, and adds the task to the module-level `_tasks` dictionary.
5. The API returns the created task using the response model. The task remains available only for the lifetime of the process.

## Key files

- `AGENTS.md` — Repository architecture, confirmed behavior, commands, and Module 5 governance rules.
- `app/main.py` — FastAPI app, CORS middleware, health endpoint, and task route handlers.
- `app/models.py` — Task request/response models, enums, defaults, and title validation.
- `app/storage.py` — Active in-memory CRUD, filtering, sorting, and overdue calculation.
- `app/business_rules.py` — Permitted task-status transitions.
- `frontend/index.html` — Static Kanban frontend and backend fetch calls.
- `tests/test_tasks.py` — API behavior tests, including known limitations.
- `tests/conftest.py` — Test client fixture and per-test storage reset.
- `docs/midcourse/mini-adr.md` — Design decisions for tags, due dates, overdue behavior, and filtering.

## Conventions

- **Validation:** Pydantic models are the source of truth. Titles are trimmed and validated; extra request fields are rejected.
- **Storage:** Tasks are held in a module-level dictionary without a database and are lost on restart.
- **Updates:** `PATCH` changes only explicitly supplied fields. Status changes follow the transitions `ToDo → InProgress → Done → InProgress`.
- **Errors:** Unknown task IDs return HTTP 404. Invalid status transitions return HTTP 422.
- **Queries:** Exact status, priority, tag-membership, and overdue filters combine with AND; results sort by `created_at` ascending.
- **Frontend/backend:** The static HTML/JavaScript frontend calls the API at `http://127.0.0.1:8000`; CORS is configured in the FastAPI application.

## Not visible or assumptions

No service layer, database, authentication system, background overdue recalculation, production deployment workflow, tag normalization, or case-insensitive tag matching is confirmed. The minimum supported Python version is also not confirmed. `app/schemas.py`, `app/repository.py`, and `app/exceptions.py` are placeholder stubs and should not be treated as active architecture. Runtime behavior and test success were not independently verified for this draft.
