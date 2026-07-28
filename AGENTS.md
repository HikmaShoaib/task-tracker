# AGENTS.md

This file governs Codex work in the Task Tracker repository, especially work performed for Module 5.

## Project summary

Task Tracker is a Python/FastAPI learning project developed through Modules 1–4. It exposes a REST API for creating, listing, filtering, retrieving, partially updating, and deleting tasks, plus a health endpoint. It also includes a static Kanban-style frontend.

Module 5 is about grading and governing AI-assisted coding work. It is not a feature-development module.

Repository sources:

- `README.md` describes supported setup, execution, testing, and known limitations.
- `app/main.py` contains the FastAPI application, CORS configuration, and route handlers.
- `app/models.py` defines the task models, enums, defaults, and field validation.
- `app/storage.py` implements in-memory persistence, filtering, sorting, and overdue calculation.
- `app/business_rules.py` enforces status transitions.
- `tests/` records tested API behavior.
- `frontend/index.html` contains the static frontend.

## Tech stack

Confirmed from repository files:

- Python 3.11 is used by CI and the Docker image. The actual minimum supported Python version is not confirmed.
- FastAPI
- Pydantic 2
- Uvicorn
- python-dotenv
- pytest
- HTTPX/TestClient
- Static HTML, CSS, and JavaScript frontend
- In-memory Python dictionary storage; no database
- Optional local Docker image

Dependency versions are declared as lower bounds in `requirements.txt`.

## Supported commands

Run commands from the repository root.

### Local setup on Windows PowerShell

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

These commands are documented in `README.md`. The application currently reads `PORT` when run through `python -m app.main`; use of `APP_ENV` is not confirmed in the application code.

### Run the API

```powershell
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://127.0.0.1:8000`. Swagger UI is at `/docs`, and the health endpoint is `GET /health`.

The shorter command below is also supported because Uvicorn defaults to port 8000:

```powershell
uvicorn app.main:app --reload
```

### Run tests

Run the complete test suite, matching CI:

```powershell
pytest -v
```

Run the main API test module:

```powershell
pytest tests/test_tasks.py -v
```

Run one confirmed test:

```powershell
pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body -v
```

`tests/verify_a.py` is a standalone verification script rather than a pytest test module:

```powershell
python -m tests.verify_a
```

### Run the frontend

With the API running, serve `frontend/index.html` using VS Code Live Server at `http://127.0.0.1:5500`.

No repository-provided frontend build or package-manager command is confirmed. The frontend calls the API at `http://127.0.0.1:8000`.

### Docker

The repository supports a local Docker build and run:

```powershell
docker build -t task-tracker:dev .
docker run --rm -p 8000:8000 --name tt-dev task-tracker:dev
```

No production deployment workflow is confirmed.

## Architecture and persistence

- `app/main.py` contains all route handlers; there is no confirmed service layer.
- `app/models.py` is the source of truth for request and response models.
- `app/storage.py` is the active repository implementation.
- Tasks are stored in the module-level `_tasks` dictionary and are lost when the process restarts.
- `tests/conftest.py` clears storage before and after every pytest test.
- `app/schemas.py`, `app/repository.py`, and `app/exceptions.py` are placeholder stubs. Do not infer missing behavior merely from their names.

## Mid-course documentation

`docs/midcourse/` contains the design and verification record for the mid-course project:

- `docs/midcourse/mini-adr.md` — design decisions for tags, due dates, overdue behavior, and filtering.
- `docs/midcourse/user-stories.md` — feature requirements expressed as user stories.
- `docs/midcourse/verification.md` — recorded verification work.
- `docs/midcourse/prompt-log.md` — AI-assistance prompt history.
- `docs/midcourse/reflection.md` — project reflection.

Before proposing or making any change to overdue, tag, or filtering behavior, read `docs/midcourse/mini-adr.md`. It records the chosen designs and why simpler or alternative approaches were rejected. Do not replace those decisions without explicit user approval and an updated decision record.

When documentation and current code appear inconsistent, report the discrepancy rather than silently choosing one as authoritative.

## Confirmed business rules

### Task fields and defaults

From `app/models.py`:

- Status values: `ToDo`, `InProgress`, and `Done`.
- Priority values: `Low`, `Medium`, and `High`.
- New tasks default to:
  - status `ToDo`
  - priority `Medium`
  - description `""`
  - assignee `None`
  - tags `[]`
  - due date `None`
- Task IDs are generated UUID strings.
- Creation and update timestamps use UTC.
- Extra request fields are forbidden.

### Title validation

For task creation:

- A title is required.
- Leading and trailing whitespace is stripped.
- A blank or whitespace-only title is rejected.
- A title longer than 200 characters after trimming is rejected.

For task updates:

- Non-null titles receive the same trimming, blank, and length validation.
- An explicit `"title": null` is currently accepted by the PATCH path. This is a known limitation recorded in `README.md` and pinned by a test in `tests/test_tasks.py`; do not describe it as intended validation.

### Status transitions

`app/business_rules.py` permits only:

- `ToDo` → `InProgress`
- `InProgress` → `Done`
- `Done` → `InProgress`

All other transitions, including same-status updates, return HTTP 422 when submitted through the PATCH endpoint.

### Partial updates

- `PATCH /tasks/{task_id}` applies only fields explicitly included in the request.
- An empty JSON object leaves the task unchanged.
- An explicitly null description is converted to an empty string.
- Unknown task IDs return HTTP 404 for get, update, and delete operations.

### Tags, filtering, and sorting

`GET /tasks` supports optional exact filters for:

- status
- priority
- tag membership
- overdue state

Multiple supplied filters combine with AND. Results sort by `created_at` in ascending order.

Tags are stored directly as `list[str]`. No separate tag entity, normalization rule, uniqueness rule, or case-insensitive matching behavior is confirmed.

### Due dates and overdue state

- A task is overdue when its due date is before the current local date and its status is not `Done`.
- A missing due date is not overdue.
- A completed task is not overdue.
- `is_overdue` is derived when a task is created or updated; clients do not supply it through `TaskCreate` or `TaskUpdate`.
- No background recalculation job is confirmed.

## Module 5 guardrails

Apply these rules to all Module 5 work:

1. Begin with read-only inspection and analysis.
2. Prefer documentation and governance work over implementation.
3. Edit files under `docs/` only unless the user explicitly authorizes another path.
4. Do not modify `app/` unless the user explicitly requests and approves one specific minimal fix.
5. Treat each Codex task/thread as one bounded task. Do not expand into unrelated cleanup, refactoring, or feature work.
6. Before editing, state the intended task, files to inspect or change, and whether permission is required.
7. Preserve unrelated user changes in the working tree.
8. Verify changes in proportion to their risk, but do not use testing as permission to alter application behavior.
9. If a requested action exceeds the approved scope, stop and request direction.

## Security and governance

- Never paste, print, commit, or expose secrets, credentials, tokens, private keys, or local `.env` values.
- Treat `.env.example` as a template, not evidence of real secret values or active configuration.
- Do not run destructive commands or operations, including broad deletion, destructive Git resets, or overwriting unrelated work.
- Prefer reversible, narrowly scoped actions.
- Cite the repository files inspected when making factual claims about the project.
- Distinguish code-confirmed behavior, test-confirmed behavior, documentation claims, and assumptions.
- Do not invent commands, architecture, test results, vulnerabilities, or business rules.
- Mark unverified statements as `not confirmed`.
- If a file is absent, inaccessible, truncated, or not inspected, say so.
- Do not claim that tests passed unless they were actually run in the current task.
- Do not treat documentation as proof that runtime behavior was verified.
- Report known limitations without silently fixing them.
