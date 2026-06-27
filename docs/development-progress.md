# Development Progress

## Current Status

- Progress ID: `MONSHIN-PROGRESS-0011`
- Date: 2026-06-27
- Project: `D:\monshin-compass`
- Branch / Git state: `main` tracks `origin/main`; Shiki opened the source Git gate with `git add / commit / push`
- Active scope: ASOCFULL safe-run ticket closeout and source Git publication
- Current UI source of truth: `docs/smartphone-app-screen-spec.md`
- Current Web UI status: smartphone app shell runtime-confirmed after MSR recheck; keyboard/focus and ARIA/DOM sanity passed after source patch; real-device evidence remains fallback-only
- Local dev URL when server is running: `http://127.0.0.1:8765/`
- Latest safe-run ticket bundle: `outputs/2026-06-27-monshin-safe-run-ticket-bundle.md`
- Latest MSR closeout report: `outputs/2026-06-27-msr-007-progress-closeout-git-gate-decision.md`
- Latest Central Session Archive pointer: `D:\CentralSessionArchive\monshin-compass\2026-06-27-safe-run-ticket-bundle-session-archive.pointer.md`
- Latest Obsidian Vault capture: `D:\Obsidian\MyVault`, pushed commit `35cbdc0 Capture Monshin safe-run ticket archive`

## Completed Since Last Checkpoint

- Confirmed the current specification and roadmap position:
  - `docs/smartphone-app-screen-spec.md` remains the UI/product source of truth.
  - `docs/mobile-question-wizard-spec.md` remains prototype-era evidence, not current product authority.
  - Safety/core contracts remain above UI implementation.
  - Current position is post-runtime browser audit and pre-real-device/accessibility validation.
- Created a safe-run ticket bundle:
  - `outputs/2026-06-27-monshin-safe-run-ticket-bundle.md`
  - parent policy plus `MSR-001` through `MSR-007`
  - first ticket: `MSR-001 State And Diff Gate`
- Preserved the previous progress map:
  - `docs/progress-snapshots/MONSHIN-PROGRESS-0009_2026-06-27_before-safe-run-preservation.md`
- Created Central Session Archive evidence for this checkpoint:
  - source JSONL 1: `C:\Users\sakur\.codex\sessions\2026\06\27\rollout-2026-06-27T13-14-29-019f0749-37f7-71e0-b461-fe2851bd2452.jsonl`
  - source JSONL 2: `C:\Users\sakur\.codex\sessions\2026\06\27\rollout-2026-06-27T14-43-18-019f079a-80fe-74d0-88a3-bd531459d1cd.jsonl`
  - exactness: exact JSONL source bytes archived; user-facing restoration should be treated as `filtered-visible` because Codex JSONL contains internal records
  - manifest: `D:\CentralSessionArchive\monshin-compass\manifests\2026-06-27T054454Z0000-monshin-compass-safe-run-ticket-bundle-checkpoint.manifest.json`
  - raw gzip 001: `D:\CentralSessionArchive\monshin-compass\raw\2026-06-27\2026-06-27T054454Z0000-monshin-compass-safe-run-ticket-bundle-checkpoint-001.jsonl.gz`
  - raw gzip 002: `D:\CentralSessionArchive\monshin-compass\raw\2026-06-27\2026-06-27T054454Z0000-monshin-compass-safe-run-ticket-bundle-checkpoint-002.jsonl.gz`
  - SQLite index: `D:\CentralSessionArchive\monshin-compass\context_index.sqlite3`
  - ASCII pointer: `D:\CentralSessionArchive\monshin-compass\2026-06-27-safe-run-ticket-bundle-session-archive.pointer.md`
- Verified the archive manifest:
  - `verify_text=MONSHIN-SAFE-RUN-20260627`
  - `verify_text_found=true`
  - `fts_enabled=true`
  - `chunk_count=1022`
- Captured the checkpoint into Obsidian without mixing Vault dirt:
  - added `D:\Obsidian\MyVault\Codex\Projects\Monshin Compass\2026-06-27-monshin-compass-safe-run-ticket-bundle-session-archive.md`
  - updated `D:\Obsidian\MyVault\Codex\Projects\Monshin Compass\Monshin Compass Index.md`
  - staged only those two Vault files
  - committed and pushed Vault commit `35cbdc0`
- Executed all seven MSR tickets from the safe-run bundle:
  - `MSR-001` state/diff gate: go
  - `MSR-002` runtime regression recheck: pass
  - `MSR-003` keyboard/focus accessibility: pass after source fix
  - `MSR-004` screen-reader/ARIA sanity: pass as ARIA/DOM sanity
  - `MSR-005` real-device evidence: fallback-only, with touch-target finding
  - `MSR-006` safety copy and route boundary review: pass with deferred copy review
  - `MSR-007` progress closeout and Git-gate decision: complete
- Applied a small accessibility patch in `web/app.js`:
  - focus active screen headings after screen transitions
  - add source-link ARIA labels with title, publisher, and URL
  - add review edit-button ARIA labels with the current answer value
- Re-ran final closeout checks after the source patch:
  - static JavaScript parse
  - API smoke
  - symptom-card validation
  - JP emergency resolver fixtures
  - P0 and P1 evaluator fixtures
  - placeholder-action grep
  - whitespace diff check
  - runtime UI audit
  - safety-core diff
- Preserved the previous progress map before this update:
  - `docs/progress-snapshots/MONSHIN-PROGRESS-0010_2026-06-27_before-msr-git-publish.md`
- Shiki opened the source Git gate after MSR closeout:
  - stage only explicit intended paths
  - keep `outputs/`, `.codex/`, and `docs/progress-snapshots/` out of source Git

## Current Working State

- Source repo pre-publication base: `HEAD` and `origin/main` are both `fced469be78a45ddb12d9d5403ca79f83b8d8fbd`.
- Source repo commit/push gate: opened by Shiki for the current source repository.
- Source repo tracked paths intended for this source commit:
  - `.gitignore`
  - `docs/development-progress.md`
  - `web/app.js`
  - `web/index.html`
  - `web/styles.css`
- Source repo ignored/generated local evidence:
  - `.codex/`
  - `outputs/`
  - `docs/progress-snapshots/`
- Source repo ignored generated history:
  - `docs/progress-snapshots/MONSHIN-PROGRESS-0009_2026-06-27_before-safe-run-preservation.md`
  - `docs/progress-snapshots/MONSHIN-PROGRESS-0010_2026-06-27_before-msr-git-publish.md`
- Safety/core files were not intentionally changed:
  - `docs/triage-output-contract.md`
  - `docs/symptom-card-schema.md`
  - `docs/red-flag-rules.md`
  - `docs/jp-emergency-routing-resolver.md`
  - `docs/evidence-retrieval-contract.md`
  - `data/`
  - `tools/`
- Obsidian Vault pushed: `main` and `origin/main` include commit `35cbdc0`.
- Obsidian Vault still has unrelated pre-existing uncommitted/untracked changes outside the two Monshin files staged for this capture.

## Decisions / Constraints

- Keep authoritative:
  - deterministic evaluator outputs
  - `data/`
  - local validators and evaluator tools
  - JP emergency route resolver
- Keep current `web/` as an implementation of the smartphone app shell, not safety authority.
- The current `web/` delta is runtime-regression-confirmed by `MSR-002`, but physical real-device validation is still not done.
- The UI must not show disease identification, diagnosis ranking, treatment instructions, medication guidance, dosage, or reassurance that care is unnecessary.
- P0 emergency routing prioritizes `119`.
- `#7119` direct display requires resolver permission: `consultation_route.show_7119_direct=true` and a consultation phone.
- Source Git, Central Session Archive, and Obsidian Git are separate destinations.
- The source Git gate is open only for this explicit `git add / commit / push` request.

## Verification

- Passed and preserved from the prior runtime checkpoint:
  - `node --check .\web\app.js`
  - `python .\tools\smoke_api.py`
  - `python .\tools\validate_symptom_cards.py --root D:\monshin-compass`
  - `python .\tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
  - `python .\tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001`
  - `python .\tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`
  - `rg -n -e 'href="#"' -e 'javascript:void' -e 'console\.log' -e 'TODO' -e 'onclick=' web` returned no matches
  - runtime Playwright audit: 205 pass / 0 fail, 14 screenshots, 0 browser console errors/warnings
- Passed in this preservation turn:
  - source repo status inspected before preservation
  - session source candidates searched and selected by exact phrase evidence
  - previous progress map copied to `docs/progress-snapshots/`
  - Central Session Archive manifest created with `verify_text_found=true`
  - archive pointer created and re-readable
  - Vault note and index re-read
  - `git -C D:\Obsidian\MyVault diff --check -- <Monshin note> <Monshin index>` exited successfully with LF-to-CRLF warnings only
  - Vault staged diff contained only the intended two Monshin files
  - Vault commit/push completed at `35cbdc0`
- Passed in the MSR safe-run after source edits:
  - `node --check web\app.js`
  - `python tools\smoke_api.py`
  - `python tools\validate_symptom_cards.py --root .`
  - `python tools\resolve_jp_emergency_route.py --root . --run-fixtures`
  - `python tools\evaluate_symptom_case.py --root . --locale JP-13 --fixture SCHEMA-TC-001`
  - `python tools\evaluate_symptom_case.py --root . --locale JP-13 --fixture SCHEMA-TC-002`
  - `rg -n -e 'href="#"' -e 'javascript:void' -e 'console\.log' -e 'TODO' -e 'onclick=' web` returned no matches
  - `git diff --check -- web/index.html web/styles.css web/app.js docs/development-progress.md .gitignore`
  - `node .\.codex\runtime_ui_audit.cjs` with bundled `NODE_PATH`: `failed_count=0`, 14 screenshots
  - safety-core diff: no diff under `data/`, `tools/`, or core safety contracts
- Not run / not fully verified:
  - real-device mobile testing
  - real screen-reader / assistive-technology runtime pass
  - medical professional review
  - rights/legal review for raw source ingestion
  - source repo push verification, pending this Git gate

## Blockers / Risks

- Real physical-device behavior remains unverified; `MSR-005` is fallback evidence only.
- Screen-reader behavior still needs a dedicated assistive-technology runtime pass; `MSR-004` is ARIA/DOM sanity only.
- Mobile touch-target risk remains: several checked controls are below the 40px fallback threshold.
- Source/data mojibake still exists in fixture/data layers; UI avoids it, but future copy work must keep that boundary.
- Medical professional review and rights/legal review remain future work.
- Obsidian Vault still has unrelated dirt; future Vault commits must keep explicit pathspec staging.
- Source repo publication is authorized for this turn; verify staged diff, commit hash, push result, and final `main...origin/main` cleanliness.

## Experience Extracted

- A safe-run bundle should begin with a state/diff gate when the repo has both preservation dirt and local UI polish.
- For compressed sessions, archive both the pre-compaction and post-compaction JSONL when both contain checkpoint evidence.
- `outputs/` is the right place for local execution tickets when the source Git gate is closed.
- Obsidian Git can be safely pushed in a dirty vault by staging only the project note and project index.
- Progress, Central Session Archive, and Obsidian Git must report the same next action but stay on separate storage surfaces.
- When a safe-run report says "leave local dirty" and Shiki then explicitly opens the Git gate, re-check the diff and update the restart map before staging.
- ARIA/DOM sanity is useful evidence, but it must not be mislabeled as a real screen-reader pass.

## Next Best Action

1. Complete the open source Git gate:
   - stage only `.gitignore`, `docs/development-progress.md`, `web/app.js`, `web/index.html`, and `web/styles.css`
   - commit the staged source delta
   - push `main` to `origin/main`
   - verify the final worktree is clean and aligned
2. Then create and run a narrow touch-target fix ticket for:
   - header icon buttons
   - review edit buttons
   - evidence source links
3. Re-run `MSR-002`, `MSR-003`, and focused `MSR-005` checks after the touch-target patch.

## Resume Command

Read `docs/development-progress.md`, then read `outputs/2026-06-27-msr-007-progress-closeout-git-gate-decision.md`. Inspect `git status --short --branch -uall`. If the source Git gate has completed and `main...origin/main` is clean, continue with a narrow ASOCFULL touch-target fix ticket. If the source repo is still dirty, verify intended paths before staging.
