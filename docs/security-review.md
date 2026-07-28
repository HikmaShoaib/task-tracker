# Module 5 Security Review

This document consolidates the read-only AI security audit, the student's grading, the manual scan, the reconciliation, and the prioritized backlog.

## 1. AI Findings (with grades)

| ID | Severity | Grade | File / location | Finding | Evidence | Suggested next step | Grading reason |
|---|---|---|---|---|---|---|---|
| SEC-01 | High if network-exposed; accepted course limitation locally | Valid | `app/main.py:59-199`; `README.md:138` | No authentication or authorization protects task data or mutations. Any client that can reach the API can list, create, modify, and delete every task. | All CRUD routes are public and have no authentication dependency. The README explicitly documents the absence of authentication. | Keep the service local-only as documented. Before shared or production deployment, define an authentication scheme and enforce authorization on every task route. | This is a real production risk but an intentional course-scope limitation, not necessarily a required Module 5 code fix. |
| SEC-02 | Medium | Valid | `app/models.py:23-29`, `app/models.py:68-74` | Most user-controlled text and collection fields are unbounded. | Only `title` has a 200-character limit. `description`, `assignee`, individual tag strings, and tag count have no application-level limits on creation or update. | Establish documented maximum lengths and tag-count limits. Add request-size limits at the serving or proxy layer if the app leaves local use. | Large accepted payloads can consume memory. The practical risk is low for local coursework but real outside that scope. |
| SEC-03 | Medium | Valid | `app/storage.py:7`, `app/storage.py:30-46`, `app/storage.py:72-81` | Storage and list responses have no capacity or pagination bounds, enabling memory and response-amplification exhaustion. | Every task remains in a process-wide dictionary. `GET /tasks` copies, filters, sorts, and returns the entire collection, while task creation has no quota or rate control. | For deployment, add pagination, request or rate limits, and bounded or persistent storage with quotas. | This is a concrete scalability and resource-control limitation outside the small local learning context. |
| SEC-04 | Medium | Valid | `app/models.py:68`, `app/models.py:99-109`, `app/storage.py:127-137`, `tests/test_tasks.py:136-145` | `PATCH` accepts `title: null`, violating the declared invariant that a task title is a string. | `TaskUpdate.title` is optional and its validator passes `None`. Storage applies the value with `model_copy(update=...)`, which bypasses validation. A test explicitly pins this behavior as buggy. | When separately authorized, reject explicit null titles and update the regression test to expect HTTP 422. | This is a demonstrated and already documented validation defect rather than intended behavior. |
| SEC-05 | Medium for a local desktop API | Valid | `app/main.py:25-36` | CORS trusts the opaque `"null"` origin while allowing every HTTP method and header. | `"null"` can represent local `file:` pages and sandboxed documents. Such pages may make browser requests to the localhost API. Credentials are not enabled, which limits impact. | Confirm whether direct `file:` use is required. If not, remove `"null"` and allow only the trusted frontend origin, methods, and headers. | A malicious local page could interact with the reachable unauthenticated API. If direct file access is intentional, this is an accepted local-development tradeoff. |
| SEC-06 | Medium | Valid | `requirements.txt:1-6`, `.github/workflows/ci.yml:20-23` | Dependency installation is not reproducible and has no visible vulnerability-scanning step. | Every package has only a lower bound. CI upgrades pip and installs whichever newer transitive versions resolve at run time. No lock file, hashes, audit step, or dependency-update policy was found. | Introduce a reviewed lock or constraints file, preferably with hashes, and add a dependency audit and update workflow. | The reproducibility and supply-chain-control limitation is established. No specific vulnerable dependency is claimed without an advisory scan. |
| SEC-07 | Low | Noise | `.github/workflows/ci.yml:13-16`; `Dockerfile:2,11` | CI actions and container base images use mutable version tags rather than immutable digests or commit SHAs. | Actions use `actions/checkout@v4` and `actions/setup-python@v5`; both Docker stages use `python:3.11-slim`. | If required by the rubric or a future production policy, pin actions to reviewed SHAs and images to reviewed digests. | Technically true, but generic supply-chain hardening for a local learning project. No compromised action, unexpected image change, or production exposure was demonstrated. |
| SEC-08 | Low | Noise | `frontend/index.html:495`; `README.md:49-51,140` | The frontend assumes an unencrypted, fixed localhost API endpoint. | `BASE_URL` is hardcoded to `http://localhost:8000`, and the repository documents local frontend use and no production deployment configuration. | For a future deployment, use a same-origin relative API path or environment configuration over HTTPS. | This is principally a deployment and functionality limitation. Under HTTPS, mixed-content blocking would normally prevent the request rather than directly expose data. |
| SEC-09 | Low | Noise | `app/main.py:168-175`; `app/storage.py:123-137` | Multi-step updates are not synchronized, so concurrent requests may overwrite one another or use stale state. | The route reads and validates status before a separate storage read-copy-write operation. No lock, transaction, or version check exists. | If concurrent shared operation enters scope, make validation and update atomic and add a reproducible concurrency test. | The issue is mainly data integrity and reliability in this unauthenticated, single-process learning app. No security-boundary bypass or reproduced failure was demonstrated. |

### Files inspected

- `AGENTS.md`
- `app/main.py`
- `app/models.py`
- `app/storage.py`
- `app/business_rules.py`
- `app/repository.py`
- `app/schemas.py`
- `app/exceptions.py`
- `tests/test_tasks.py`
- `tests/conftest.py`
- `tests/verify_a.py`
- `requirements.txt`
- `Dockerfile`
- `.dockerignore`
- `.github/workflows/ci.yml`
- `frontend/index.html`
- `.env.example`
- `README.md`

No `pyproject.toml`, compose file, or additional GitHub workflow was found in the inspected inventory. `app/repository.py`, `app/schemas.py`, and `app/exceptions.py` contained placeholder stubs only.

### Categories where the audit found no issue

- Status and priority use explicit enums, and invalid values are tested.
- Request models forbid unknown fields.
- Title creation validation trims whitespace and enforces nonblank and 200-character rules.
- No hardcoded credentials, tokens, private keys, or other secrets were found. `.env.example` contains only non-secret template settings.
- No application-level broad exception handlers or explicit stack-trace exposure were found.
- The frontend escapes API-provided values before interpolating them into task-card HTML; error text is rendered with `textContent`.
- The Docker runtime uses a non-root user, and `.dockerignore` excludes `.env` files, version-control data, virtual environments, and caches.
- The container command does not enable Uvicorn reload mode.

### Audit assumptions and limits

- This was a static, read-only audit. No files were changed during the audit, tests were not run, containers were not built, and endpoints were not fuzzed.
- No live dependency advisory lookup or resolved-environment scan was performed; specific vulnerable package versions are not confirmed.
- Reverse-proxy controls, host firewall rules, GitHub repository settings, branch protections, deployment environment, and external secret management were not visible.
- Severity for authentication, CORS, capacity, and concurrency assumes possible network or multi-user exposure. The repository identifies itself as a local learning project, so immediate risk within its intended scope is lower.

## 2. My Manual Findings

| ID | Finding | File evidence | Assessment |
|---|---|---|---|
| MANUAL-01 | Direct execution with `python app/main.py` hardcodes `reload=True`, a development-only setting that could silently remain active outside development if someone bypasses the documented Uvicorn command. | `app/main.py:202-206` calls `uvicorn.run(..., host="127.0.0.1", port=port, reload=True)`. | Confirmed by file evidence. This is a low-risk development-configuration issue because the documented Uvicorn command and the Docker command do not use this direct-execution path. |

## 3. Reconciliation (Agreement / AI-only / You-only)

| Agreement | AI-only | You-only |
|---|---|---|
| None | **Valid:** SEC-01 no authentication; SEC-02 unbounded fields; SEC-03 unbounded storage and listing; SEC-04 nullable-title defect; SEC-05 permissive `"null"` CORS origin; SEC-06 unpinned dependency resolution. **Noise:** SEC-07 mutable CI and image tags; SEC-08 fixed HTTP frontend URL; SEC-09 concurrency risk. | **MANUAL-01:** Direct execution enables `reload=True` unconditionally at `app/main.py:205`. The manual scan caught this alternate startup-path configuration issue and the AI audit did not. |

### Observation

AI coverage was broad, emphasizing production hardening, resource limits, dependency governance, and known validation weaknesses; several findings mattered mainly outside the course's local-use scope.  
The manual scan was narrower but caught a concrete execution-path configuration issue that the AI missed, illustrating the value of checking alternate startup paths.

## 4. Top-3 Backlog

| Rank | Finding | Why it matters | Suggested owner | Next action |
|---:|---|---|---|---|
| 1 | SEC-01: No authentication or authorization | Any client that reaches the service can read, change, or delete all tasks. This is acceptable only while the application remains a trusted local learning project. | Course/project owner and backend | Document a firm local-only boundary. Before shared deployment, select an authentication model and require authorization on every task route. |
| 2 | SEC-02 and SEC-03: Unbounded inputs, storage, and list responses | Arbitrarily large fields, unlimited task creation, and full-collection responses create a credible memory and response-amplification risk. | Backend | Define field and tag limits and pagination requirements, then add bounded validation and list parameters in a separately approved implementation task. |
| 3 | SEC-05: CORS permits the `"null"` origin | Local or sandboxed pages may interact with the unauthenticated localhost API, including mutation endpoints. | Backend and frontend | Confirm whether direct `file:` access is required. If not, remove `"null"` and restrict CORS to the frontend's explicit served origin, methods, and headers. |
