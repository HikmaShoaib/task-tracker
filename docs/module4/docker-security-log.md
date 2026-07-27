# Docker Security Log — Part 4.3

| Check | Evidence |
|---|---|
| Non-root user | `docker exec tt-dev whoami` → `app` |
| Slim runtime base | Runtime stage uses `python:3.11-slim` |
| No baked secrets | `.dockerignore` excludes `.env`, `.git`, `venv/`, `.venv/`, and caches |

Additional verification:
- `docker build -t task-tracker:dev .` completed successfully (14/14 steps).
- `GET /health` returned `200 OK` with `{"status":"ok", "timestamp": "..."}`.