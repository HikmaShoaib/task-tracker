# Verification — Mid-Course Project

## Manual Verification (via Swagger UI)

| # | Behavior | How verified | Result |
|---|----------|---------------|--------|
| 1 | Task can be created with tags and due_date | POST /tasks with tags=["urgent","work"], due_date="2026-01-01" | Pass — response included tags, due_date, is_overdue=true |
| 2 | is_overdue correctly computed for past due date | Same request as above | Pass — is_overdue: true |
| 3 | GET /tasks?tag=urgent filters correctly | Created 2 tasks, filtered by tag | Pass — only matching task(s) returned |
| 4 | Frontend displays tags and due date on cards | Opened frontend, viewed board | Pass — "#urgent", "#work", "Overdue: 2026-01-01" pill shown correctly |
| 5 | Frontend New Task / Edit modal supports tags + due date input | Created/edited task via modal | Pass — fields saved and reflected on card |

## Automated Verification (pytest)

All 25 tests pass, including 6 new tests covering the two features:
- `test_create_task_with_tags_and_due_date_returns_201`
- `test_create_task_without_tags_or_due_date_defaults`
- `test_future_due_date_is_not_overdue`
- `test_done_task_with_past_due_date_is_not_overdue`
- `test_list_tasks_filter_by_tag_returns_only_matches`
- `test_list_tasks_filter_by_overdue_true_returns_only_overdue`

**Result: 25/25 tests passing. No regressions in existing behavior.**