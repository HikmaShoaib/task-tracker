# Governance Worksheet — Module 5

## What I Shared with AI

| Item Shared | Context |
|---|---|
| Task Tracker source code (app/main.py, models.py, storage.py, business_rules.py) | Shared across Modules 1-5 for review, planning, and security audit |
| Test files and test output | Shared for review, debugging, and CI work |
| Dockerfile, CI YAML | Shared for Docker/CI setup and security review |
| README.md, AGENTS.md | Shared as project context for Codex |
| .env.example | Shared during security review (template only, no real secrets) |


## Risk Classification

| Item shared | Risk | Reason | Safer future version | Ambiguity to resolve |
|---|---|---|---|---|
| Task Tracker source code (`app/main.py`, `models.py`, `storage.py`, `business_rules.py`) | Low | This is public course-project code with no stated secrets, sensitive data, or proprietary logic. | Paste only the functions relevant to the question, preferably linking to the public repository instead of copying entire files. | Confirm that the pasted versions matched the public files and contained no uncommitted private additions. |
| Test files and test output | Low | Public tests and ordinary test results for a toy project are low risk. | Share the relevant public test and a short, sanitized failure excerpt rather than the complete output. | Test output could become Medium if it exposed a username, institutional filesystem path, private CI metadata, or other non-public environment details; High if it printed credentials or tokens. |
| Dockerfile and CI YAML | Low | Public build and CI definitions are public course-project code, assuming they contain only configuration already committed to the repository. | Link to the public files or paste only the relevant build stage or workflow step, keeping all secret values redacted. | This would be Medium if the pasted version contained non-public infrastructure details, and High if it contained actual credentials, tokens, or production configuration. |
| `README.md` and `AGENTS.md` | Low | Public project documentation and public AI-working instructions are low risk when they contain no private institutional or personal context. | Link to the public documents or paste a minimal project summary containing only context needed for the task. | Confirm that the shared `AGENTS.md` was the public version and that surrounding tool context did not expose private institutional paths, identities, policies, or unpublished course material; such additions could be Medium. |
| `.env.example` | Low | A public template containing placeholders and no real secrets is low risk, even though it reveals basic configuration structure. | Share only the required variable names with neutral placeholders such as `API_KEY=<redacted>`, after checking every value and comment. | It would be High if any example value was actually usable or copied from a real `.env`; private endpoints or account identifiers could make it Medium or High depending on sensitivity. |

## What I Received from AI

| Item Received | Context |
|---|---|
| Backend models, validators, routes, storage suggestions | Received across Modules 1-4 while building the Task Tracker API |
| Test suite (pytest, 26 tests) | Received in Module 2-3 for coverage of CRUD, validation, and edge cases |
| Docker setup, CI/CD workflow (GitHub Actions) | Received in Module 4 |
| Docstrings, README rewrite | Received in Module 4 documentation pass |
| Security audit findings (SEC-01 through SEC-09) | Received in Module 5 security review |
| AGENTS.md draft | Received in Module 5 setup |

## Traced Code Block

**Function:** `_compute_is_overdue` in `app/storage.py`

```python
def _compute_is_overdue(due_date: Optional[date], status: TaskStatus) -> bool:
    if due_date is None:
        return False
    if status == TaskStatus.DONE:
        return False
    return due_date < date.today()
```

**My explanation (in my own words):**

When there is no deadline for a task, a task cannot be past due. Because Python cannot compare None to a real date, this check also prevents the method from crashing when it attempts to compare an empty due date to today's date.