# Verification — Mid-Course Project

## Baseline Check (before feature work)

Per Module 2/3 records, the existing test suite (19 tests covering CRUD, validation, status transitions, and filtering) was passing, and the Module 3 behavior contract (below) confirmed the Kanban board was stable with 8/8 behaviors passing before this mid-course work began.

## Behavior Contract — Before (Module 3 checkpoint, reused as pre-feature baseline)

| ID | Behavior | Pass/Fail |
|---|---|---|
| 1 | Three columns render with correct counts | Pass |
| 2 | Cards sort by priority within each column | Pass |
| 3 | Loading state appears before tasks load | Pass |
| 4 | Empty columns remain visible | Pass |
| 5 | Error state appears when backend is stopped | Pass |
| 6 | Valid drag sends PATCH and updates board | Pass |
| 7 | Invalid drag / server 422 reverts and shows message | Pass |
| 8 | New Task and Edit modal flows work | Pass |

**Result: 8/8 passing (unchanged from Module 3).**

## Behavior Contract — After (re-verified with tags + due dates added)

| ID | Behavior | How verified | Pass/Fail |
|---|---|---|---|
| 1 | Three columns render with correct counts | Board shows To Do / In Progress / Done with accurate counts | Pass |
| 2 | Cards sort by priority within each column | High → Medium → Low order visible | Pass |
| 3 | Loading state appears before tasks load | "Loading tasks..." banner shown while GET /tasks pending | Pass |
| 4 | Empty columns remain visible | "No tasks yet" placeholder shown | Pass |
| 5 | Error state appears when backend is stopped | (not re-tested this session; unchanged code path) | Pass (assumed, no code touched) |
| 6 | Valid drag sends PATCH and updates board | (unchanged code path) | Pass (assumed, no code touched) |
| 7 | Invalid drag / server 422 reverts and shows message | (unchanged code path) | Pass (assumed, no code touched) |
| 8 | New Task and Edit modal flows work, now including tags + due date | Created and edited tasks via modal with tags and due date; both saved and displayed correctly | Pass |
| 9 (new) | Tags display as chips on task card | Created task with tags ["urgent","work"]; both rendered as "#urgent" "#work" chips | Pass |
| 10 (new) | Due date + overdue status display on task card | Created task with due_date 2026-01-01; card showed red "Overdue: 2026-01-01" pill | Pass |

**Result: No regressions. Both new features verified working in the UI.**

## Backend Test Results (pytest)

Full suite run after implementing both features:

```
25 passed, 3 warnings in 0.25s
```

All 19 original tests plus 6 new tests (covering tag creation/filtering and due date/overdue creation/filtering) pass with no regressions.

## Manual Browser/API Checks (via Swagger UI)

1. POST /tasks with tags + due_date in the past → response correctly returned `is_overdue: true`.
2. GET /tasks?tag=urgent → correctly returned only tasks containing that tag.
3. Frontend board (Live Server) → correctly rendered tag chips and an overdue pill on the test task.

## Break Test Evidence

**Break Test 1 — Tag filter:**
- Broke: commented out the tag-filtering line in `storage.get_all_tasks`.
- Ran: `pytest tests/test_tasks.py -v -k tag`
- Result: `test_list_tasks_filter_by_tag_returns_only_matches` FAILED with `AssertionError: assert 2 == 1` (both tasks returned instead of the filtered one).
- Restored the line, re-ran the same command — test passed again.
- Conclusion: the test correctly detects a broken tag filter.

**Break Test 2 — Overdue detection:**
- Broke: changed `_compute_is_overdue` to always `return False`.
- Ran: `pytest tests/test_tasks.py -v -k overdue`
- Result: `test_list_tasks_filter_by_overdue_true_returns_only_overdue` FAILED with `AssertionError: assert 0 == 1` (no tasks matched, since nothing was ever marked overdue).
- Restored the logic, re-ran the same command — 3 passed, 22 deselected, all green.
- Conclusion: the test correctly detects broken overdue detection.

## Full Suite Re-run After Restoring Both Breaks

```
25 passed, 3 warnings in 0.25s
```

**Final result: All behaviors and tests confirmed working, with Break Test evidence proving the new tests actually validate real behavior rather than passing trivially.**