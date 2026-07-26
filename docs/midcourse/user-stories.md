# User Stories — Mid-Course Project

## Feature 1: Tags/Labels

1. **As a user, I want to add one or more tags to a task, so I can categorize it.**
   - Acceptance criteria: POST /tasks accepts a `tags` list; tags are trimmed strings; blank/whitespace-only tags are rejected.

2. **As a user, I want to see a task's tags displayed on its card, so I can quickly identify its category.**
   - Acceptance criteria: Each tag renders as a separate chip (e.g. "#urgent") on the task card in the frontend.

3. **As a user, I want to filter the task board by tag, so I can focus on tasks relevant to a specific category.**
   - Acceptance criteria: GET /tasks?tag=urgent returns only tasks containing that tag (case-sensitive exact match).

4. **As a user, I want to update a task's tags without affecting its other fields, so I can correct categorization over time.**
   - Acceptance criteria: PATCH /tasks/{id} with only a `tags` field updates tags and leaves title/status/priority/etc. unchanged.

**AI assumption corrected:** AI's first draft assumed tags needed a separate Tag entity with IDs for global rename/delete. I corrected this — tags are just free-text strings per task; no tag management system needed at this scope.

## Feature 2: Due Dates + Overdue Filter

1. **As a user, I want to set an optional due date when creating or editing a task, so I know when it needs to be completed.**
   - Acceptance criteria: POST/PATCH accept an optional `due_date` in ISO format (YYYY-MM-DD); invalid date strings return 422.

2. **As a user, I want to see a task's due date displayed on its card, so I can plan my work.**
   - Acceptance criteria: Due date renders as a pill on the card when present; no pill shown when due_date is null.

3. **As a user, I want overdue tasks (due date in the past, not yet Done) to be visually flagged, so I can prioritize them.**
   - Acceptance criteria: `is_overdue` is true only when due_date < today AND status != Done; the overdue pill is styled distinctly (red) on the frontend.

4. **As a user, I want to filter the board to show only overdue tasks, so I can quickly see what needs urgent attention.**
   - Acceptance criteria: GET /tasks?overdue=true returns only tasks where is_overdue is true.

**AI assumption corrected:** AI's first draft suggested storing `is_overdue` as a persisted field, updated by a background job. I corrected this — overdue status is computed live on every read, so it can never go stale and no background job is needed.