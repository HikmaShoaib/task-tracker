# Module 4 - Tool-Fit Reflection

## GitHub Copilot (Ask mode)

I used Copilot's Ask mode throughout the course to work through the structured prompt library — asking it to explain existing code, draft data models, generate CRUD endpoints and business rules, and write tests, all from the strict, file-referenced prompts provided in each module. Because Ask mode doesn't edit files directly, every suggestion had to be reviewed and applied by hand, which kept me in control of what actually changed in the codebase. This made it a good fit for the "ask, inspect, run, test, refine" loop the course emphasizes, though it meant more manual copy-pasting compared to an agent that edits in place.

## Cursor

I haven't used Cursor for this project.

## Claude Code

I used Claude Code for the repo-level engineering work in Module 4: setting up CLAUDE.md, generating and inspecting the CI workflow, building the Dockerfile, adding docstrings and rewriting the README, running an AI-assisted code review, and drafting the technical decision note. Because Claude Code can read, edit, and run commands across the whole repo, it was suited to this broader scope in a way Copilot's Ask mode wasn't — but it also meant I had to be more deliberate about reviewing diffs and verifying claims (like the README claim-vs-reality audit) before trusting the output.

## Module 4 Deliverable Checklist

| Part | Deliverable | Status | Evidence |
|---|---|---|---|
| 4.1 | Claude Code setup + CLAUDE.md | Done | CLAUDE.md committed, verified against code |
| 4.2 | CI pipeline (green→red→green) | Done | `.github/workflows/ci.yml`, commits efcfd62, 21570e3 |
| 4.3 | Docker containerization | Done | Commit 0c9c554, `docs/module4/docker-security-log.md` |
| 4.4 | Documentation (docstrings, README, claim-vs-reality) | Done | Commit 760f159 |
| 4.5 | AI-assisted code review triage | Done | Commit 7d23ef6, `docs/module4/review-log.md` |
| 4.6 | Technical decision note | Done | Commit b6e82c7, `docs/decisions/in-memory-task-storage.md` |
| X1 | Tool-fit reflection | Done | This file |
