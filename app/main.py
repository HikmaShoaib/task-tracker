"""Task Tracker API - Module 1-4 learning project.

Creates the FastAPI application instance and exposes a full CRUD API for
tasks (create, list/filter, get, update, delete) plus GET /health.
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException
from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority
from app import storage
from app.business_rules import validate_status_transition

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Task Tracker API",
    description="Module 1-4 learning project: a task tracker REST API with full CRUD for tasks.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "null",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health() -> dict:
    """Liveness check endpoint.

    Route:
        GET /health

    Returns:
        dict: ``{"status": "ok", "timestamp": <current UTC ISO-8601 datetime>}``.

    Example:
        GET /health -> 200 {"status": "ok", "timestamp": "2026-07-27T12:00:00+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Route:
        POST /tasks

    Args:
        payload: Task creation data. Validated by ``TaskCreate``
            (extra fields forbidden; ``title`` required, non-blank,
            <=200 characters after trimming).

    Returns:
        TaskResponse: The newly created task, HTTP 201.

    Raises:
        [VERIFY] No explicit HTTPException is raised in this handler
        body; invalid payloads are rejected by FastAPI/Pydantic
        request validation (HTTP 422) before this function runs.

    Example:
        POST /tasks {"title": "Write docs"} -> 201 TaskResponse
    """
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def get_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    tag: str | None = None,
    overdue: bool | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by query parameters.

    Route:
        GET /tasks

    Args:
        status: Optional exact-match status filter (query param).
        priority: Optional exact-match priority filter (query param).
        tag: Optional tag filter; task must have this tag in its
            ``tags`` list (query param).
        overdue: Optional filter on the derived ``is_overdue`` flag
            (query param).

    Returns:
        list[TaskResponse]: Matching tasks sorted ascending by
        ``created_at``.

    Example:
        GET /tasks?status=ToDo&tag=urgent -> 200 [TaskResponse, ...]
    """
    return storage.get_all_tasks(status=status, priority=priority, tag=tag, overdue=overdue)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Get a single task by id.

    Route:
        GET /tasks/{task_id}

    Args:
        task_id: The task's unique id (path parameter).

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.

    Example:
        GET /tasks/{task_id} -> 200 TaskResponse
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task.

    Route:
        PATCH /tasks/{task_id}

    If ``payload.status`` is set, the task must exist and the
    requested transition must be allowed (see
    ``app.business_rules.validate_status_transition``) or a 422 is
    raised before any field is applied.

    Args:
        task_id: The id of the task to update (path parameter).
        payload: Partial update data; only explicitly set fields are
            applied (extra fields forbidden).

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
        HTTPException: 422 if ``payload.status`` is set and the
            transition from the task's current status is not allowed.

    Example:
        PATCH /tasks/{task_id} {"status": "InProgress"} -> 200 TaskResponse
    """
    if payload.status is not None:
        existing_task = storage.get_task_by_id(task_id)
        if existing_task is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing_task.status, payload.status)
    updated_task = storage.update_task(task_id, payload)
    if updated_task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return updated_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by id.

    Route:
        DELETE /tasks/{task_id}

    Args:
        task_id: The id of the task to delete (path parameter).

    Returns:
        None. HTTP 204 No Content on success.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.

    Example:
        DELETE /tasks/{task_id} -> 204
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)