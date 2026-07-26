# Prompt Log — Mid-Course Project

## Workflow followed
Plan → constrain → implement in small steps → inspect → verify → test → document, using Claude as an AI pair-programmer in guided, step-by-step mode (one change at a time, manually verified before moving on).

## Key prompts and outcomes

1. **Feature selection**: Asked for the 2 simplest features from a list of 5 options given time constraints. AI recommended tags/labels + due dates/overdue filter as requiring the least new state/relationships.

2. **Planning docs**: Asked AI to draft user-stories.md (as-a-user statements) and mini-adr.md (technical decisions: tags as list[str], due_date as optional date, is_overdue computed not stored, filtering via query params).

3. **Backend implementation**: Requested one field/function change at a time across `app/models.py`, `app/storage.py`, `app/main.py` — adding tags/due_date fields, an `_compute_is_overdue()` helper, and query param filtering. Each step was applied manually and verified before the next.

4. **Frontend implementation**: Requested incremental changes to `frontend/index.html` — new form fields, JS field references, populate/reset logic, payload construction, and card rendering for tags/due date pills.

5. **Test writing**: Asked AI to write 6 new pytest tests matching the existing test file's style and conventions (arrange/act/assert, one behavior per test).

## Issues encountered and corrections
- A duplicate `_tasks` dict declaration and an indentation mismatch were introduced during manual copy-paste into `storage.py` — caught via VS Code's Problems panel and fixed by requesting the full corrected file rather than another patch.
- A test function's JSON body was accidentally deleted during manual paste, causing a syntax error and one test to silently merge into the previous test's body. Diagnosed using the Problems panel error location and pytest's failure traceback, then fixed by replacing the broken function with a corrected version.
- Confirmed all fixes by re-running `pytest tests/test_tasks.py -v` until 25/25 passed with no regressions.