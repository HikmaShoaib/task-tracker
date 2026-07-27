from datetime import datetime, date
from enum import Enum
from typing import Optional

from pydantic import ConfigDict, BaseModel, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    tags: list[str] = []
    due_date: Optional[date] = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> object:
        """Strip and validate the ``title`` field before type coercion.

        Runs in Pydantic "before" mode, so ``value`` may be any raw
        input type (not yet coerced to ``str``).

        Args:
            value: The raw input for the ``title`` field.

        Returns:
            The stripped title string; unchanged if ``value`` is
            ``None`` or not a ``str`` (in which case Pydantic's
            built-in type validation handles it next, since ``title``
            has no default and is not ``Optional`` here).

        Raises:
            ValueError: If the stripped title is empty, or longer than
                200 characters.
        """
        if value is None:
            return value
        if not isinstance(value, str):
            return value

        stripped_value = value.strip()
        if not stripped_value:
          raise ValueError("Title is required and cannot be blank")
        if len(stripped_value) > 200:
            raise ValueError("Title must be 1..200 characters after trimming")
        return stripped_value


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    tags: Optional[list[str]] = None
    due_date: Optional[date] = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> object:
        """Strip and validate an optional ``title`` update before type coercion.

        Runs in Pydantic "before" mode. ``title`` is ``Optional`` on
        ``TaskUpdate``, so ``None`` passes through unchanged here.
        [VERIFY] That makes an explicit ``"title": null`` in a request
        body indistinguishable from other None-ish inputs at this layer
        — it is not rejected by this validator.

        Args:
            value: The raw input for the ``title`` field, or ``None``.

        Returns:
            The stripped title string; ``None`` unchanged; or the
            original value unchanged if it is not a ``str`` (left for
            Pydantic's built-in type validation).

        Raises:
            ValueError: If the stripped title is empty, or longer than
                200 characters.
        """
        if value is None:
            return value
        if not isinstance(value, str):
            return value

        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Title is required and cannot be blank")
        if len(stripped_value) > 200:
            raise ValueError("Title must be 1..200 characters after trimming")
        return stripped_value


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    tags: list[str] = []
    due_date: Optional[date] = None
    is_overdue: bool = False
    created_at: datetime
    updated_at: datetime