# Release Evidence

## Baseline

- Branch: final-project
- Date: 2026-08-08
- Local app run command: `uvicorn app.main:app --reload`
- /health result: `{"status":"ok","timestamp":"2026-08-08T14:16:11.112609+00:00"}` (HTTP 200)
- Frontend check: Opened `frontend/index.html` with VS Code Live Server; Kanban board loads with status columns, and creating/editing a task still works.
- Test command: `pytest -v`
- Test result: 26 passed, 3 warnings (0.41s). Warnings are pre-existing deprecation notices (`httpx`/starlette test client, `HTTP_422_UNPROCESSABLE_ENTITY` naming) — not failures, and not introduced by final-project work.

## CI evidence

- Workflow file: .github/workflows/ci.yml
- Latest run link or note: https://github.com/HikmaShoaib/task-tracker/actions/runs/31261476522 (CI #15, green, final-project branch, 24s)
- Test command used by CI: `pytest -v`
- Shortcut check: no continue-on-error / no || true / pytest is not skipped. Python version pinned explicitly to 3.11; dependencies installed via `pip install -r requirements.txt` before tests run.

## Docker evidence

- Build command: `docker build -t task-tracker:dev .`
- Run command: `docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev`
- /health check: `curl http://127.0.0.1:8000/health` returned HTTP 200, `{"status":"ok","timestamp":"2026-08-08T15:50:29.979817+00:00"}`
- Non-root check, if implemented: `docker exec tt-dev whoami` returned `app` (confirmed non-root execution).
- No-baked-secrets check: `.dockerignore` excludes `.env` and secret files; Dockerfile does not COPY any `.env` file into the image; requirements are installed from `requirements.txt` only.

## Documentation claim-vs-reality log

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| PATCH /tasks/{id} with title: null is not rejected and returns title: null | tests/test_tasks.py::test_patch_title_null_is_accepted_and_returns_null_title — PASSED in pytest run | Confirmed accurate | None needed |
| Dockerfile runs as non-root app user | `docker exec tt-dev whoami` returned `app` | Confirmed accurate | None needed |
| ci.yml runs on push/pull_request and executes `pytest -v` | CI #15 run on final-project branch (green, triggered by push) matches workflow file content | Confirmed accurate | None needed |