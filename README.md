## Final Project
Branch reviewed: final-project

### What this submission demonstrates
- Existing Task Tracker app still runs inside the intended course scope.
- CI runs the pytest suite on push and/or pull request.
- Docker image builds and runs with /health returning 200.
- AI review, security, and ownership evidence is in docs/.

### How to run locally
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

### How to run tests
```powershell
pytest -v
```

### How to run with Docker
```powershell
docker build -t task-tracker:dev .
docker run --rm -p 8000:8000 --name tt-dev task-tracker:dev
curl http://127.0.0.1:8000/health
```

### Evidence files
- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

### AI assistance summary
AI helped draft or review: CI verification, Docker verification, documentation claim-checking, security mini-review.
I verified the work by: running the full pytest suite (26 passed), checking the live CI run on GitHub, building and running the Docker image locally, and confirming /health returned 200 in both local and Docker runs.
One AI suggestion I rejected or corrected: Codex initially graded my public source code as Medium risk in the governance retrospective; I corrected this after confirming the repo was actually public on GitHub.

---


# Task Tracker API — Module 4

A Task Tracker REST API built with Python and FastAPI as a Module 1–4 learning project. It exposes CRUD endpoints for tasks (create, list/filter, view, update, delete) plus a `/health` check, backed by an in-memory store — no database.

This is a learning project, not a production service. It has no auth, no database, and no deployment configuration beyond a local-use Dockerfile — see [Project conventions and current limitations](#project-conventions-and-current-limitations).

## Prerequisites

- Python 3.11+ ([VERIFY] CI and the Dockerfile both pin 3.11; this repo's local `venv/` is actually Python 3.13.5, so the true minimum is unconfirmed — 3.11 is the safe target to match CI/Docker)
- pip
- Optional: Docker Desktop (or another Docker engine), if you want to run the app in a container instead of a venv
- Optional: VS Code with the Live Server extension, if you want to run the frontend

## Local setup

All commands assume PowerShell from the repo root.

1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create your local env file from the example:

```powershell
Copy-Item .env.example .env
```

## Run the app locally

```powershell
uvicorn app.main:app --reload --port 8000
```

The API starts on http://127.0.0.1:8000 — Swagger UI at `/docs`, health check at `GET /health`.

```powershell
curl http://127.0.0.1:8000/health
```

### Running the frontend (optional)

The frontend is a static HTML/JS file at `frontend/index.html`. With the backend running (above), open `frontend/index.html` in VS Code and use the Live Server extension ("Open with Live Server"). It runs on http://127.0.0.1:5500 and talks to the backend automatically — `app/main.py` hardcodes CORS to allow that origin plus `127.0.0.1`/`localhost:8000`.

## Run tests

With the virtual environment activated:

```powershell
pytest tests/test_tasks.py -v
```

To run everything CI runs (the full suite, same command `ci.yml` uses):

```powershell
pytest -v
```

[VERIFY] `tests/verify_a.py` is a standalone manual-verification script (prints PASS/FAIL, no `test_`-prefixed functions) — it is **not** collected by pytest and not run in CI. If you want to run it directly:

```powershell
python -m tests.verify_a
```

## Run with Docker

The `Dockerfile` is a multi-stage build (`python:3.11-slim`), runs as a non-root `app` user, and does not bake in `.env` or any secrets (see `.dockerignore` and `docs/module4/docker-security-log.md`).

```powershell
docker build -t task-tracker:dev .
docker run --rm -p 8000:8000 --name tt-dev task-tracker:dev
```

```powershell
curl http://127.0.0.1:8000/health
```

[VERIFY] The image does not copy `.env` in, and the container `CMD` hardcodes `--port 8000`, so `PORT`/`APP_ENV` from `.env.example` have no effect unless passed explicitly, e.g. `docker run --env-file .env ...` — this has not been tested against the current image.

This Dockerfile is for local/manual use only; there is no deployment or orchestration config in this repo.

## CI workflow summary

`.github/workflows/ci.yml` runs on every `push` and `pull_request` (all branches, no path filters):

1. Checks out the repo.
2. Sets up Python 3.11.
3. Installs dependencies from `requirements.txt`.
4. Runs `pytest -v`.

There is no lint step, no Docker build/push step, and no deployment step in CI currently.

## Project structure

```
app/
  main.py            FastAPI app instance, CORS config, all route handlers
  models.py           Pydantic models/enums: TaskCreate, TaskUpdate, TaskResponse,
                       TaskStatus, TaskPriority (title validation lives here)
  storage.py           In-memory repository (_tasks dict), CRUD, filtering/sorting
  business_rules.py    Status-transition validation
  schemas.py, repository.py, exceptions.py
                       Empty placeholder stubs — despite the names, not where
                       schema/repository/exception logic actually lives
tests/
  test_tasks.py        pytest suite for the API (run in CI)
  conftest.py          Autouse fixture that resets storage between tests
  verify_a.py          Standalone manual verification script (see Run tests)
frontend/
  index.html           Static Kanban UI served via Live Server on :5500
docs/
  midcourse/           ADR, user stories, verification, prompt log, reflection
                       for the mid-course-project branch
  module4/             Module 4 notes (e.g. Docker security log)
Dockerfile             Multi-stage build, non-root runtime user
.dockerignore           Excludes .env, .git, venv/.venv, caches, etc.
.github/workflows/ci.yml  GitHub Actions test workflow
requirements.txt        Python dependencies
.env.example             Template for local .env (PORT, APP_ENV)
```

## Project conventions and current limitations

- **In-memory storage only.** Tasks live in a module-level dict; all data is lost on app restart and is reset between tests via an autouse fixture. There is no database.
- **`is_overdue` is always computed, never stored** — derived on every read/write from `due_date < today() and status != Done`. No background job. See `docs/midcourse/mini-adr.md`.
- **Tags** are a bare `list[str]` on the task; no separate Tag entity. Filter via `GET /tasks?tag=...`.
- **Status transitions are restricted**: ToDo→InProgress, InProgress→Done, Done→InProgress only. Same-status or any other transition returns HTTP 422.
- Title validation (strip, non-blank, ≤200 chars) is duplicated across `TaskCreate` and `TaskUpdate` in `app/models.py`.
- `app/schemas.py`, `app/repository.py`, `app/exceptions.py` are empty stub files — don't assume missing functionality just because these are empty.
- **No authentication or authorization** of any kind.
- **No database** — this is intentionally out of scope for this module.
- **No deployment configuration.** The Dockerfile is for local/manual container runs only; nothing here should be treated as production-ready.
- CORS in `app/main.py` is hardcoded to a fixed allowlist (`127.0.0.1`/`localhost` on ports `5500` and `8000`), not configurable via env vars.
- **Known limitation:** `PATCH /tasks/{id}` with an explicit `title: null` is not rejected — it bypasses `TaskUpdate` validation via `model_copy(update=...)` and returns a `TaskResponse` with `title: null`, even though `title` is otherwise required. Not yet fixed.

## Mid-course project features

Two features were added on the `mid-course-project` branch:

- **Tags/labels**: Tasks can have multiple string tags. Filter with `GET /tasks?tag=urgent`.
- **Due dates + overdue filter**: Tasks can have an optional due date. Overdue status is computed automatically (past due + not Done). Filter with `GET /tasks?overdue=true`.

## Decisions and technical notes

- [`docs/midcourse/mini-adr.md`](docs/midcourse/mini-adr.md) — design decisions for tags, due dates, and the overdue filter (why simpler/alternative approaches were rejected).
- [`docs/module4/docker-security-log.md`](docs/module4/docker-security-log.md) — verification log for the Module 4 Docker setup (non-root user, slim base, no baked secrets).
- [`docs/decisions/in-memory-task-storage.md`](docs/decisions/in-memory-task-storage.md) — decision note on using an in-memory dict for task storage (context, alternatives, trade-offs, open questions).
- See also `docs/midcourse/user-stories.md`, `docs/midcourse/verification.md`, `docs/midcourse/prompt-log.md`, and `docs/midcourse/reflection.md` for the rest of the mid-course paper trail.
