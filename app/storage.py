from datetime import datetime, timezone, date
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def _compute_is_overdue(due_date: Optional[date], status: TaskStatus) -> bool:
    if due_date is None:
        return False
    if status == TaskStatus.DONE:
        return False
    return due_date < date.today()


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and persist a new task.

    Generates a new UUID id and UTC timestamps, and derives the initial
    ``is_overdue`` flag from ``due_date``/``status``.

    Args:
        payload: Validated task creation data.

    Returns:
        TaskResponse: The newly created and stored task.
    """
    task_id = str(uuid4())
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        tags=payload.tags,
        due_date=payload.due_date,
        is_overdue=_compute_is_overdue(payload.due_date, payload.status),
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    tag: Optional[str] = None,
    overdue: Optional[bool] = None,
) -> list[TaskResponse]:
    """Return stored tasks, optionally filtered, sorted by creation time.

    Filters combine with AND when more than one is supplied. Each
    filter is a no-op when left as ``None``.

    Args:
        status: If given, only include tasks with this exact status.
        priority: If given, only include tasks with this exact priority.
        tag: If given, only include tasks whose ``tags`` list contains
            this value.
        overdue: If given, only include tasks whose stored
            ``is_overdue`` flag equals this value.

    Returns:
        list[TaskResponse]: Matching tasks sorted ascending by
        ``created_at``.
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    if tag is not None:
        tasks = [task for task in tasks if tag in task.tags]
    if overdue is not None:
        tasks = [task for task in tasks if task.is_overdue == overdue]
    return sorted(tasks, key=lambda task: task.created_at)

def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a single task by id.

    Args:
        task_id: The task's unique id.

    Returns:
        The matching TaskResponse, or None if no task with that id
        exists.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task.

    Only fields explicitly set on ``payload`` are applied (via
    ``model_dump(exclude_unset=True)``); omitted fields are left
    unchanged. An explicitly set ``description: None`` is coerced to
    ``""``. ``updated_at`` and ``is_overdue`` are recomputed after the
    update is applied.

    Note:
        This function does not itself validate status transitions;
        that is enforced by the caller (see
        ``app.business_rules.validate_status_transition``, invoked
        from the ``PATCH /tasks/{task_id}`` route handler).
        [VERIFY] Fields are applied via ``model_copy(update=...)``,
        which bypasses Pydantic field validation at this layer — e.g.
        an explicit ``title: null`` would not be re-checked here.

    Args:
        task_id: The id of the task to update.
        payload: The partial update payload.

    Returns:
        None if no task with ``task_id`` exists; the unchanged
        existing task if ``payload`` set no fields; otherwise the
        updated TaskResponse.
    """
    existing_task = _tasks.get(task_id)
    if existing_task is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return existing_task

    if "description" in update_data and update_data["description"] is None:
        update_data["description"] = ""

    updated_task = existing_task.model_copy(update=update_data)
    updated_task.updated_at = datetime.now(timezone.utc)
    updated_task.is_overdue = _compute_is_overdue(updated_task.due_date, updated_task.status)
    _tasks[task_id] = updated_task
    return updated_task


def delete_task(task_id: str) -> bool:
    """Delete a task by id.

    Args:
        task_id: The id of the task to delete.

    Returns:
        True if a task was found and deleted, False if no task with
        that id existed.
    """
    return _tasks.pop(task_id, None) is not None


def _reset() -> None:
    _tasks.clear()