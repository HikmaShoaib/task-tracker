# Mini ADR — Mid-Course Project

## Decision 1: Tags stored as a list of strings on the Task model

- **Context:** Tasks need to support multiple categorization labels.
- **Decision:** Add a `tags: list[str]` field to the Task model, defaulting to an empty list. No separate Tag entity/table — tags are just strings on the task.
- **Why:** Simplest possible implementation given time constraints and in-memory dict storage. No need for tag management (rename/delete globally) in this scope.
- **Alternative considered:** Separate Tag model with IDs — rejected as overkill for this project size.

## Decision 2: Due date as optional ISO date field; overdue computed, not stored

- **Context:** Tasks need an optional due date, and the system needs to flag overdue tasks.
- **Decision:** Add `due_date: Optional[date]` to the Task model. "Overdue" is NOT a stored field — it's computed on read (due_date < today AND status != "Done").
- **Why:** Avoids stale/inconsistent data (an overdue flag stored in the DB could go out of sync). Computing it live is simple and always correct.
- **Alternative considered:** Storing an `is_overdue` boolean — rejected, would require background jobs to keep updated.

## Decision 3: Filtering happens via query parameters on GET /tasks

- **Decision:** Extend `GET /tasks` to accept optional query params: `tag` (filter by tag) and `overdue` (true/false filter).
- **Why:** Keeps the API RESTful and consistent with existing endpoint design; no new endpoints needed.