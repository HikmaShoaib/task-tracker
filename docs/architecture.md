# Task Tracker Architecture

## 1. What the app does

Task Tracker is a FastAPI REST API that provides a health check and CRUD operations for tasks. Clients can create, retrieve, filter, partially update, and delete tasks. Filtering supports status, priority, tag membership, and overdue state. (`app/main.py`)

## 2. Data model

The main entity is `Task`, represented by three Pydantic models:

- `TaskCreate`: title, description, status, priority, assignee, tags, and due date.
- `TaskUpdate`: optional versions of the creation fields for partial updates.
- `TaskResponse`: adds UUID-based `id`, derived `is_overdue`, `created_at`, and `updated_at`.
- Status values: `ToDo`, `InProgress`, `Done`.
- Priority values: `Low`, `Medium`, `High`.

New tasks default to `ToDo`, `Medium` priority, an empty description and tag list, and no assignee or due date. (`app/models.py`)

## 3. Request flow

For `POST /tasks`, FastAPI parses the request into `TaskCreate`. Pydantic rejects extra fields and validates the required title by trimming whitespace, rejecting blank values, and enforcing a 200-character maximum. The route calls `storage.add_task`, which generates a UUID, creates UTC timestamps, calculates overdue state from the local date, constructs a `TaskResponse`, stores it in the module-level dictionary, and returns it with HTTP 201. (`app/main.py`, `app/models.py`, `app/storage.py`)

## 4. Key files

- `app/main.py` — creates the FastAPI app, configures CORS, and defines health and task routes.
- `app/models.py` — defines task schemas, enums, defaults, and title validation.
- `app/storage.py` — implements in-memory CRUD, filtering, sorting, UUID creation, and overdue calculation.
- `app/business_rules.py` — referenced by the update route for status-transition validation; its implementation is not visible from the files I read.
- Frontend entry file — not visible from the files I read.

## 5. Conventions

- **Validation:** Pydantic models forbid extra fields; titles are trimmed and constrained to 1–200 characters. Partial updates apply only explicitly supplied fields.
- **Storage:** Tasks reside in a module-level `dict[str, TaskResponse]`; no durable persistence is visible from the files I read.
- **Errors:** Missing task IDs produce HTTP 404. Invalid status transitions produce HTTP 422 through the referenced business-rule function. Request-model validation occurs before route execution.
- **Derived data:** `is_overdue` is false without a due date or when status is `Done`; otherwise it compares the due date with the current local date.
- **Frontend/backend interaction:** The API enables CORS for `null` and localhost/127.0.0.1 on ports 5500 and 8000. The frontend implementation and its request behavior are not visible from the files I read.

## 6. Not visible or assumptions

Authentication, authorization, deployment architecture, database support, frontend structure, tests, dependency versions, status-transition rules, production CORS policy, logging, monitoring, and concurrency or multi-process behavior are **not visible from the files I read**.

## Coverage gaps

Strategy C could not confirm the frontend implementation, test coverage, or the implementation inside `app/business_rules.py`. Consult `docs/architecture-B.md` for broader context in those areas, while treating its summary-derived claims as items to verify against the relevant source files.

## Strategy comparison

| Strategy | What it got right | What it got wrong, missed, or invented | Best-suited task shape |
|---|---|---|---|
| **A — Minimal context** | Produced the richest end-to-end narrative, covering the API, frontend, storage, validation, tests, ADR, and known limitations. Its creation flow is concrete and easy to follow. | It makes several uniquely specific claims that the other drafts do not substantiate: the frontend closes its form and reloads tasks after creation, the frontend uses `localhost:8000`, and the ADR conflicts with the implementation over overdue calculation. Because the draft does not attribute claims to source files, these details are difficult to distinguish from inference. Its frontend URL also conflicts with B's `127.0.0.1:8000`. | Fast, exploratory summaries where broad coverage matters more than strict traceability and the output will be checked afterward. |
| **B — Structured context** | Gives the most balanced repository-level overview. It covers the frontend, backend, persistence, filters, sorting, status transitions, placeholder modules, governance context, and the distinction between confirmed behavior and unverified runtime results. | It treats `AGENTS.md` as a “key file” in the application architecture even though the draft describes it as a repository-governance and behavior summary. Several detailed claims—especially the exact transition chain, query behavior, and frontend URL—appear to come from structured summaries rather than source attribution. Its final caveat admits that runtime behavior was not independently verified. | Broad orientation documents, onboarding summaries, and governance work that must cover many parts of a repository consistently. |
| **C — Targeted context** | Provides the clearest claim-to-source traceability by citing `app/main.py`, `app/models.py`, and `app/storage.py` alongside the relevant sections. It carefully marks unseen material instead of filling gaps, and gives a precise, bounded account of the request flow and active in-memory storage. | Its narrow anchors leave major architectural gaps: the frontend, tests, dependency information, and actual status-transition rules are not covered. It mentions `app/business_rules.py` but cannot describe its implementation. Consequently, it is less complete as a repository-wide architecture overview. | Focused technical documentation where factual precision, provenance, and controlled scope matter more than exhaustive repository coverage. |

## Verdict

I chose **Strategy C, targeted context**, for the final architecture document because its important claims are tied directly to the files that support them, and it explicitly marks what its anchor set could not establish. Strategy B offered broader coverage, but C provided a safer foundation for architecture documentation by reducing summary-derived assumptions; any missing section can be added later by deliberately selecting another relevant anchor file.

## Context-engineering rule

For focused architecture documentation that requires source-level accuracy, I use targeted context because a small set of anchor files makes each claim traceable and exposes coverage gaps. For broad repository orientation or governance summaries, I use structured context because it captures cross-cutting conventions and components more efficiently, while treating unverified summary claims as leads rather than evidence.
