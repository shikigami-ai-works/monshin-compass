# Development Progress

## Current Status

- Progress ID: `MONSHIN-PROGRESS-0006`
- Date: 2026-06-25
- Project: `D:\monshin-compass`
- Branch / Git state: not a Git repository at checkpoint time
- Active scope: ASOCFULL 20-ticket smartphone app shell implementation
- Current UI source of truth: `docs/smartphone-app-screen-spec.md`
- Current Web UI status: rebuilt smartphone app shell; runtime browser QA not completed due browser policy blocker
- Local dev URL when server is running: `http://127.0.0.1:8765/`

## Completed Since Last Checkpoint

- Completed T01: rebuilt HTML app shell with required screens.
- Completed T02: added readable Japanese UI copy layer in `web/app.js`.
- Completed T03: added app state model and screen router.
- Completed T04: implemented Launch screen.
- Completed T05: implemented Region Confirmation screen.
- Completed T06: implemented Question Card flow.
- Completed T07: implemented Safety Confirmation interruption.
- Completed T08: implemented Review Answers screen.
- Completed T09: implemented Settings / Help screen.
- Completed T10: implemented Emergency Escape flow.
- Completed T11: wired evaluator API integration.
- Completed T12: implemented result/action rendering by priority.
- Completed T13: implemented Evidence / Source screen.
- Completed T14: enforced #7119 locale gating in UI copy.
- Completed T15: rebuilt responsive smartphone-first CSS.
- Completed T16: added source-level UI interaction audit:
  - `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-25_asocfull-20ticket-source.md`
- Completed T17: recorded implementation decisions in `docs/implementation-notes.md`.
- Completed T18: ran static/API/evaluator validation.
- Blocked T19: runtime browser screenshots/audit.
  - Browser automation rejected `http://127.0.0.1:8765/` and disallowed workaround through alternate browser surfaces.
- Completed T20: updated this progress checkpoint.

## Current Working State

- Pushed: none; project is not currently a Git repository.
- Local committed: none.
- Uncommitted: all files under `D:\monshin-compass` are plain filesystem artifacts.
- Runtime files changed in this checkpoint:
  - `web/index.html`
  - `web/styles.css`
  - `web/app.js`
- Docs changed in this checkpoint:
  - `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-25_asocfull-20ticket-source.md`
  - `docs/implementation-notes.md`
  - `docs/development-progress.md`
- Safety/core files were not changed:
  - `docs/triage-output-contract.md`
  - `docs/symptom-card-schema.md`
  - `docs/red-flag-rules.md`
  - `docs/jp-emergency-routing-resolver.md`
  - `docs/evidence-retrieval-contract.md`
  - `data/`
  - `tools/`

## Decisions / Constraints

- Keep authoritative:
  - deterministic evaluator outputs
  - `data/`
  - local validators and evaluator tools
  - JP emergency route resolver
- Keep current `web/` as an implementation of the smartphone app shell, not safety authority.
- User-facing UI copy is curated in `web/app.js` to avoid displaying mojibake fixture labels.
- The UI must not show disease identification, diagnosis ranking, treatment instructions, medication guidance, dosage, or reassurance that care is unnecessary.
- P0 emergency routing prioritizes `119`.
- `#7119` direct display requires resolver permission: `consultation_route.show_7119_direct=true` and a consultation phone.
- Runtime browser QA remains required before claiming final UI verification.

## Verification

- Passed:
  - `node --check web\app.js`
  - `python tools\smoke_api.py`
  - `python tools\validate_symptom_cards.py --root D:\monshin-compass`
  - `python tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
  - `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001`
  - `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`
  - source scan found no `href="#"`, `javascript:void`, `console.log`, `TODO`, or inline `onclick=` controls in `web/`
- Failed:
  - `git status --short` fails because `D:\monshin-compass` is not a Git repository
- Blocked:
  - in-app browser runtime rejected `http://127.0.0.1:8765/`
  - no screenshot evidence was captured in this pass
- Not run:
  - browser screenshot audit at `360/390/430`
  - runtime click-through audit
  - real-device mobile/accessibility testing
  - medical professional review
  - rights/legal review for raw source ingestion

## Blockers / Risks

- Browser policy currently blocks localhost UI verification for this target URL.
- The project is still not a Git repository, so there is no branch/commit history or source push path.
- Runtime UI may still have layout issues that static checks cannot reveal.
- Source/data mojibake still exists in fixture/data layers; UI avoids it, but future copy work must keep that boundary.
- Medical professional review and rights/legal review remain future work.

## Next Best Action

1. Complete runtime UI verification in an allowed browser session:
   - launch flow
   - region confirmation
   - question flow
   - safety confirmation after unknown safety answer
   - P0 emergency result
   - P1 Tokyo result with confirmed #7119
   - P1 Japan / area unconfirmed result without direct #7119 display
   - evidence/source screen
   - review/edit/re-evaluate path
   - settings locale change path
2. Capture screenshots at `360`, `390`, and `430` CSS px widths.
3. Update the UI interaction audit from source-level to runtime-confirmed.

## Resume Command

Read `docs/development-progress.md`, then read `docs/smartphone-app-screen-spec.md`. Treat the current `web/` as the active smartphone app shell implementation. Continue with runtime UI verification and screenshot capture only if the browser target is allowed; otherwise keep the browser blocker explicit and do not work around it.
