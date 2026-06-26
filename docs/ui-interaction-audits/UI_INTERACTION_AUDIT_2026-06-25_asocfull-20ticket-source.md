# UI Interaction Audit: ASOCFULL 20-Ticket Smartphone App Shell

Date: 2026-06-25  
Scope: `web/` smartphone app shell source-level audit after layered spec implementation  
Launch method: `python app/server.py --host 127.0.0.1 --port 8765`  
Target URL: `http://127.0.0.1:8765/`

## Summary

This audit checks the rebuilt smartphone app shell controls for intended user-observable outcomes. Runtime browser interaction and screenshots were attempted through the in-app browser path, but browser security policy rejected use of `http://127.0.0.1:8765/`. Per policy, no Playwright/Chrome workaround was used.

Result:

- Source-level control mapping: pass
- API/static validation: pass
- Runtime click/screenshot confirmation: manual confirmation needed

## Commands And Checks Run

```powershell
node --check D:\monshin-compass\web\app.js
```

```powershell
python D:\monshin-compass\tools\smoke_api.py
```

```powershell
python D:\monshin-compass\tools\validate_symptom_cards.py --root D:\monshin-compass
```

```powershell
python D:\monshin-compass\tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures
```

Static placeholder scan:

```powershell
rg -n -e 'href="#"' -e 'javascript:void' -e 'console\.log' -e 'TODO' -e 'onclick=' web docs
```

## Browser Blocker

Browser verification blocker:

- The browser automation layer rejected navigation to `http://127.0.0.1:8765/`.
- The rejection explicitly disallowed achieving the same result through workaround, indirect execution, raw CDP, alternate browser surfaces, or policy circumvention.
- Therefore screenshot capture and runtime click proof were not completed in this pass.

## Audit Table

| UI element | Type | Visible location | Code reference | Connected handler/action | Expected behavior | Observable result | Verification method | Result | Fix needed | Manual confirmation needed |
|---|---|---|---|---|---|---|---|---|---|---|
| Back | Button | Header | `web/index.html` `#backIconButton`; `web/app.js` `goBack()` | `goBack` | Return to previous app screen or prior question state | Source maps screen-specific back behavior | Source inspection | Source pass | No | Yes |
| Menu | Button | Header | `#menuButton`; menu handlers in `web/app.js` | toggles `#menuPanel` | Open/close menu panel and expose secondary actions | Source toggles `hidden` and `aria-expanded` | Source inspection | Source pass | No | Yes |
| Menu emergency | Button | Menu | `#menuEmergencyButton` | `showEmergencyResult` | Show P0 emergency guidance with 119 priority | Source renders emergency result | Source inspection | Source pass | No | Yes |
| Menu review | Button | Menu | `#menuReviewButton` | `renderReview` | Open Review Answers screen | Source renders review rows | Source inspection | Source pass | No | Yes |
| Menu settings | Button | Menu | `#menuSettingsButton` | `showScreen("settings")` | Open Settings / Help | Source route exists | Source inspection | Source pass | No | Yes |
| Menu restart | Button | Menu | `#menuRestartButton` | `restart` | Clear answers and return to launch | Source clears selected/skipped/history/result | Source inspection | Source pass | No | Yes |
| Start | Button | Launch | `#startButton` | `goRegion` | Move from Launch to Region Confirmation | Source route exists | Source inspection | Source pass | No | Yes |
| Launch emergency | Button | Launch | `#launchEmergencyButton` | `showEmergencyResult` | Show P0 emergency guidance | Source renders 119-first route text | Source inspection | Source pass | No | Yes |
| Locale choice JP-13 | Button | Region | `[data-locale-choice="JP-13"]` | `setLocale("JP-13")` | Mark Tokyo / JP-13 selected and allow confirmed route behavior | Source sets state and `aria-pressed` | Source inspection | Source pass | No | Yes |
| Locale choice JP | Button | Region | `[data-locale-choice="JP"]` | `setLocale("JP")` | Mark unconfirmed area selected and suppress direct #7119 display | Source sets state and `aria-pressed` | Source inspection | Source pass | No | Yes |
| Confirm region | Button | Region | `#confirmRegionButton` | `startQuestions` | Start question flow | Source route exists | Source inspection | Source pass | No | Yes |
| Region emergency | Button | Region | `#regionEmergencyButton` | `showEmergencyResult` | Show P0 emergency guidance | Source route exists | Source inspection | Source pass | No | Yes |
| Dynamic answer option | Button | Question | `.answer-option[data-value]` | `chooseAnswer` | Store structured value, evaluate, continue or stop on P0/P1 | Source stores `state.selected` and calls evaluator | Source + API smoke | Source pass | No | Yes |
| Question back | Button | Question | `#questionBackButton` | `goBack` | Restore previous question and answer state | Source restores history snapshot | Source inspection | Source pass | No | Yes |
| Question emergency | Button | Question | `#questionEmergencyButton` | `showEmergencyResult` | Show emergency guidance without completing questions | Source route exists | Source inspection | Source pass | No | Yes |
| Safety answer option | Button | Safety Confirmation | dynamic `.answer-option` | safety option `apply` + `evaluateAndMaybeStop` | Resolve high-risk ambiguity or keep unknown | Source maps emergency options to deterministic values | Source inspection | Source pass | No | Yes |
| Safety back | Button | Safety Confirmation | `#safetyBackButton` | `showQuestion` | Return to triggering question | Source route exists | Source inspection | Source pass | No | Yes |
| Safety emergency | Button | Safety Confirmation | `#safetyEmergencyButton` | `showEmergencyResult` | Show P0 emergency guidance | Source route exists | Source inspection | Source pass | No | Yes |
| Result review | Button | Result | `#resultReviewButton` | `renderReview` | Open answer review | Source route exists | Source inspection | Source pass | No | Yes |
| Result evidence | Button | Result | `#resultEvidenceButton` | `showScreen("evidence")` | Open Evidence / Source screen | Source route exists | Source inspection | Source pass | No | Yes |
| Result restart | Button | Result | `#resultRestartButton` | `restart` | Clear answer state and return to launch | Source route exists | Source inspection | Source pass | No | Yes |
| Source link | Link | Evidence / Source | dynamic `sourceCard()` | external source URL | Open source in new tab when URL exists | Source creates `target="_blank"` and `rel` | Source inspection | Source pass | No | Yes |
| Evidence back | Button | Evidence / Source | `#evidenceBackButton` | `showScreen("result")` | Return to result | Source route exists | Source inspection | Source pass | No | Yes |
| Locale select | Select | Settings / Help | `#localeSelect` | `settingsApplyButton` applies value | Choose route display locale | Source stores value through `setLocale` | Source inspection | Source pass | No | Yes |
| Settings apply | Button | Settings / Help | `#settingsApplyButton` | `applySettings` | Apply locale and re-evaluate route display when needed | Source calls evaluator when result exists | Source inspection | Source pass | No | Yes |
| Settings restart | Button | Settings / Help | `#settingsRestartButton` | `restart` | Clear session and return to launch | Source route exists | Source inspection | Source pass | No | Yes |
| Settings back | Button | Settings / Help | `#settingsBackButton` | `goBack` | Return to previous app screen | Source route exists | Source inspection | Source pass | No | Yes |
| Review edit | Button | Review Answers | dynamic `.review-row button` | set question index + `showQuestion` | Return to selected question for correction | Source route exists | Source inspection | Source pass | No | Yes |
| Review result | Button | Review Answers | `#reviewResultButton` | `showScreen("result")` | Return to result | Source route exists | Source inspection | Source pass | No | Yes |
| Review restart | Button | Review Answers | `#reviewRestartButton` | `restart` | Clear session and return to launch | Source route exists | Source inspection | Source pass | No | Yes |

## Safety-Specific Findings

- P0 route copy explicitly prioritizes `119`.
- Tokyo / JP-13 route can display `#7119` only when `consultation_route.show_7119_direct` and `consultation_phone` are present.
- Japan / area unconfirmed route suppresses direct #7119 display and asks for area confirmation.
- The UI copy states that the app does not provide diagnosis or treatment.
- The settings limitation text mentions prohibited categories only as exclusions.

## Remaining Manual Confirmation Items

- Launch to Region Confirmation click path.
- Region selection and question start path.
- Each dynamic answer option state change.
- Safety Confirmation interruption after unknown safety answer.
- P0 result visual prominence and 119 priority.
- P1 Tokyo direct #7119 display.
- P1 Japan / area unconfirmed suppression of direct #7119 display.
- Evidence screen source link behavior.
- Review edit and re-evaluation path.
- 360 / 390 / 430 CSS px responsive screenshots.

## Conclusion

No placeholder-only, TODO-only, `href="#"`, `javascript:void(0)`, or `console.log`-only controls were found by source scan. Runtime interaction confirmation remains blocked by browser policy and must be completed in an allowed browser session before this UI can be called fully interaction-audited.
