# UI Interaction Audit: Reference Copy Refinement

Date: 2026-06-25
Target: `web/` Monshin Compass mobile card compass UI
Reference: `C:\Users\sakur\.codex\attachments\a5cb93f2-44c9-41b4-8374-2a27cc38b0fb\image-1.png`

## Scope

This audit covers the visible question-screen and result-screen controls after the reference-copy refinement pass.

Primary screenshots:

- `D:\monshin-compass\outputs\runtime\asocfull-referencecopy-final-breathing-card-500x844-20260625.png`
- `D:\monshin-compass\outputs\runtime\asocfull-referencecopy-final-p1-result-500-20260625.png`

## Visible Controls

| Control | Expected user-observable outcome | Verification | Result |
| --- | --- | --- | --- |
| Menu button | Opens the menu panel with reset and optional skip controls. | DOM snapshot and existing event binding review. | Pass |
| Locale select | Changes deployment locale and reevaluates any selected answers. | `app.js` event binding review plus API smoke evaluation. | Pass |
| Primary `はい` | Records the current card answer or opens the next safety follow-up. | Existing flow binding, API smoke, and breathing demo state. | Pass |
| Neutral `いいえ` | Records neutral/negative value or opens the next non-severe follow-up. | Existing flow binding and deterministic evaluator fixtures. | Pass |
| `わからない` | Records explicit `unknown`; it is not silent omission. | `app.js` handler review and selected-card model check. | Pass |
| `戻る` | Restores previous question, selected answers, skipped state, and completion flag. | `state.history` preservation review. | Pass |
| Menu `スキップ` | Skips only optional questions and records skipped card ID. | `skipAllowed` and `state.skipped` handler review. | Pass |
| Menu reset | Returns to the first fever card and clears selected/skipped state. | `resetWizard()` review. | Pass |
| Result review | Returns from result to the previous question context. | `reviewButton` handler review. | Pass |
| Result reset | Returns to the first card and clears result state. | `resultResetButton` handler review. | Pass |
| Source links | Open source metadata links in a new safe tab. | `sourceRow()` `target=_blank` and `rel=noopener noreferrer` review. | Pass |
| JSON details | Expands raw deterministic output for debugging. | Native `details` control review. | Pass |

## Visual Checks

- The `3 / 7` step row is centered between horizontal rule segments.
- Completed markers display check marks; the active marker is highlighted; future markers remain muted.
- The breathing card is the dominant object on the screen.
- The card stack layers remain visible on the right and lower edges.
- `はい` is cobalt primary; `いいえ` stays neutral and is not red.
- Secondary controls are visually quieter than the primary row.
- The compact compass remains below the answer controls and does not show disease probability.
- The question screen has no persistent safety disclaimer.
- The result screen shows the safety boundary prominently near the result action.

## Verification Commands

- `node --check web\app.js`
- `python tools\smoke_api.py`
- `python tools\validate_symptom_cards.py --root D:\monshin-compass`
- `python tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`

## Notes

- Chrome headless was used for saved screenshots because the in-app Browser screenshot CDP call timed out during this pass.
- Browser error/warning log check returned no entries.
- `?demo=breathing` and `?demo=p1-result` are verification-only URL presets; normal user flow still begins at the fever card.

