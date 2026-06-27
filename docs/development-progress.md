# Development Progress

## Current Status

- Progress ID: `MONSHIN-PROGRESS-0008`
- Date: 2026-06-26
- Project: `D:\monshin-compass`
- Branch / Git state: `main` tracks `origin/main`; Git push gate opened by Shiki for this runtime UI checkpoint
- Active scope: ASOCFULL runtime UI verification, targeted smartphone app shell fix, and Git publication
- Current UI source of truth: `docs/smartphone-app-screen-spec.md`
- Current Web UI status: smartphone app shell runtime-confirmed in bundled Node Playwright; real-device and assistive-technology checks not completed
- Local dev URL when server is running: `http://127.0.0.1:8765/`

## Completed Since Last Checkpoint

- Read the active restart map and layered smartphone app spec.
- Confirmed Git state before work: `main...origin/main` with no tracked changes at start.
- Confirmed an allowed runtime verification path using existing bundled Node Playwright dependencies; no install was performed.
- Added an ignored local runtime audit harness:
  - `.codex/runtime_ui_audit.cjs`
- Captured runtime screenshot evidence under ignored output storage:
  - `outputs/runtime/2026-06-26-runtime-ui-audit/`
  - 14 screenshots covering 360 / 390 / 430 CSS px widths plus desktop host.
- Ran runtime browser interaction audit:
  - 205 checks passed
  - 0 failed
  - 0 browser console errors or warnings
- Verified required runtime paths:
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
  - source link new-tab behavior with external response stubbed for audit
- Found and fixed one runtime UI issue:
  - Result-to-Evidence navigation preserved body scroll and could clip header controls above the viewport.
  - `web/app.js` now resets scroll to the top in `showScreen()`.
- Added runtime-confirmed UI audit:
  - `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-26_asocfull-20ticket-runtime.md`
- Recorded implementation decision and experience:
  - `docs/implementation-notes.md`
- Shiki opened the Git gate for this checkpoint:
  - staged only intended tracked files
  - prepared commit/push on `main`

## Current Working State

- Pushed: this checkpoint is intended to be pushed to `origin/main` after commit succeeds.
- Local committed: pending this checkpoint commit.
- Tracked changes included in this checkpoint:
  - `web/app.js`
  - `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-26_asocfull-20ticket-runtime.md`
  - `docs/implementation-notes.md`
  - `docs/development-progress.md`
- Ignored/generated local evidence:
  - `.codex/runtime_ui_audit.cjs`
  - `outputs/runtime/2026-06-26-runtime-ui-audit/`
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
- User-facing UI copy remains curated in `web/app.js` to avoid displaying mojibake fixture labels.
- The UI must not show disease identification, diagnosis ranking, treatment instructions, medication guidance, dosage, or reassurance that care is unnecessary.
- P0 emergency routing prioritizes `119`.
- `#7119` direct display requires resolver permission: `consultation_route.show_7119_direct=true` and a consultation phone.
- Runtime audit harness is local ignored evidence for now, not a committed product test suite.
- Git gate for this checkpoint is open; stage only intended tracked files and keep ignored evidence out of source Git.

## Verification

- Passed:
  - `node --check .\web\app.js`
  - `python .\tools\smoke_api.py`
  - `python .\tools\validate_symptom_cards.py --root D:\monshin-compass`
  - `python .\tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
  - `python .\tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001`
  - `python .\tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`
  - `rg -n -e 'href="#"' -e 'javascript:void' -e 'console\.log' -e 'TODO' -e 'onclick=' web` returned no matches
  - runtime Playwright audit: 205 pass / 0 fail, 14 screenshots, 0 browser console errors/warnings
  - visual inspection of key screenshots: launch, P0, P1 Tokyo, P1 area-unconfirmed, Evidence, Review, Settings, desktop host
- Failed:
  - none after scroll-reset fix
- Not run:
  - real-device mobile testing
  - screen-reader / assistive-technology runtime pass
  - medical professional review
  - rights/legal review for raw source ingestion

## Blockers / Risks

- The previous in-app browser localhost blocker was not retried; this checkpoint used an allowed local Playwright route from bundled dependencies.
- Runtime UI is now browser-confirmed, but not real-device-confirmed.
- Screen-reader behavior still needs a dedicated pass.
- Source/data mojibake still exists in fixture/data layers; UI avoids it, but future copy work must keep that boundary.
- Medical professional review and rights/legal review remain future work.
- This checkpoint is prepared for commit/push; ignored evidence must remain out of source Git.

## Next Best Action

1. Complete commit and push for the staged runtime-confirmed checkpoint.
2. After push, verify `main...origin/main` is clean.
3. If continuing validation after Git, run a focused real-device / accessibility pass:
   - mobile hardware viewport check
   - keyboard/focus order check
   - screen-reader sanity check
   - manual external source-link confirmation in a normal browser

## Resume Command

Read `docs/development-progress.md`, then read `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-26_asocfull-20ticket-runtime.md` and `docs/smartphone-app-screen-spec.md`. Inspect `git status --short --branch -uall`. Treat current `web/` as the active smartphone app shell implementation. If the commit/push has completed, continue with focused real-device/accessibility validation when Shiki asks.
