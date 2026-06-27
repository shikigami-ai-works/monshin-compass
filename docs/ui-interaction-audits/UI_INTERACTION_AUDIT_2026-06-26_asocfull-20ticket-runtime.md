# UI Interaction Audit: ASOCFULL 20-Ticket Smartphone App Shell Runtime

Date: 2026-06-26
Scope: `web/` smartphone app shell runtime audit after source-level ASOCFULL implementation
Launch method: `python app/server.py --host 127.0.0.1 --port 8765`
Target URL: `http://127.0.0.1:8765/`
Runtime evidence: `outputs/runtime/2026-06-26-runtime-ui-audit/`

## Summary

Result: runtime-confirmed pass.

- Runtime checks: 205 pass / 0 fail
- Browser console errors or warnings: 0
- Screenshots captured: 14
- Widths covered: 360, 390, 430 CSS px plus 1024 px desktop host
- Safety paths covered: Launch, Region Confirmation, Question flow, Safety Confirmation, P0, P1 Tokyo, P1 Japan area-unconfirmed, P3, Evidence, Review, Settings

One runtime issue was found and fixed during this audit:

- Finding: switching from a scrolled Result screen to Evidence preserved the page scroll position, causing header controls to render above the viewport in headless runtime inspection.
- Fix: `web/app.js` now resets `window.scrollTo({ top: 0, left: 0, behavior: "auto" })` inside `showScreen()`.
- Verification after fix: full runtime audit re-run with 205 pass / 0 fail.

## Commands And Checks Run

```powershell
node --check .\web\app.js
```

```powershell
python .\tools\smoke_api.py
python .\tools\validate_symptom_cards.py --root D:\monshin-compass
python .\tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures
python .\tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001
python .\tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002
```

```powershell
rg -n -e 'href="#"' -e 'javascript:void' -e 'console\.log' -e 'TODO' -e 'onclick=' web
```

Runtime automation:

```powershell
node .\.codex\runtime_ui_audit.cjs
```

The runtime command started the local server, waited for `/api/health`, drove Chromium through the target flows, captured screenshots, verified layout constraints, and stopped the server.

## Screenshot Evidence

| Screen | Width | Path |
|---|---:|---|
| Launch | 360 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/launch-360.png` |
| Launch | 390 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/launch-390.png` |
| Launch | 430 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/launch-430.png` |
| P0 result | 360 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/p0-result-360.png` |
| P0 result | 390 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/p0-result-390.png` |
| P0 result | 430 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/p0-result-430.png` |
| P1 Tokyo result | 390 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/p1-tokyo-result-390.png` |
| P1 Japan area-unconfirmed result | 390 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/p1-jp-unconfirmed-result-390.png` |
| P3 result | 390 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/p3-result-390.png` |
| Safety Confirmation | 390 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/safety-confirmation-390.png` |
| Evidence / Source | 390 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/evidence-390.png` |
| Review Answers | 390 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/review-390.png` |
| Settings / Help | 390 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/settings-390.png` |
| Desktop host P1 | 1024 | `outputs/runtime/2026-06-26-runtime-ui-audit/screenshots/desktop-host-p1-1024.png` |

## Audit Table

| UI element | Type | Visible location | Code reference | Connected handler/action | Expected behavior | Observable result | Verification method | Result | Fix needed | Manual confirmation needed |
|---|---|---|---|---|---|---|---|---|---|---|
| Back | Button | Header | `web/index.html` `#backIconButton`; `web/app.js` `goBack()` | `goBack` | Return to prior app screen or question state | Region/question/evidence/review/settings paths returned as expected | Runtime click + source mapping | Pass | No | No |
| Menu | Button | Header | `#menuButton` | menu toggle | Open and close menu panel | Menu opened without overflow, clipping, or overlap | Runtime click + layout check | Pass | No | No |
| Menu emergency | Button | Menu | `#menuEmergencyButton` | `showEmergencyResult` | Show P0 emergency result | P0 result shown with 119 route text | Runtime click | Pass | No | No |
| Menu review | Button | Menu | `#menuReviewButton` | `renderReview` | Open Review Answers | Review screen rendered answer rows | Runtime click + screenshot | Pass | No | No |
| Menu settings | Button | Menu | `#menuSettingsButton` | `showScreen("settings")` | Open Settings / Help | Settings screen opened | Runtime click + screenshot | Pass | No | No |
| Menu restart | Button | Menu | `#menuRestartButton` | `restart` | Clear session and return to Launch | Launch screen shown after restart | Runtime click | Pass | No | No |
| Start | Button | Launch | `#startButton` | `goRegion` | Move to Region Confirmation | Region screen shown | Runtime click | Pass | No | No |
| Launch emergency | Button | Launch | `#launchEmergencyButton` | `showEmergencyResult` | Show P0 emergency guidance | P0 result shown with 119 | Runtime click | Pass | No | No |
| Locale choice JP-13 | Button | Region | `[data-locale-choice="JP-13"]` | `setLocale("JP-13")` | Mark Tokyo / JP-13 selected | `aria-pressed` changed correctly | Runtime click + DOM check | Pass | No | No |
| Locale choice JP | Button | Region | `[data-locale-choice="JP"]` | `setLocale("JP")` | Mark area-unconfirmed selected | `aria-pressed` changed correctly | Runtime click + DOM check | Pass | No | No |
| Confirm region | Button | Region | `#confirmRegionButton` | `startQuestions` | Start question flow | Question screen at `1 / 7` | Runtime click | Pass | No | No |
| Region emergency | Button | Region | `#regionEmergencyButton` | `showEmergencyResult` | Show P0 emergency guidance | Direct click showed P0 result | Runtime click | Pass | No | No |
| Dynamic answer options | Button group | Question | dynamic `#answerList button` | `chooseAnswer` | Store answer and continue/evaluate | Normal path advanced through 7 questions to P3 | Runtime clicks | Pass | No | No |
| Question back | Button | Question | `#questionBackButton` | `goBack` | Return to previous question state | Progress restored from `2 / 7` to `1 / 7` | Runtime click | Pass | No | No |
| Question emergency | Button | Question | `#questionEmergencyButton` | `showEmergencyResult` | Show emergency result from question flow | Direct click showed P0 result | Runtime click | Pass | No | No |
| Safety answer options | Button group | Safety Confirmation | dynamic `#safetyAnswers button` | safety option apply + evaluate | Resolve ambiguity or escalate | Unknown dyspnea opened Safety Confirmation; strong dyspnea escalated to P0 | Runtime clicks | Pass | No | No |
| Safety back | Button | Safety Confirmation | `#safetyBackButton` | `showQuestion` | Return to triggering question | Direct click returned to the triggering question at `3 / 7` | Runtime click | Pass | No | No |
| Safety emergency | Button | Safety Confirmation | `#safetyEmergencyButton` | `showEmergencyResult` | Show P0 emergency guidance | Direct click showed P0 result | Runtime click | Pass | No | No |
| Result review | Button | Result | `#resultReviewButton` | `renderReview` | Open Review Answers | Review screen opened | Runtime click | Pass | No | No |
| Result evidence | Button | Result | `#resultEvidenceButton` | `showScreen("evidence")` | Open Evidence / Source | Evidence screen opened at top after scroll fix | Runtime click + screenshot | Pass | No | No |
| Result restart | Button | Result | `#resultRestartButton` | `restart` | Clear session and return to Launch | Direct click returned to Launch | Runtime click | Pass | No | No |
| Source link | Link | Evidence / Source | dynamic `sourceCard()` | external URL link | Open source in a safe new tab | Link has external URL, `_blank`, `noopener noreferrer`; click opened new tab with external URL using audit stub response | Runtime click + DOM check | Pass | No | No |
| Evidence back | Button | Evidence / Source | `#evidenceBackButton` | `showScreen("result")` | Return to Result | Result screen restored | Runtime click | Pass | No | No |
| Locale select | Select | Settings / Help | `#localeSelect` | used by `settingsApplyButton` | Choose route-display locale | `JP` selected before apply | Runtime select | Pass | No | No |
| Settings apply | Button | Settings / Help | `#settingsApplyButton` | `applySettings` | Re-resolve route display | P1 Tokyo changed to area-unconfirmed route without direct #7119 | Runtime select + click | Pass | No | No |
| Settings restart | Button | Settings / Help | `#settingsRestartButton` | `restart` | Restart session | Direct click returned to Launch | Runtime click | Pass | No | No |
| Settings back | Button | Settings / Help | `#settingsBackButton` | `goBack` | Return to previous app screen | Direct click returned to Result | Runtime click | Pass | No | No |
| Review edit | Button | Review Answers | dynamic `.review-row button` | set question index + `showQuestion` | Return to selected question for correction | Dyspnea edit opened question; severe answer re-evaluated to P0 | Runtime click | Pass | No | No |
| Review result | Button | Review Answers | `#reviewResultButton` | `showScreen("result")` | Return to Result | Direct click returned to Result | Runtime click | Pass | No | No |
| Review restart | Button | Review Answers | `#reviewRestartButton` | `restart` | Restart session | Direct click returned to Launch | Runtime click | Pass | No | No |

## Safety-Specific Runtime Results

- P0 result at 360 / 390 / 430 shows `119` priority.
- P1 Tokyo / JP-13 displays `#7119` and keeps the 119 caveat.
- P1 Japan / area-unconfirmed does not display direct `#7119`.
- Safety Confirmation appears after unknown dyspnea and can escalate to P0.
- Evidence screen states that priority comes from deterministic rules.
- Result screen safety boundary is visible.
- No visible layout horizontal overflow, clipped controls, or control overlap was found in the checked viewports.

## Remaining Not Verified

- Real-device mobile behavior.
- Screen-reader pass with an assistive technology runtime.
- Medical professional review.
- Rights/legal review for raw external source ingestion.

## Experience Extracted

- Runtime screen transitions need scroll-state verification; source-level handler mapping cannot reveal a preserved scroll offset.
- Evidence links should be tested as interactions, not only as `href` attributes.
- #7119 gating needs both positive and negative runtime cases; testing only Tokyo would miss the area-unconfirmed safety requirement.
- Screenshot evidence should pair automated layout checks with human visual inspection, because either method alone can miss a different class of UI failure.
