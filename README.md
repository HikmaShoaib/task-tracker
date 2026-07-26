# Task Tracker API — Module 1

A simple Task Tracker REST API built with Python and FastAPI as a learning project. Tasks are stored in an in-memory dictionary; all data resets when the application restarts (an accepted Module 1 trade-off — see the ADR).

This skeleton exposes only a /health endpoint. CRUD endpoints for tasks (create, view, update, delete) are added in later steps.

## Setup

1. Create and activate a virtual environment:

Windows PowerShell:
python -m venv venv
venv\Scripts\Activate.ps1

2. Install dependencies:
pip install -r requirements.txt

3. Create your local env file from the example:
Copy-Item .env.example .env

## Run

uvicorn app.main:app --reload

The API starts on http://127.0.0.1:8000

## Test the health endpoint

curl http://127.0.0.1:8000/health

## API docs

Interactive Swagger UI: http://127.0.0.1:8000/docs

## Running the Frontend

The frontend is a static HTML/JS file at `frontend/index.html`. With the backend running (see above), open `frontend/index.html` using VS Code's Live Server extension (right-click the file → "Open with Live Server"). It will run on http://127.0.0.1:5500 and connect to the backend automatically.

## Running Tests

With your virtual environment activated:

pytest tests/test_tasks.py -v

## Mid-Course Project Features

Two features were added on the `mid-course-project` branch:

- **Tags/labels**: Tasks can have multiple string tags. Filter with `GET /tasks?tag=urgent`.
- **Due dates + overdue filter**: Tasks can have an optional due date. Overdue status is computed automatically (past due + not Done). Filter with `GET /tasks?overdue=true`.

See `docs/midcourse/` for user stories, architecture decisions, prompt log, verification, and reflection.