# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: yes
- Docs-first/read-first guardrail included: yes
- Unexpected app/frontend edits rule included: yes

AGENTS.md (created in Module 5.1) documents the confirmed Python/FastAPI stack, run/test commands, business rules from the actual code, and explicit Module 5 guardrails: read-only by default, docs/ only unless approved, no app/ changes without explicit approval, and citation requirements for any repo claims.

## AI code review mini-log

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| Stale module docstring in app/main.py still said "Module 1 skeleton" | Useful | Docstring no longer matched the current state of the project after Modules 2-4 | Updated the docstring and FastAPI `description=` to reflect current scope |
| `title: null` PATCH bug was undocumented by any test | Useful | A known limitation with no regression test risked silent breakage later | Added `test_patch_title_null_is_accepted_and_returns_null_title` to pin the behavior |
| Formatting inconsistency in one `Raises:` docstring section | Noise | Cosmetic only, no functional or documentation-accuracy impact | Left as-is |
| Note about bundled commit scope | Noise | Not tied to a specific defect or risk; a process comment, not a finding | Left as-is |

(Full log: `docs/module4/review-log.md`, commit `7d23ef6`)

## AI security mini-review

| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| PATCH /tasks/{id} accepts title: null, bypassing validation | app/models.py, app/storage.py (model_copy bypasses validation), tests/test_tasks.py | Valid | Demonstrated defect, pinned by regression test | Documented as known limitation; fix is out of scope for this project (no new app/ changes without approval) |
| No authentication or authorization on any task route | app/main.py, README.md | Valid | Real risk if ever deployed beyond local use; intentional course-scope decision | Keep documented as a scope limitation; would require an auth scheme before any shared deployment |
| CORS allows the "null" origin alongside wildcard methods/headers | app/main.py | Valid | Could allow local/sandboxed pages to interact with the unauthenticated API | Documented; removal recommended if `file:` frontend access is not required |

(Full audit and grading: `docs/security-review.md`, commit `947cf3a`)

## Manual security check

I manually reviewed `app/main.py` and found that the `if __name__ == "__main__":` block hardcodes `reload=True`, a dev-only setting. If someone runs the app with `python -m app.main` instead of the documented `uvicorn` command, it silently starts in auto-reload mode. This was not flagged by the AI security audit — I found it independently by reading the direct-execution path. Logged as MANUAL-01 in `docs/security-review.md`.

## One AI output I rejected or corrected

During Module 5's governance risk classification, Codex initially graded my source code, tests, Dockerfile/CI, and documentation sharing as Medium risk, reasoning that it could not confirm the repository was public. I corrected this by checking `github.com/HikmaShoaib/task-tracker` myself and confirming the repo is public. I asked Codex to re-grade using that fact, and it correctly reclassified those items as Low risk per its own rubric — but I did not accept its first answer, since it was based on an unconfirmed assumption rather than a checked fact.

## Three AI usage rules

1. Never paste: Real student answers to instructor course evaluations or any other surveys (satisfaction surveys, exit surveys), and login credentials.
2. Always verify: Every file an AI tool claims to have changed, and every factual claim about my repo (e.g., confirming repo visibility before accepting a risk grade), before accepting the output.
3. Record AI contributions by: Naming the specific artifact or finding received (models, validators, routes, tests, documentation, security findings) in the relevant docs/ file for that piece of work.

## Ownership statement

I am comfortable submitting this repo as my own work because every AI-generated claim about it was checked against the actual files, tests, or running app before I accepted it — not just read and trusted. I independently found and documented a security issue (`reload=True`) that AI missed, corrected an AI risk-grading error after checking my repo's visibility myself, and can explain the core business logic (like the overdue-calculation function) in my own words rather than just repeating an AI-generated summary. The known limitations documented here (the `title: null` bug, no authentication) are accurately described, not hidden, and I understand why each one exists.