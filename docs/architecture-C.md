# Task Tracker Architecture

## 1. What the app does

Task Tracker is a FastAPI REST API that provides a health check and CRUD operations for tasks. Clients can create, retrieve, filter, partially update, and delete tasks. Filtering supports status, priority, tag membership, and overdue state. (`app/main.py`)

## 2. Data model

The main entity is `Task`, represented by three Pydantic models:

- `TaskCreate`: title, description, status, priority, assignee, tags, and due date.
- `TaskUpdate`: optional versions of the creation fields for partial updates.
- `TaskResponse`: adds UUID-based `id`, derived `is_overdue`, `created_at`, and `updated_at`.
- Status values: `ToDo`, `InProgress`, `Done`.
- Priority values: `Low`, `Medium`, `High`.

New tasks default to `ToDo`, `Medium` priority, an empty description and tag list, and no assignee or due date. (`app/models.py`)

## 3. Request flow

For `POST /tasks`, FastAPI parses the request into `TaskCreate`. Pydantic rejects extra fields and validates the required title by trimming whitespace, rejecting blank values, and enforcing a 200-character maximum. The route calls `storage.add_task`, which generates a UUID, creates UTC timestamps, calculates overdue state from the local date, constructs a `TaskResponse`, stores it in the module-level dictionary, and returns it with HTTP 201. (`app/main.py`, `app/models.py`, `app/storage.py`)

## 4. Key files

- `app/main.py` — creates the FastAPI app, configures CORS, and defines health and task routes.
- `app/models.py` — defines task schemas, enums, defaults, and title validation.
- `app/storage.py` — implements in-memory CRUD, filtering, sorting, UUID creation, and overdue calculation.
- `app/business_rules.py` — referenced by the update route for status-transition validation; its implementation is not visible from the files I read.
- Frontend entry file — not visible from the files I read.

## 5. Conventions

- **Validation:** Pydantic models forbid extra fields; titles are trimmed and constrained to 1–200 characters. Partial updates apply only explicitly supplied fields.
- **Storage:** Tasks reside in a module-level `dict[str, TaskResponse]`; no durable persistence is visible from the files I read.
- **Errors:** Missing task IDs produce HTTP 404. Invalid status transitions produce HTTP 422 through the referenced business-rule function. Request-model validation occurs before route execution.
- **Derived data:** `is_overdue` is false without a due date or when status is `Done`; otherwise it compares the due date with the current local date.
- **Frontend/backend interaction:** The API enables CORS for `null` and localhost/127.0.0.1 on ports 5500 and 8000. The frontend implementation and its request behavior are not visible from the files I read.

## 6. Not visible or assumptions

Authentication, authorization, deployment architecture, database support, frontend structure, tests, dependency versions, status-transition rules, production CORS policy, logging, monitoring, and concurrency or multi-process behavior are **not visible from the files I read**.
