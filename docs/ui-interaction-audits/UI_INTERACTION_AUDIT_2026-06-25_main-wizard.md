# UI Interaction Audit 2026-06-25: Main Wizard

Scope audited: `web/` main mobile wizard, menu controls, P1 result screen, locale routing, JSON details, source links.

Launch method: existing local server at `http://127.0.0.1:8765/`.

Viewport: Browser plugin, `390 x 844` mobile viewport. A desktop smoke screenshot was also captured at `1280 x 720`.

Commands and checks:

- `node --check web\app.js`
- `python tools\smoke_api.py`
- `python tools\validate_symptom_cards.py --root D:\monshin-compass`
- `python tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
- Browser screenshot and interaction loop through the in-app Browser.

| UI element | Type | Visible location | Code reference | Connected handler/action | Expected behavior | Observable result | Verification method | Result | Fix needed | Manual confirmation needed |
|---|---|---|---|---|---|---|---|---|---|---|
| Skip to content | Link | Top of page on focus | `web/index.html` | `href="#questionHeading"` | Move keyboard focus path toward main question | Link target resolves to local question heading anchor | DOM link audit | Pass | No | No |
| Menu | Button | Header | `web/index.html`, `web/app.js` | `menuButton` click listener | Toggle menu panel | `menuPanel.hidden` changed `true -> false -> true` | Browser click + DOM state | Pass | No | No |
| Locale select | Select | Header | `web/index.html`, `web/app.js` | `localeSelect` change listener | Re-evaluate route for selected locale | P1 result changed from Tokyo `#7119` display to area-confirmation copy for `JP` | Browser select + DOM state | Pass | No | No |
| Reset | Button | Menu panel | `web/index.html`, `web/app.js` | `resetWizard()` | Clear answers and return to first question | Heading returned to `発熱はありますか？`, result hidden, priority reset to `未判定` | Browser click + DOM state | Pass | No | No |
| Skip current question | Button | Menu panel | `web/index.html`, `web/app.js` | `skipQuestion()` | Skip optional current question and advance | Fever skipped, next heading became `咳はありますか？` | Browser click + DOM state | Pass | No | No |
| Yes | Button | Question screen | `web/index.html`, `web/app.js` | `answer("yes")` | Save affirmative answer and advance | Fever yes advanced to cough; P1 path completed after dyspnea moderate | Browser click + DOM state | Pass | No | No |
| No | Button | Question screen | `web/index.html`, `web/app.js` | `answer("no")` | Save negative answer or branch to next severity question | Severe dyspnea no advanced to moderate dyspnea confirmation | Browser click + DOM state | Pass | No | No |
| Unknown | Button | Question screen | `web/index.html`, `web/app.js` | `markUnknown()` | Save explicit unknown and advance | Fever unknown advanced to cough with no console errors | Browser click + DOM state | Pass | No | No |
| Back | Button | Question screen | `web/index.html`, `web/app.js` | `goBack()` | Restore previous question and previous selected state | Cough screen returned to fever; empty result UI reset to `未判定` | Browser click + DOM state | Pass | No | No |
| Compact compass meter | Status display | Question screen bottom | `web/index.html`, `web/app.js` | `updateMeter()` | Show provisional action direction without disease probability | Meter visible in mobile viewport; needle/status updated after answers | Browser screenshot + DOM state | Pass | No | No |
| P1 result card | Result view | P1 result screen | `web/index.html`, `web/app.js` | `renderResult()` | Show action, route, matched reason, answer memo, safety boundary | Result displayed `P1`, `早めに医療相談してください`, Tokyo `#7119`, and safety boundary | Browser P1 flow + screenshot | Pass | No | No |
| JSON output | Details disclosure | Result view | `web/index.html`, `web/app.js` | Native `<details>` | Reveal raw deterministic output only on request | `details.open` changed to `true` | Browser click + DOM state | Pass | No | No |
| Review answers | Button | Result view | `web/index.html`, `web/app.js` | review button click listener | Return to question flow for correction | Result hidden and question view returned to dyspnea review point | Browser click + DOM state | Pass | No | No |
| Start over | Button | Result view | `web/index.html`, `web/app.js` | `resetWizard()` | Clear answers and return to first question | Heading returned to fever; priority reset to `未判定` | Browser click + DOM state | Pass | No | No |
| Source links | Links | Result view source records | `web/app.js` | `sourceRow()` external anchors | Open official source records in new tab with noopener | All five result links had HTTPS URLs, `target="_blank"`, and `rel="noopener noreferrer"` | DOM link audit | Pass | No | No |

Remaining failed controls: none found.

Manual confirmation items: none required for the local UI. External source websites were not opened during the audit; the link targets and safe anchor attributes were verified by DOM inspection.

Screenshots captured:

- `outputs/runtime/asocfull-redesign-mobile-final-initial-20260625.png`
- `outputs/runtime/asocfull-redesign-mobile-final-p1-result-20260625.png`
- `outputs/runtime/asocfull-redesign-desktop-final-initial-v2-20260625.png`

Changed files covered by this audit:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `web/favicon.svg`
