# AI Code Review Log — Part 4.5

Reviewed commit: `760f159` (docstrings + README rewrite)

| # | Issue | Severity | Category | Bucket | Reasoning |
|---|---|---|---|---|---|
| 1 | `create_task` docstring's Raises: section malformed (missing exception name) | medium | docs | Noise | Cosmetic formatting inconsistency, doesn't affect functionality or readers |
| 2 | `title: null` bug is documented but has no regression test | high | test | Useful | Real gap — a known bug should be pinned by a test so it can't silently change |
| 3 | Module docstring in `app/main.py` still says "Module 1 skeleton... will be added in later steps" | low | docs | Useful | Genuinely stale and misleading, contradicts the fully documented CRUD routes right below it |
| 4 | README rewrite bundled with docstring commit in one commit | low | scope | Noise | Accurate observation, but not worth fixing retroactively |

## My AI-review rule
I will use Claude Code review for a broad first pass, but I will only act on a comment after verifying it against the actual code myself.