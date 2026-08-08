# My Personal AI Coding Playbook

## 1. When I reach for AI first

- Task or situation: Scaffolding a well-defined piece of code (data models, CRUD endpoints, test suites) from a clear spec I already understand.
- Desired outcome: A first draft I can verify quickly against tests or manual checks, rather than writing boilerplate myself.
- Boundary or condition: I have a way to verify the output (tests, manual request, or file citation) before trusting it.

## 2. When I do not reach for AI

- Task or situation: Git operations (add, commit, push) and final judgment calls on AI's own output (grading security findings, verifying claims).
- Reason: I want full visibility into what's being versioned, and AI cannot grade its own work objectively — that judgment has to be mine.
- Alternative approach: Run git commands myself in the terminal; do my own manual review/scan before accepting AI's self-assessment.

## 3. My non-negotiables

- Privacy or security requirement: I will never paste real survey answers or login credentials into any AI tool.
- Quality or correctness requirement: AI claims about my repo must cite the actual file — generic or unsupported claims get rejected, not accepted at face value.
- Ownership or accountability requirement: I do not commit or push code I cannot explain in my own words.

## 4. My review rules

- What I verify: Every file Codex claims to have changed, and every factual claim about my repo (e.g., confirming repo visibility before accepting a risk grade).
- How I verify it: Run `git status` before staging anything, read diffs/previews before approving, and cross-check AI's claims against the actual repo when something seems off.
- What requires extra review: Anything AI marks as "Valid" or high-confidence in a security or governance context — I still run my own manual check before trusting the grade.

## 5. What I am still figuring out

- Open question: How much to trust AI-generated test coverage without independently writing some tests myself from scratch.
- Unresolved tradeoff: When a documented decision (like the ADR) and the actual code disagree, whether to trust the newer code or investigate why the drift happened before choosing either.
- Practice I want to evaluate: Running my own security/governance scan *before* seeing AI's findings, instead of after, to see if it changes what I notice.

## Decision Card

- For a new feature I reach for: GitHub Copilot (Ask mode) - scaffolding models, endpoints, and business logic from a clear spec, always applied manually.
- For a code review I reach for: Claude Code - but I still check whether flagged items are real issues myself, not just accept a "Useful" label at face value.
- For debugging I reach for: Claude as a step-by-step coach, walking through errors one step at a time.
- For infrastructure I reach for: Claude Code, but I run and read the raw output myself (build logs, health checks, whoami) rather than trusting its summary.
- I will never paste real student, staff, or faculty survey answers (course evaluations, satisfaction surveys, exit surveys) or login credentials into an AI tool.
- My one rule is: Verify before I trust - see the raw evidence, and grade every AI claim against the actual repo before accepting it.

---

*30-day reminder: Re-read this playbook on September 7, 2026. Am I still following it?*