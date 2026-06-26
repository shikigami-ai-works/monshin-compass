# Card Compass Spec Session Ledger

Date: 2026-06-25
Project: `D:\monshin-compass`
Progress ID: `MONSHIN-PROGRESS-0002`
Scope: large-card mobile card compass UI specification lock

## Trigger

Shiki requested:

- `Progress`
- `Session Archive`
- `Obsidian`
- `GIT`

## Exactness

- Project files archived by the Central Session Archive are preserved from source bytes.
- Chat transcript is not available as exact source bytes in this workspace.
- Conversation context in this ledger is a best-effort visible summary.

## User-Visible Decision

The mobile UI direction is fixed to the A+C hybrid:

- A: illustrated two-choice body-part or situation card deck.
- C: compact compass/action meter with `観察`, `相談`, and `救急`.

The question screen no longer shows a persistent safety footer. That space is reserved for a larger illustration card.

The safety boundary appears prominently on the final result screen:

`診断・治療ではありません。強い症状は119を優先。`

## Primary Project Artifacts

- `docs/mobile-question-wizard-spec.md`
- `outputs/design/monshin-compass-mobile-card-compass-large-card-20260625.png`
- `docs/development-progress.md`

## Verification Performed

- `tools/validate_symptom_cards.py --root D:\monshin-compass`
- `tools/resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
- `tools/evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`
- Reference image SHA-256: `24BBA3DB405C474DA978A42BA6CFAF4454564E5343C709000A83C1C9C3E82ABD`
- Project Git check: `D:\monshin-compass` is not currently a Git repository.

## Archive Pointer

Central Session Archive manifest: `D:\遏･隴倬寔遨阪ヵ繧｡繧､繝ｫ・医Ξ繝ｳ・噂Nextchat_full_archive\.context-archive\manifests\2026-06-25T062245Z0000-monshin-compass-card-compass-spec-session-archive.manifest.json`
Central Session Archive index: `D:\遏･隴倬寔遨阪ヵ繧｡繧､繝ｫ・医Ξ繝ｳ・噂Nextchat_full_archive\.context-archive\context_index.sqlite3`

## Restore Path

1. Read `docs/development-progress.md`.
2. Open the Central Session Archive manifest named in that progress file.
3. Use the manifest source paths and raw gzip paths to restore archived source bytes if needed.
4. Continue with the Next Best Action in ASOCFULL unless Shiki narrows scope.
