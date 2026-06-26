# UI Interaction Audit 2026-06-25: Mobile Skillpass

Scope audited: `web/` mobile question flow, menu, result flow, locale routing, JSON details, source links, and responsive question viewports.

Launch method: existing local server at `http://127.0.0.1:8765/`.

Viewport coverage:

- Browser plugin DOM and console checks at `390 x 844`.
- Playwright with installed Chrome screenshots and interactions at `390 x 844`.
- Playwright responsive screenshot and fit metrics at `360 x 844`.

Screenshot evidence:

- `outputs/runtime/asocfull-mobile-skillpass-final-initial-390x844-20260625.png`
- `outputs/runtime/asocfull-mobile-skillpass-final-breathing-390x844-20260625.png`
- `outputs/runtime/asocfull-mobile-skillpass-final-breathing-360x844-20260625.png`
- `outputs/runtime/asocfull-mobile-skillpass-final-p1-result-390x844-20260625.png`

Browser note:

- In-app Browser screenshot capture timed out at `Page.captureScreenshot`.
- In-app Browser DOM snapshot and console check passed.
- Playwright was used as screenshot and interaction fallback without adding dependencies.

## Results

| UI element | Type | Visible location | Code reference | Connected handler/action | Expected behavior | Observable result | Verification method | Result | Fix needed | Manual confirmation needed |
|---|---|---|---|---|---|---|---|---|---|---|
| Page load | App surface | First screen | `web/index.html`, `web/app.js` | `loadCards()` | Render first fever card | Title `Monshin Compass`, heading `発熱はありますか？`, step `1/7` | Playwright DOM state | Pass | No | No |
| Question viewport fit | Layout | Question screen | `web/styles.css` | CSS mobile rules | Fit without horizontal or vertical question-screen overflow | `390 x 844`: scroll `390 x 844`; `360 x 844`: scroll `360 x 844`; clipped controls `0` | Playwright viewport metrics | Pass | No | No |
| Menu | Button | Header | `web/index.html`, `web/app.js` | `menuButton` click listener | Toggle menu panel | `menuPanel.hidden` changed to `false`; `aria-expanded=true` | Playwright click + DOM state | Pass | No | No |
| Skip current question | Button | Menu panel | `web/index.html`, `web/app.js` | `skipQuestion()` | Skip optional current card, advance, and return focus to main flow | Fever skipped, heading became `咳はありますか？`, step `2/7`, menu closed | Playwright click + DOM state | Pass | No | No |
| Menu reset | Button | Menu panel | `web/index.html`, `web/app.js` | `resetWizard()` | Clear state, return to first card, close menu | Heading returned to `発熱はありますか？`, step `1/7`, menu closed | Playwright click + DOM state | Pass | No | No |
| Yes | Button | Question screen | `web/index.html`, `web/app.js` | `answer("yes")` | Save affirmative answer and advance | Fever yes advanced to cough, step `2/7` | Playwright click + DOM state | Pass | No | No |
| No | Button | Question screen | `web/index.html`, `web/app.js` | `answer("no")` | Save negative answer or branch to next severity question | Severe dyspnea no advanced into moderate dyspnea confirmation during P1 path | Playwright click + DOM state | Pass | No | No |
| Unknown | Button | Question screen | `web/index.html`, `web/app.js` | `markUnknown()` | Save explicit unknown and advance | Fever unknown advanced to cough, step `2/7` | Playwright click + DOM state | Pass | No | No |
| Back | Button | Question screen | `web/index.html`, `web/app.js` | `goBack()` | Restore previous question and previous selected state | Cough returned to fever; back disabled at first card | Playwright click + DOM state | Pass | No | No |
| Compact compass meter | Status display | Question screen bottom | `web/index.html`, `web/app.js`, `web/styles.css` | `updateMeter()` | Show provisional action direction without disease probability | Meter visible in first viewport; no clipped question controls | Playwright screenshot + metrics | Pass | No | No |
| Locale select | Select | Header | `web/index.html`, `web/app.js` | `localeSelect` change listener | Reevaluate route for selected locale | P1 Tokyo `#7119` route changed to area-confirmation copy for `JP` | Playwright select + DOM state | Pass | No | No |
| P1 result card | Result view | Result screen | `web/index.html`, `web/app.js` | `renderResult()` | Show priority, route, matched reason, answer memo, safety boundary | Result showed `P1`, Tokyo `#7119`, and safety boundary | Playwright P1 path + screenshot | Pass | No | No |
| Safety boundary | Result block | Result screen near action | `web/index.html` | Static result view block | Prominently state not diagnosis/treatment and 119 priority | Boundary visible in first result viewport | Playwright DOM state + screenshot | Pass | No | No |
| JSON output | Details disclosure | Result view | `web/index.html`, `web/app.js` | Native `<details>` | Reveal deterministic JSON only on request | `details.open=true`, JSON length `6622` | Playwright click + DOM state | Pass | No | No |
| Source links | Links | Result source list | `web/app.js` | `sourceRow()` external anchors | Expose HTTPS source records safely | 6 HTTPS links, all `target="_blank"` and `rel="noopener noreferrer"` | Playwright DOM link audit | Pass | No | No |
| Review answers | Button | Result view | `web/index.html`, `web/app.js` | `reviewButton` click listener | Return from result to previous question context | Result hidden; question view returned to `動くと息切れしますか？` | Playwright click + DOM state | Pass | No | No |
| Start over | Button | Result view | `web/index.html`, `web/app.js` | `resultResetButton` -> `resetWizard()` | Clear result and return to first card | Result hidden; heading `発熱はありますか？`, step `1/7` | Playwright click + DOM state | Pass | No | No |
| Console health | Runtime | Browser/app | Browser dev logs and Playwright page events | No app errors or warnings | No console warnings, console errors, or page errors observed | Browser log check + Playwright listeners | Pass | No | No |

Remaining failed controls: none found.

Manual confirmation items: none required for the local UI. External source sites were not opened; link targets and safe anchor attributes were verified by DOM inspection.

Changed files covered by this audit:

- `web/styles.css`
- `web/app.js`

Verification commands:

- `node --check web\app.js`
- `python tools\smoke_api.py`
- `python tools\validate_symptom_cards.py --root D:\monshin-compass`
- `python tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`

## Experience Extracted

- Treat screenshot tooling as part of the test target: if a screenshot path crops at small widths, verify against DOM metrics before trusting the image.
- Menu-revealed controls need state-cleanup checks, not just "does the handler run" checks.
- For a medical action compass, mobile premium polish is best measured by clarity, stable fit, thumb-safe controls, and zero false certainty, not by decorative motion or landing-page structure.
