# Technical Decision Note: In-Memory Task Storage

**Module:** 4 — Task Tracker API
**Status:** Final
**Scope:** `app/storage.py`, `app/main.py`, `app/models.py`

## 1. Context

The Task Tracker API needs somewhere to persist `Task` records between requests within a single running process, so that `POST /tasks`, `GET /tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`, and `DELETE /tasks/{id}` all operate on the same data.

This is a Module 1–4 learning project (see `CLAUDE.md`, `README.md`). The assignment scope through Module 4 covers building the API surface, request/response validation with Pydantic, status-transition business rules, and a Dockerized runtime — it does not include a database, authentication, or a deployment target. `app/storage.py` currently implements persistence as a single module-level dictionary, `_tasks: dict[str, TaskResponse]`, keyed by a UUID string generated in `add_task`.

## 2. Decision

Task storage is an in-memory Python dictionary (`_tasks` in `app/storage.py`), not a database. All CRUD operations (`add_task`, `get_all_tasks`, `get_task_by_id`, `update_task`, `delete_task`) read from and write to this single dict. There is no persistence layer, no ORM, and no file- or network-based storage of any kind. Data exists only for the lifetime of the running process: it is empty on startup, accumulates only what the current process has written, and is fully discarded on restart. `storage._reset()` clears it directly, and `tests/conftest.py` calls it via an autouse fixture so every test starts from an empty store.

## 3. Alternatives Considered

- **SQLite file-backed database** — would survive process restarts and give real query/filter semantics instead of Python list comprehensions. Rejected for this module: no ORM/database layer exists yet, and `CLAUDE.md` confirms `app/repository.py` is an empty placeholder stub, i.e. a DB-backed repository was consciously deferred, not accidentally skipped.
- **JSON file on disk** — a low-effort way to survive restarts without a real database. Rejected as adding file I/O and serialization concerns (concurrent writes, partial writes, schema drift) disproportionate to this module's scope.
- **External database (Postgres/etc.) via a hosted or containerized instance** — would require connection management, migrations, and credentials — explicitly out of scope per `CLAUDE.md` ("This module is not adding a database, auth, or deployment") and the README's stated limitations.

[VERIFY] I did not find a written record of this specific alternatives discussion (e.g. in `docs/midcourse/mini-adr.md`) beyond the tags/due-date ADR entries — this list is reconstructed from the current code and stated constraints, not from a prior decision log for storage itself.

## 4. Trade-offs

I chose in-memory storage because it kept the project simple to build and test — no database to install or manage, and every CRUD function in `storage.py` is just a handful of lines of pure Python over a dict, which makes the module easy to read end-to-end alongside `app/models.py` and `app/business_rules.py`. Test isolation was also trivial: `_reset()` plus the autouse fixture in `tests/conftest.py` gives every test a clean slate without spinning up or tearing down any external service.

But I was genuinely worried about losing task data, and at points during testing I actually did lose tasks after restarting the app or the container and had to re-add them by hand. That's the real cost of this decision, not just a theoretical one. On top of that:

- There's no concurrency safety — `_tasks` is a plain dict with no locking. [VERIFY] Under Uvicorn's default single-worker, async event-loop model this may not manifest as a practical race condition for this project's traffic patterns, but it is not a guarantee the code makes anywhere.
- It doesn't scale past one process — if the app were ever run with multiple workers or replicas, each would have its own independent `_tasks`, silently fragmenting data with no error raised.
- `update_task`'s use of `existing_task.model_copy(update=update_data)` bypasses Pydantic validation on the fields being merged in, which is how the documented `PATCH .../{id}` with `title: null` limitation exists (see README "Project conventions and current limitations"). This is a consequence of how the update path is implemented over the in-memory store, not a property of in-memory storage itself, but it's coupled to this decision closely enough to flag here.

## 5. Consequences

- Every deployment or restart is a full data wipe — anyone using the running API needs to know not to treat it as durable storage.
- The Dockerfile (`Dockerfile`, `docs/module4/docker-security-log.md`) runs this same in-memory model inside a container: stopping the container has the identical effect as restarting the local process — total data loss, by design, not by bug.
- `is_overdue` is computed on every read/write against `_tasks` rather than stored (per `docs/midcourse/mini-adr.md`), which was only a safe choice *because* there's no durable store to keep an independently-stored flag in sync with — the two decisions reinforce each other.
- Because there is no repository/database abstraction (`app/repository.py` is an empty stub), swapping in a real database later means writing that layer from scratch rather than swapping an implementation behind an existing interface — `app/storage.py`'s functions would need signature-compatible replacements, and every caller (`app/main.py`) would need no changes if the function signatures are preserved.
- Test suite correctness depends on the autouse `_reset()` fixture being called; forgetting to wire that fixture into any future test module would leak state across tests silently.

## 6. Open Questions

I'm not sure if a persistence layer is expected in a later module, or if in-memory storage is acceptable for the final grading. I also don't know yet whether the `title: null` bug should be fixed as part of a storage change, or separately.

- If a database is introduced later, does `app/repository.py` become the intended seam, or would `app/storage.py`'s existing function signatures just get reimplemented in place?
- Is there a need to support multiple Uvicorn workers/processes even for local dev, which the current single-dict design would silently break?

---

I would do this differently by adding a clear warning or reset confirmation in the UI, so it's obvious to anyone using the app that a restart wipes all data. For this project, in-memory storage was the right call — but I'd like to learn how to build a real database-backed version later, once I'm ready for that step.