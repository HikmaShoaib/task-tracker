# Comments on Tasks Feature Plan and Evaluation

Status: Proposed design only. Nothing in this document has been implemented.

## 1. Repo-Grounded Plan

### Data Model

#### Observed repository pattern

`app/models.py` contains the task request and response models. Each request model uses `ConfigDict(extra="forbid")`, while IDs and timestamps are generated in `app/storage.py`.

Tasks are stored as `TaskResponse` objects in the module-level `_tasks: dict[str, TaskResponse]` dictionary in `app/storage.py`. There is no database or actual foreign-key mechanism.

#### Proposed models

Add the comment models to `app/models.py` alongside the existing task models:

- `CommentCreate`
  - `author: str`
  - `body: str`
  - Forbid extra fields, following `TaskCreate`.
  - Reject missing values, `null`, non-string values, blank or whitespace-only values, and values outside the specified lengths.
  - Explicitly decide whether leading and trailing whitespace is stripped. The existing title validator strips whitespace before checking length, but no reusable string-validation convention exists.
- `CommentResponse`
  - `id: str`
  - `task_id: str`
  - `author: str`
  - `body: str`
  - `created_at: datetime`
  - Forbid extra fields, following `TaskResponse`.

Clients must not be able to supply `id`, `task_id`, or `created_at` through `CommentCreate`. Generate `id` with `str(uuid4())`, matching task IDs, and generate `created_at` with `datetime.now(timezone.utc)`, matching task creation timestamps.

Do not add comments directly to `TaskResponse` in the initial design. Keeping the resource separate avoids changing every existing task response and avoids duplicating complete comment collections whenever `GET /tasks` renders the Kanban board.

#### Proposed storage relationship

Add a separate module-level comment store in `app/storage.py`:

- Use a dictionary keyed by comment ID, with `CommentResponse` values.
- Filter that dictionary by `task_id` when listing comments and sort the results by `created_at` ascending.

This follows the current `_tasks` dictionary pattern while keeping comments independently addressable. Because there is no database, `task_id` is a logical reference rather than an enforced foreign key. Comment creation must confirm that `storage.get_task_by_id(task_id)` returns a task before storing the comment.

`storage._reset()` must clear both task and comment storage so the existing autouse fixture in `tests/conftest.py` continues to isolate tests.

### API Routes

The initial feature should expose creation and listing. Editing, individual retrieval, and deletion are not included until the team answers the lifecycle questions under Open Questions.

#### Create a comment

| Item | Design |
|---|---|
| Method | `POST` |
| Path | `/tasks/{task_id}/comments` |
| Request body | `author` and `body` only |
| Success status | `201 Created` |
| Response body | Complete `CommentResponse` |
| OpenAPI tag | `comments` |

The server generates `id`, copies `task_id` from the path, and generates `created_at` in UTC.

Error cases:

- `404 Not Found` when the task does not exist. To match existing route wording, use a detail such as `Task with id {task_id} not found`.
- `422 Unprocessable Entity` when:
  - `author` or `body` is missing.
  - Either field is `null`.
  - Either field is not a string.
  - Either field is blank after applying the chosen whitespace policy.
  - `author` is longer than 100 characters.
  - `body` is longer than 2,000 characters.
  - The payload includes an unknown or server-managed field such as `id`, `task_id`, or `created_at`.

No authentication-related errors are proposed because the application has no authentication or authorization.

#### List comments for a task

| Item | Design |
|---|---|
| Method | `GET` |
| Path | `/tasks/{task_id}/comments` |
| Request body | None |
| Success status | `200 OK` |
| Response body | `list[CommentResponse]` |
| Ordering | `created_at` ascending, subject to team confirmation |
| OpenAPI tag | `comments` |

Error cases:

- `404 Not Found` when the task does not exist.
- An existing task with no comments returns `200 OK` and an empty list, matching the behavior of `GET /tasks`.

Pagination, filtering, and sorting query parameters are not proposed for the initial in-memory feature. No repository convention for pagination is visible.

#### Interaction with task deletion

`DELETE /tasks/{task_id}` currently removes only the task from `_tasks`. A comments implementation must adopt one explicit policy:

- Cascade-delete comments belonging to the task; or
- Retain orphaned comments, which is not recommended for the current nested API.

Cascade deletion is the recommended default because comments cannot be reached meaningfully through `/tasks/{task_id}/comments` after their task is deleted. This still requires team approval because the repository currently has no relationship-deletion convention.

### Tests

The existing API tests use `pytest`, FastAPI's `TestClient`, direct status/body assertions, a `created_task` fixture, and an autouse storage reset fixture. Add a focused `tests/test_comments.py` rather than further expanding `tests/test_tasks.py`.

`tests/conftest.py` can continue to supply `client` and `created_task`. Its autouse fixture will cover comments once `storage._reset()` clears both stores.

#### Happy path

- `test_create_comment_valid_returns_201_with_full_body`
  - Assert that the returned `id` is non-empty and parseable as a UUID.
  - Assert that `task_id`, `author`, and `body` match the request and parent task.
  - Assert that `created_at` is present, parseable, and UTC-aware.
- `test_list_comments_for_task_returns_200_in_creation_order`
  - Create two comments for one task and assert ascending creation order if that order is approved.
- `test_list_comments_for_existing_task_with_no_comments_returns_empty_list`
- `test_list_comments_returns_only_comments_for_requested_task`
  - Create two tasks and comments for each; verify isolation by `task_id`.
- `test_create_comment_accepts_author_at_100_character_boundary`
- `test_create_comment_accepts_body_at_2000_character_boundary`

#### Validation

- `test_create_comment_missing_author_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_null_author_returns_422`
- `test_create_comment_null_body_returns_422`
- `test_create_comment_blank_author_returns_422`
- `test_create_comment_blank_body_returns_422`
- `test_create_comment_author_over_100_characters_returns_422`
- `test_create_comment_body_over_2000_characters_returns_422`
- `test_create_comment_non_string_author_returns_422`
- `test_create_comment_non_string_body_returns_422`
- `test_create_comment_unknown_field_returns_422`
- `test_create_comment_rejects_client_supplied_id`
- `test_create_comment_rejects_client_supplied_task_id`
- `test_create_comment_rejects_client_supplied_created_at`

Boundary tests should reflect the agreed whitespace policy. For example, if values are trimmed before validation, add:

- `test_create_comment_trims_author_before_storing`
- `test_create_comment_whitespace_only_body_returns_422`

#### Edge cases

- `test_create_comment_for_missing_task_returns_404_with_detail`
- `test_list_comments_for_missing_task_returns_404_with_detail`
- `test_comment_id_is_unique_across_comments`
- `test_comment_created_at_is_server_generated_utc_datetime`
- `test_reset_storage_removes_comments_between_tests`
- `test_delete_task_removes_its_comments`
  - Include only if cascade deletion is approved.
- `test_delete_task_does_not_remove_comments_for_other_tasks`
  - Include only if cascade deletion is approved.
- `test_comment_body_preserves_internal_newlines`
- `test_comment_response_contains_no_extra_fields`

`tests/verify_a.py` is a standalone manual verification script rather than part of pytest or CI. Comment coverage should therefore go into pytest tests, not only that script.

### Frontend Changes

The entire frontend currently lives in `frontend/index.html`, including markup, CSS, state, rendering, and API calls. There is no visible frontend build system or separate JavaScript module.

#### Files that would change

- `frontend/index.html`
  - Add comment-section markup and styles.
  - Add comment loading, rendering, validation, submission, empty-state, and error-state logic.
  - Call the nested comment endpoints using the existing `BASE_URL`.
- `app/main.py`
  - Add the API routes. Existing CORS configuration already permits the Live Server origins and all HTTP methods, so no CORS change appears necessary.
- `app/models.py` and `app/storage.py`
  - Add the models and in-memory storage behavior described above.
- `tests/test_comments.py`
  - Add the proposed API tests. `tests/conftest.py` need not change unless a new comment-specific fixture is useful.
- `README.md`
  - Document the new routes and clarify comment persistence and deletion behavior.

#### Proposed user experience

The existing task modal supports both "New Task" and "Edit Task." Comments should appear only when editing an already-created task because a new task has no `task_id`.

When the user selects **Edit** on a task card:

- The modal continues to show the existing task fields.
- A **Comments** section appears below those fields.
- Existing comments load from `GET /tasks/{task_id}/comments`.
- Each comment shows its author, body, and creation time.
- An empty state says that the task has no comments yet.
- A small form lets the user enter an author and body and submit a new comment.
- Successful submission clears the comment body and refreshes or appends the returned comment.
- Validation and network failures appear within the comments section rather than replacing the board-level state.
- User-provided author and body content is rendered as text or escaped with the existing `escapeHtml` convention.

Disable or otherwise guard the submit action while a comment request is in flight to reduce accidental duplicate submissions.

A comment count on every Kanban card is not part of the initial plan. With only the nested list endpoint, obtaining counts would require one request per task. If counts are desired, the team should first choose an API design that avoids that request pattern.

### Migration Notes

There is no database and therefore no schema migration, database migration script, or existing persisted task data to transform. `README.md` and `app/storage.py` confirm that all task data is process-local and disappears on restart.

The in-memory storage shape still requires coordinated changes:

- Add comment storage without changing the existing `_tasks` value shape.
- Extend `storage._reset()` to clear comments as well as tasks.
- Ensure comment creation checks that the referenced task currently exists.
- Update task deletion if cascade deletion is selected.
- Keep comments out of `TaskResponse` unless the API contract is deliberately expanded later.

Existing task API response bodies can remain unchanged. This avoids breaking `tests/test_tasks.py` and the assumptions in `frontend/index.html`.

If the project later adopts a database, the comment model would require:

- A comments table or equivalent collection.
- A unique identifier.
- A relationship to tasks.
- An index on `task_id`.
- An explicit delete policy.
- UTC-aware timestamp storage.

The database technology and migration tooling are not visible in the repository and must not be assumed.

### Open Questions

These questions should be resolved as decision gates before the routes, storage behavior, and dependent tests are finalized:

1. **What happens to comments when a task is deleted?**  
   Cascade deletion is recommended, but the repository has no existing relationship-deletion policy.
2. **Should comments be editable or deletable?**  
   The supplied data model has no `updated_at`, and the application has no authentication. Supporting edits or deletion would require deciding who may perform them and whether edit history matters.
3. **What is the whitespace policy for `author` and `body`?**  
   Task titles are trimmed, but comment bodies may intentionally contain leading whitespace or line breaks. Decide whether to trim both fields, trim only the author, or preserve body whitespace while rejecting whitespace-only bodies.
4. **Should an author be free-form or derived from identity?**  
   The current project has no authentication. A free-form author is consistent with the requested schema but allows impersonation and inconsistent names.
5. **Should list order be oldest-first or newest-first?**  
   Oldest-first follows `storage.get_all_tasks()`, which sorts tasks by `created_at` ascending. Newest-first may be more convenient in a comment UI.
6. **Are comments included in task responses or always fetched separately?**  
   Separate nested endpoints preserve the existing task contract and avoid inflating `GET /tasks`; embedding could reduce requests in a future task-detail view.
7. **Are pagination or maximum comments per task needed?**  
   They are likely unnecessary for this learning project, but an unbounded in-memory collection can grow indefinitely. No pagination convention currently exists.
8. **Should task cards display comment counts?**  
   This would require adding a derived count to task responses, adding a summary endpoint, or accepting one comment request per displayed task.

## 2. Section Critique

| Section | Label | Evidence | Minimal correction |
|---|---|---|---|
| Data Model | Right | Correctly places request/response models in `app/models.py`, follows its `ConfigDict(extra="forbid")` convention, and recognizes that `app/storage.py` uses an in-memory `_tasks` dictionary rather than real foreign keys. It also keeps server-generated fields out of `CommentCreate`. | None. |
| API Routes | Right | Specifies method, nested path, request/response bodies, status codes, validation failures, and missing-task behavior. The proposed `POST`/`GET /tasks/{task_id}/comments` routes fit the route structure in `app/main.py`. | Resolve ordering and task-deletion policy before treating those parts as final API behavior. |
| Tests | Right | Gives concrete pytest names grouped by happy path, validation, and edge cases. It follows the existing `TestClient`, fixture, and direct assertion style in `tests/conftest.py` and `tests/test_tasks.py`, and correctly notes that `tests/verify_a.py` is not the pytest suite. | Keep deletion tests conditional until cascade behavior is approved. |
| Frontend Changes | Right | Correctly identifies `frontend/index.html` as the single-file frontend, its create/edit modal, `BASE_URL`, and `escapeHtml` convention. Showing comments only for an existing task is consistent with needing a `task_id`. | Remove `tests/conftest.py` from the definite change list unless a new comment-specific fixture is actually needed; extending `storage._reset()` may be sufficient. |
| Migration Notes | Right | Correctly states that there is no database migration or persisted dataset to backfill because `app/storage.py` uses process-local memory. It identifies the actual storage-shape changes while preserving existing task responses. | None; keep future database notes explicitly hypothetical. |
| Open Questions | Needs-Resequencing | The questions are substantive and repo-grounded, especially deletion behavior, whitespace validation, ordering, endpoint scope, and comment counts. However, several earlier sections already recommend behavior that these questions leave undecided. | Promote the blocking decisions—scope, whitespace, list order, and deletion policy—to decision gates before finalizing routes, tests, and storage work. |

## 3. Generic vs Repo-Grounded Comparison

**Biggest difference:** The generic plan describes portable possibilities; the repo-grounded plan maps them to this project's actual files, in-memory storage, pytest fixtures, route conventions, and single-file frontend.

**Plan I would hand to a teammate and why:** The repo-grounded plan, after resolving its blocking open questions, because it identifies concrete change locations and preserves the existing task API contract.

**A task shape where generic chat is enough:** Early feature discovery or requirements brainstorming where architecture-specific implementation sequencing is not yet needed.
