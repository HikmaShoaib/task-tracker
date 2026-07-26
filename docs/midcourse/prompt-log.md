# Prompt Log — Mid-Course Project

## Feature 1: Tags/Labels

**Prompt 1 (weak → strong rewrite):**
- Weak: "Add tags to my task tracker."
- Why weak: no file references, no data shape, no validation rule — AI could invent a Tag database table, a new endpoint, or arbitrary field names.
- Strong (used instead): "In app/models.py, add a `tags: list[str] = []` field to TaskCreate, TaskUpdate, and TaskResponse. No new entity, no separate Tag table — tags are just strings on the task."
- AI output: Correctly added the field to all three models with the exact type/default requested.
- Decision: Accepted as-is, no edits needed.

**Prompt 2:** "In app/storage.py, add tag filtering to get_all_tasks — a `tag: Optional[str]` param that keeps only tasks where `tag in task.tags`."
- AI output: Correct filter logic, consistent with existing status/priority filter pattern in the same function.
- Decision: Accepted as-is.

**Prompt 3:** "Update GET /tasks in app/main.py to accept a `tag` query param and pass it to storage.get_all_tasks."
- AI output: Correct, matched existing query param style (status, priority already there).
- Decision: Accepted as-is.

**Prompt 4:** "Add tags to the frontend modal form (comma-separated text input), and render each tag as a pill/chip on the task card."
- AI output: Added the input field, JS parsing (split by comma, trim, filter empty), and chip rendering.
- Decision: Accepted as-is; verified visually in the browser that tags render as separate "#tag" chips.

## Feature 2: Due Dates + Overdue Filter

**Prompt 1:** "In app/models.py, add an optional due_date field (type date) to TaskCreate, TaskUpdate, and TaskResponse. Also add is_overdue: bool to TaskResponse only."
- AI output: Correct fields added; is_overdue correctly left out of TaskCreate/TaskUpdate since it's not something the client sets directly.
- Decision: Accepted as-is.

**Prompt 2 (weak → strong rewrite):**
- Weak: "Make overdue tasks show up somehow."
- Why weak: doesn't specify whether overdue is computed or stored, doesn't define the overdue rule, and "somehow" gives no UI guidance.
- Strong (used instead): "Add a `_compute_is_overdue(due_date, status)` helper in app/storage.py that returns True only if due_date is in the past AND status is not Done. Call it whenever a task is created or updated, and store the result on the TaskResponse's is_overdue field."
- AI output: Correct helper function and correct call sites in add_task and update_task.
- Decision: Accepted as-is — this avoids a stale stored flag by recomputing on every write.

**Prompt 3:** "Add an `overdue: Optional[bool]` query param to GET /tasks that filters by the is_overdue field."
- AI output: Correct, consistent with the tag filter added earlier.
- Decision: Accepted as-is.

**Prompt 4:** "Add a due date input (type=date) to the frontend modal, and show a red 'Overdue: <date>' pill on cards where is_overdue is true, or a normal 'Due: <date>' pill otherwise."
- AI output: Correct conditional rendering logic.
- Decision: Accepted as-is; verified visually that overdue tasks show a red pill and non-overdue tasks show a normal pill.

## Cross-cutting note
AI's first-pass suggestion for is_overdue was to store it as a persisted field, updated by a background job on a schedule. I rejected this as too complex for the project scope and asked for it to be computed live on every read/write instead — see mini-adr.md for the full reasoning.