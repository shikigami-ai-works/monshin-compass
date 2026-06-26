# Mobile Card Compass UI Spec

> Current status: prototype-era Web UI reference.
>
> The screen-design source of truth has moved to
> `docs/smartphone-app-screen-spec.md`.
>
> Keep this file as implementation evidence for the verified Web prototype and
> the large-card visual experiment. Do not treat it as the next product screen
> architecture unless Shiki explicitly restores it.

Created: 2026-06-25
Status: superseded for future UI direction; retained as prototype reference
Scope: `web/` mobile-first vertical-slice UI for fever, cough, and dyspnea triage
Reference image: `outputs/design/monshin-compass-mobile-card-compass-large-card-20260625.png`

## ASOCFULL Alignment Snapshot

- Target: lock the mobile question UI to the latest large-card mockup.
- Latest user scope: use the A+C hybrid concept. A = illustrated two-choice card deck. C = compact compass/action meter.
- Hard fence: do not design a disease identification UI. This product guides next action and triage priority only.
- Previous loop result: the bottom safety strip consumed too much space during questions.
- Spec decision: remove the persistent question-screen safety strip, enlarge the illustration card, and show the safety boundary prominently on the final result screen.
- Verified: reference image exists in `outputs/design/`.
- Not verified: no implementation or browser audit has been run for this locked design yet.
- Decision: rewrite this spec as the implementation source of truth for the next UI pass.

## Product Position

Monshin Compass is a symptom action compass. It does not identify a disease.

The mobile UI must help the user answer one body-part or situation card at a time, then guide them toward the next action:

- `観察`
- `相談`
- `救急`

The UI may visually feel like a diagnostic flow, but the text and result model must stay action-oriented. It must not show disease names, diagnosis candidates, treatment advice, medication names, dosage, or reassurance that care is unnecessary.

## Fixed Design Direction

Use the A+C hybrid:

- A: illustrated card deck for body parts and situations.
- C: compact compass/action meter that shows provisional action direction.

The current question screen is not a form and not a dashboard. It is a large tactile card interaction.

### Required Visual Hierarchy

1. Compact app header.
2. Progress and card markers.
3. Very large illustrated card deck.
4. Two primary choices.
5. Secondary controls.
6. Compact compass/action meter.

No persistent bottom safety disclaimer appears during question screens. The freed space belongs to the illustrated card.

## Question Screen Layout

Target viewport is a portrait smartphone around 390 x 844 CSS pixels. The layout must remain usable down to 360 px width.

### Header

Required elements:

- menu icon
- compass mark
- `Monshin Compass`
- locale chip: `Tokyo / JP-13`

The header must be compact. It must not compete with the card.

### Progress Row

Required elements:

- large current step text, for example `3 / 7`
- seven small card markers
- completed markers use check marks
- active marker is highlighted
- future markers are muted

The progress row communicates deck progress, not clinical certainty.

### Card Deck

The active card is the main visual object on the screen.

Required card behavior:

- one active front card
- visible stacked-card shadow or offset layers behind it
- 8 px radius or close to the project radius language
- large body-part or situation illustration
- category label
- card title
- direct question
- short support copy

For the breathing card shown in the reference image:

- category label: `呼吸`
- card title: `息がしづらい`
- question: `息がしづらいですか？`
- support copy: `少しでも息苦しい場合は「はい」を選びます。`
- illustration: lungs and breath marks, large enough to dominate the card

The illustration must be larger than in the previous footer version. The card is the primary screen content.

### Primary Answers

Required controls:

- `はい`
- `いいえ`

Rules:

- `はい` is the primary cobalt button.
- `いいえ` is neutral, white or very light surface with border.
- Do not make `いいえ` red.
- Buttons must be large enough for thumb use.
- Controls must have real state transitions. No placeholder actions.

### Secondary Controls

Required controls:

- `わからない`
- `戻る`

Optional only if space allows:

- `リセット`

Rules:

- secondary controls are visually quieter than `はい` and `いいえ`
- `わからない` maps to an explicit internal value, not silent omission
- `戻る` restores the previous question and previous selected state

### Compact Compass Meter

The compass/action meter stays visible on question screens, but it is secondary to the card.

Required labels:

- `観察`
- `相談`
- `救急`

Required status copy:

- `判定中: 次の行動を確認`

Rules:

- the meter is compact and anchored below the answer controls
- the needle may move provisionally as answers accumulate
- the meter must not show disease probability
- the meter must not imply final safety until the result screen
- red appears only in the `救急` zone or final P0/P1 warnings, not on ordinary negative answers

## Result Screen Layout

The result screen is where the safety boundary appears strongly.

When the question flow reaches a final or high-priority result, the UI must replace the question card with a result view.

### Result Summary

Required elements:

- priority badge: `P0`, `P1`, `P2`, or `P3`
- action direction: one of `救急`, `相談`, or `観察`
- short action headline
- locale-aware route block
- matched reason summary
- selected answer summary

### Safety Boundary Block

The removed bottom disclaimer must appear here as a prominent block.

Required copy:

`診断・治療ではありません。強い症状は119を優先。`

Rules:

- show the block near the result action, not as tiny footer copy
- for P0, the 119 instruction is the dominant result
- for P1/P2/P3, the safety boundary remains visible but does not overpower the main action
- do not state that care is unnecessary

### Locale And Emergency Routing

For `Tokyo / JP-13`, confirmed local `#7119` may be shown for consultation routes when resolver output allows it.

Rules:

- never display `#7119` as nationwide
- for P0, `119` takes priority over `#7119`
- if locale is unconfirmed, route the user to area confirmation instead of displaying `#7119` as a direct number

## Internal Answer Model

The visible UI is mostly two-choice. The internal model is not simple boolean.

Required values:

- `fever`: `yes | no | unknown`
- `cough`: `yes | no | unknown`
- `dyspnea`: `none | mild | moderate | severe | unknown`
- optional context cards may use their schema-defined values

Rules:

- skipped optional questions are not confirmed safe
- required safety questions prefer `unknown` over silent omission
- dyspnea must use follow-up cards to distinguish `mild`, `moderate`, and `severe`
- deterministic rules decide `P0/P1/P2/P3`; LLM or RAG must not decide priority

## Initial Card Order

The MVP card order is:

1. 発熱: `熱っぽさはありますか？`
2. 咳: `咳はありますか？`
3. 呼吸: `息がしづらいですか？`
4. 呼吸 / 強さ: if breathing difficulty exists, ask severe confirmation
5. 呼吸 / 動作時: if not severe, ask moderate confirmation
6. 期間: `発熱や咳は4日以上続いていますか？`
7. 変化: `時間とともに悪化していますか？`

Each card must use a body-part or situation illustration. The card is not a plain input row.

## Visual System

Use a calm but memorable healthcare product style.

Required style:

- warm off-white background
- white card surfaces
- graphite text
- cobalt primary action
- amber consultation accent
- green observation accent
- red emergency accent used sparingly
- clean medical line illustrations
- tactile card deck shadows
- compact compass gauge

Avoid:

- purple AI gradients
- doctor stock photos
- chatbot framing
- dense dashboard cards on mobile
- over-rounded pill-only UI
- red `いいえ`
- disease probability charts
- fake medical certainty

## Accessibility And Mobile Ergonomics

Requirements:

- primary answer controls must be thumb-friendly
- text must fit within 360 px width without overlap
- small labels may be compact, but question and answers must remain readable
- color cannot be the only signal for priority or progress
- active, completed, and disabled states must be visually distinct
- back navigation must be possible without losing prior answers

## Forbidden Drift

- Do not restore the mobile multi-card checklist as the primary input.
- Do not place a persistent safety disclaimer footer on question screens.
- Do not shrink the card to make room for secondary legal or metadata content.
- Do not present disease names, likely diseases, diagnosis rankings, treatment, medication, dosage, or reassurance that care is unnecessary.
- Do not allow LLM/RAG output to choose the triage priority.
- Do not display `#7119` without locale confirmation.
- Do not treat skipped or unknown safety answers as safe.

## Acceptance Criteria

The next implementation pass is acceptable when:

- the first mobile viewport visually matches the large-card reference direction
- the active card takes the majority of the question-screen vertical attention
- the bottom safety disclaimer is absent during question screens
- the final result screen contains the prominent safety boundary block
- `はい`, `いいえ`, `わからない`, and `戻る` all perform user-observable actions
- `いいえ` is neutral, not red
- the compact compass shows `観察 / 相談 / 救急`
- the UI never shows disease identification or treatment advice
- `P0/P1/P2/P3` still comes from deterministic local evaluation
- Tokyo-specific `#7119` behavior remains locale-gated

## Verification Plan

After implementation:

1. Run the existing symptom card validator.
2. Run JP emergency route fixtures.
3. Run evaluator fixtures for at least one P0 and one P1 path.
4. Capture mobile screenshot around 390 x 844.
5. Run a UI interaction audit covering every visible control.
6. Confirm the question screen has no persistent safety footer.
7. Confirm the result screen shows the safety boundary prominently.
