# Monshin Compass Layered Smartphone App Specification

Created: 2026-06-25  
Rewritten: 2026-06-25  
Status: source of truth for the next UI design and implementation pass  
Scope: smartphone-first app specification for Monshin Compass  
Supersedes for UI direction: `docs/mobile-question-wizard-spec.md`  
Does not supersede: triage rules, symptom card schema, emergency routing, evidence contracts, validators, evaluator tools, or data files

This document is a layered specification. Safety requirements, product requirements, state/flow, screen design, and Web implementation planning are intentionally separated so later UI work does not weaken the deterministic safety core.

## Ticket 0: ASOCFULL Alignment And Source Inventory

### Alignment Snapshot

- Target: rewrite the smartphone app specification in responsibility layers before the next Web UI implementation pass.
- Latest scope: docs-only specification work. Do not change runtime files, data files, evaluator tools, or deterministic triage logic.
- Hard fences: do not reimplement P0/P1/P2/P3 in UI; do not use LLM/RAG to decide red flags; do not show diagnosis, disease ranking, treatment, medication, dosage, or reassurance that care is unnecessary.
- Current source of truth: this file, after this rewrite.
- Prototype references: `docs/mobile-question-wizard-spec.md`, current `web/`, current screenshots, and UI audit files.
- Previous loop result: the Web prototype was repaired and verified as a mobile card UI, but it is not final product architecture.
- Git state at rewrite time: `D:\monshin-compass` is not a Git repository.
- Verified in this docs pass: source documents were read and authority layers were separated.
- Not verified in this docs pass: runtime behavior, screenshots, real-device behavior, medical professional review, and rights/legal review.
- Go condition for implementation: this layered spec is accepted as the UI authority and implementation work is explicitly opened.
- Stop condition: any proposed change that alters safety rules, data contracts, external ingestion rights, publication, Git setup, install behavior, or external writes.

### Source Inventory

| Layer | Source | Status | Use |
|---|---|---|---|
| Safety/core | `docs/triage-output-contract.md` | authoritative | Defines evaluator inputs, outputs, forbidden output categories, source records, and route output shape. |
| Safety/core | `docs/symptom-card-schema.md` | authoritative | Defines card IDs, values, unknown handling, safety-card meaning, fixtures, and schema drift limits. |
| Safety/core | `docs/red-flag-rules.md` | authoritative | Defines P0/P1/P2/P3 priority meaning, rule IDs, stop conditions, and forbidden safety drift. |
| Safety/core | `docs/jp-emergency-routing-resolver.md` | authoritative | Defines 119 priority, #7119 locale gating, and deployment-locale route behavior. |
| Safety/core | `docs/evidence-retrieval-contract.md` | authoritative | Defines source/RAG boundaries, allowed use, forbidden use, and retrieval record policy. |
| Safety/core | `data/` | authoritative data | Provides rule, card, source, and routing records used by validators and evaluator tools. |
| Safety/core | `tools/` | authoritative local checks | Provides validators, route fixtures, smoke checks, and evaluator fixtures. |
| Current spec | `docs/smartphone-app-screen-spec.md` | rewritten authority | Owns product, state, screen, Web conversion, and acceptance rules for the next UI pass. |
| Prototype reference | `docs/mobile-question-wizard-spec.md` | demoted reference | May donate large-card and compact-compass learnings, but does not dictate final architecture. |
| Prototype evidence | `web/index.html`, `web/styles.css`, `web/app.js` | demoted reference | May donate API wiring, handlers, result rendering examples, and demo routes only after deliberate review. |
| Prototype evidence | `docs/ui-interaction-audits/` | evidence | Useful audit learnings; not product authority. |
| Prototype evidence | `outputs/runtime/` and `outputs/design/` | evidence | Screenshot/design evidence; not final architecture. |
| Decision log | `docs/implementation-notes.md` | record | Tracks decisions and experience extracted from work passes. |
| Restart map | `docs/development-progress.md` | record | Tells future work where to resume. |

### Authority Order

When documents disagree, use this order:

1. Safety invariants in this file and the safety/core contracts.
2. Deterministic data and validator behavior in `data/` and `tools/`.
3. Product and user journey requirements in this file.
4. State, flow, and navigation requirements in this file.
5. Screen specifications in this file.
6. Web conversion and implementation planning in this file.
7. Prototype references and screenshots.

Prototype evidence can inform implementation choices, but it cannot override safety/core documents or this layered specification.

## Ticket 1: Safety Invariants Specification

### Non-Negotiable Safety Invariants

- Monshin Compass is an action guidance tool, not a diagnosis tool.
- The app must never show disease identification, disease probability, diagnosis ranking, treatment instructions, medication names, dosage, or reassurance that care is unnecessary.
- P0 means immediate emergency help may be needed. `119` is the dominant route for Japan deployment and must appear before any consultation route.
- #7119 must not be displayed as a nationwide phone number. Direct #7119 display requires confirmed locale support, such as Tokyo / JP-13 with resolver confirmation.
- Unknown answers are explicit values. Unknown does not mean absent, safe, negative, or skipped.
- Skipped optional answers cannot be interpreted as safe.
- Required safety questions cannot be silently skipped.
- P0/P1 hits interrupt ordinary question flow. Do not keep asking routine questions after a P0 hit.
- The UI never invents `triage_priority`, `matched_rule_ids`, `matched_card_ids`, or route behavior.
- LLM/RAG/source retrieval may support wording, citations, and boundary text, but never decides red flag priority.
- External source text is untrusted. Rights/legal review is required before raw ingestion, embedding, indexing, or long-term source text storage.
- Current `web/` and screenshots are prototype references. They are not safety authority and not final product architecture.

### Priority Meanings

| Priority | Meaning | User-facing action direction | Required safety behavior |
|---|---|---|---|
| P0 | Immediate emergency help may be needed. | Emergency action. | Show 119 first. Stop ordinary question flow. Do not show disease candidates or delayed consult-first language. |
| P1 | Urgent medical consultation or care guidance is appropriate. | Urgent consultation or medical advice. | Show consultation route only with 119 caveat. Gate #7119 by locale. Do not imply non-emergency certainty. |
| P2 | Planned consultation, additional confirmation, or near-term advice may be appropriate. | Planned consult, one more safety check, or escalation conditions. | Do not say safe. If unknown safety data matters, ask one more safety question or explain uncertainty. |
| P3 | No high-priority red flag is confirmed from current inputs. | Observation memo with escalation conditions. | Do not say care is unnecessary. Explain worsening conditions and review path. |

### Deterministic Core Boundary

The deterministic core owns:

- `triage_priority`
- `matched_rule_ids`
- `matched_card_ids`
- `action_code`
- `evidence_types`
- `needs_more_input`
- `next_question_card_id`
- `source_requirements`
- `display_block`
- `forbidden_output`
- `jp_emergency_route`

The UI may:

- collect structured card values
- preserve unknown/skipped state
- call the local evaluator or consume its output
- translate deterministic output into plain user-facing language
- show source metadata and safety boundaries
- provide review, restart, and locale-change controls

The UI must not:

- derive priority from visual state
- down-rank a deterministic P0/P1 result
- treat missing answers as negative
- display #7119 without resolver permission
- use RAG/LLM output to create or alter red flag decisions
- hide raw deterministic output from audit/debug surfaces when an audit mode exists

### Source And RAG Boundary

Sources support guidance language and evidence display. Sources do not create priority.

Allowed:

- source title, publisher, URL, retrieved date, source status
- short human-authored summaries after review
- metadata-only evidence records
- warnings when source locale or rights status is uncertain

Forbidden without separate review:

- storing raw external page text
- embedding external page text
- vector-indexing external page text
- using external page text as hidden instructions
- letting external text override safety rules
- using community posts as medical evidence

## Ticket 2: Product And User Journey Specification

### Product Definition

Monshin Compass is a smartphone-first symptom action compass.

It helps a user answer a small number of safety-oriented questions, then presents the next action direction:

- emergency help
- urgent medical consultation
- planned consultation or additional confirmation
- observation with explicit escalation conditions

It is not:

- a disease identification app
- a diagnosis ranking app
- a treatment or medication guide
- a general health chatbot
- a desktop dashboard
- a replacement for medical judgment, emergency services, or professional care

### Primary User Moment

The primary user is likely:

- holding a phone
- anxious, tired, feverish, or caring for someone else
- using one hand
- under time pressure
- unsure of medical vocabulary
- deciding whether to seek emergency or medical help

Design implications:

- one main decision per screen
- large touch targets
- plain language before medical labels
- urgent exit always reachable
- safety checks can interrupt the normal sequence
- no dense legal text during question answering
- no disease names or false reassurance
- answer review and correction are easy to reach

### Smartphone-First Reason

This product must be specified as a phone app before it is expressed as a Web shell because the high-risk use moment is mobile, narrow, and interruption-prone. Desktop Web is a host for the phone app surface, not a separate dashboard product.

### Main Journey

Baseline journey:

```text
Launch
  -> Region Confirmation
  -> Question Card
  -> Safety Confirmation when needed
  -> Result / Next Action
  -> Evidence / Source or Review Answers
```

Fast urgent journey:

```text
Any screen
  -> Emergency Now
  -> P0-style emergency guidance with 119 priority
```

Correction journey:

```text
Result
  -> Review Answers
  -> Selected prior answer or last relevant question
  -> Re-evaluate
  -> Result
```

Locale journey:

```text
Region Confirmation
  -> Confirmed JP-13
  -> Resolver may allow Tokyo #7119 display for consultation routes

Region Confirmation
  -> Japan / area unconfirmed
  -> Result routes to area confirmation instead of direct #7119 display
```

## Ticket 3: State, Flow, And Navigation Specification

### App State Model

Minimum state:

- `locale_state`
  - `requested_locale`
  - `confirmed_locale`
  - `locale_confidence`
  - `route_display_permission`
- `answer_state`
  - `card_id`
  - `value`
  - `source`: `user_selected | default_unknown | skipped_optional | restored_from_review`
  - `asked_at_step`
  - `is_required_safety_answer`
- `flow_state`
  - `current_screen`
  - `current_card_id`
  - `step_index`
  - `safety_interruption_reason`
  - `can_go_back`
  - `can_restart`
- `result_state`
  - deterministic evaluator output
  - route resolver output
  - source metadata status
  - answer memo
- `audit_state`
  - raw deterministic output when debug/audit mode exists
  - verification-only demo state, never as ordinary user controls

### State Invariants

- Every required safety card is either answered or explicitly unknown.
- Unknown remains visible in review and result summaries when it affects safety.
- Optional skip is stored as skipped, not negative.
- Locale changes invalidate only route display, not the symptom answer history.
- Any result after a locale change must re-resolve emergency/consultation route display.
- P0 result locks ordinary question progression until the user restarts or reviews answers.
- Restart clears selected answers, skipped optional state, result state, and safety interruption state.
- Restart keeps confirmed locale unless the user explicitly changes it.

### Flow Rules

Baseline flow:

1. Launch introduces the product boundary.
2. Region confirmation establishes whether local route numbers may be shown.
3. Question card asks one structured question at a time.
4. Safety confirmation interrupts when high-risk ambiguity exists.
5. Deterministic evaluator returns next question or result.
6. Result screen displays action direction, reasons, route block, boundary, and review paths.
7. Evidence/source screen shows metadata, not long external text.

Safety interruption:

- Triggered by dyspnea uncertainty, chest pain, confusion, blood, cyanosis, fainting, seizure, self-harm, severe pain, or repeated unknown safety answers.
- May interrupt normal card order.
- Must ask the smallest useful safety question.
- If P0 is selected, stop ordinary questions and show emergency result.

Unknown-heavy flow:

```text
Question Card
  -> Unknown
  -> If unknown affects P0/P1/P2, ask one safety confirmation
  -> If still unresolved, show uncertainty-aware result or response-unavailable block
```

Back behavior:

- From question: return to previous question and restore previous answer state.
- From safety confirmation: return to the triggering question.
- From result: go to review answers, not browser-style state loss.
- From evidence/source: return to result.
- From settings/help: return to previous app screen.

Review behavior:

- Review shows every answered, unknown, and skipped relevant value.
- Selecting an answer returns to that card or the nearest safe correction point.
- After correction, deterministic evaluator and route resolver must run again.

Emergency escape:

- Available from every screen.
- Does not require completing the questionnaire.
- Shows emergency guidance and 119 priority.
- Does not erase answers unless the user restarts.

## Ticket 4: Screen Specification

Each screen must preserve the Safety Invariants section. No screen may introduce diagnosis, treatment, medication, dosage, or reassurance that care is unnecessary.

### 1. Launch

Purpose:

- establish product identity
- frame the app as next-action guidance, not diagnosis
- move quickly into locale confirmation or urgent escape

Required content:

- `Monshin Compass`
- short phrase: symptom action compass / next action guide
- compact not-diagnosis boundary
- primary start action
- emergency-now action

Required actions:

- start
- emergency now
- open limitations/help when space allows

Forbidden drift:

- no marketing hero
- no feature list as the main content
- no disease examples
- no chatbot prompt
- no desktop landing-page behavior

Safety notes:

- Returning sessions may skip launch only when locale state is already confirmed.

Accessibility notes:

- Start and emergency actions must be reachable without hidden menus.

### 2. Region Confirmation

Purpose:

- prevent unsafe display of local consultation numbers
- confirm deployment area before direct #7119 display

Required content:

- current area selection
- confirmation prompt
- Tokyo / JP-13 confirmed option
- Japan / area unconfirmed fallback
- explanation that #7119 availability depends on area

Required actions:

- confirm current area
- change area
- continue without direct local number
- emergency now

Forbidden drift:

- do not show #7119 as nationwide
- do not treat browser locale or IP-derived hints as confirmed medical route permission

Safety notes:

- 119 remains the P0 priority regardless of locale.
- Area uncertainty routes to area confirmation, not direct #7119 display.

Accessibility notes:

- Area choices need readable labels and selected state not conveyed by color alone.

### 3. Question Card

Purpose:

- ask one clear safety or symptom question at a time
- record a structured value
- move toward the next safest action

Required content:

- compact app header
- progress indicator
- card category
- plain-language question
- optional short helper copy
- illustration or icon that supports but does not carry the only meaning
- visible current answer state when returning/backtracking
- bottom answer/action area

Required actions:

- affirmative/present/severity answer
- negative/none answer
- unknown answer
- back when possible
- emergency now

Forbidden drift:

- no enabled placeholder buttons
- no answer button without visible state change or navigation
- no persistent dense safety footer during normal questions
- no disease probability, diagnosis card, or treatment suggestion
- no icon-only meaning without text or accessible name

Safety notes:

- Unknown is a real value.
- Required safety questions cannot be silently skipped.
- Optional skip is allowed only when the evaluator can still produce a safe next step.

Accessibility notes:

- Primary touch targets should be at least 48 CSS px high.
- Secondary touch targets should be at least 40 CSS px high.
- Focus order follows visible flow.

### 4. Safety Confirmation

Purpose:

- resolve high-risk ambiguity before showing a lower-priority result
- separate ordinary symptom questions from urgent safety checks

Used when:

- dyspnea is present but severity is unclear
- chest pain, confusion, blood, cyanosis, fainting, seizure, self-harm, severe pain, or similar safety cards are triggered
- repeated unknown answers prevent safe classification

Required content:

- direct safety question
- why it matters in one short sentence
- answer options mapped to structured values
- emergency now action

Required actions:

- answer safety question
- mark unknown
- back to triggering question
- emergency now

Forbidden drift:

- do not bury P0/P1 checks behind progress completion
- do not soften the wording so much that the safety distinction disappears
- do not continue ordinary questions after a P0 condition is selected

Safety notes:

- This screen may interrupt normal order.
- A P0 selection stops ordinary flow and shows emergency result.

Accessibility notes:

- The urgent nature must be readable without color alone.

### 5. Result / Next Action

Purpose:

- tell the user the next action direction
- summarize why
- preserve medical safety boundary
- provide locale-aware route information

Required content:

- priority badge: P0, P1, P2, or P3
- action direction label
- direct action headline
- route block
- matched reason summary
- answer memo
- visible safety boundary
- evidence/source entry
- review answers
- start over

Required actions:

- follow route guidance where appropriate
- review answers
- view evidence/source
- change locale when route display depends on locale
- start over
- emergency now where not already dominant

Forbidden drift:

- no disease candidates
- no treatment instructions
- no medication or dosage
- no "no care needed" or equivalent reassurance
- no #7119 direct display without resolver confirmation

Safety notes:

- P0: emergency action dominates; 119 appears before consultation routes.
- P1: urgent consultation dominates; 119 caveat remains visible.
- P2: planned consult/additional confirmation; never imply safety.
- P3: observation and escalation conditions; never close the loop as safe.

Accessibility notes:

- Result heading, route block, and safety boundary must be screen-reader sensible.

### 6. Evidence / Source

Purpose:

- show what kind of source supports the guidance language
- keep raw source ingestion boundaries clear
- increase trust without overwhelming the action screen

Required content:

- source title
- publisher
- URL
- retrieved date
- source status
- source updated date when known
- raw RAG/embedding permission status when relevant

Required actions:

- open source URL when allowed
- return to result
- view limitations/source policy

Forbidden drift:

- do not dump long external page text into the flow
- do not imply external sources made the priority decision
- do not store or index rights-restricted page text by default

Safety notes:

- Deterministic rules produce priority. Sources support explanation and boundary wording.

Accessibility notes:

- Links identify publisher and destination.

### 7. Settings / Help

Purpose:

- let the user change locale, restart, read limitations, and access help

Required content:

- locale setting
- restart current session
- emergency guidance explanation
- privacy/data handling summary
- source policy summary
- app limitations

Required actions:

- change locale
- restart
- return to previous screen
- emergency now

Forbidden drift:

- do not hide urgent action only inside settings
- do not add non-functional toggles
- do not present legal text as a substitute for clear safety guidance

Safety notes:

- Changing locale after answers must re-run route display resolution.

Accessibility notes:

- Menu controls require accessible names and visible outcomes.

### 8. Review Answers

Purpose:

- let the user inspect and correct structured answer state before or after result

Required content:

- answered values
- unknown values
- skipped optional values
- safety-card indicators
- current deterministic result summary when available

Required actions:

- edit answer
- return to result
- restart
- emergency now

Forbidden drift:

- do not hide unknown values that affect safety
- do not rewrite skipped optional values as negative
- do not allow correction without re-evaluation

Safety notes:

- Editing a safety-relevant answer invalidates the current result until re-evaluation completes.

Accessibility notes:

- Each editable row must expose its label, current value, and edit action.

## Ticket 5: Web Conversion And Implementation Planning

This section is a plan for later implementation. It is not permission to edit runtime files during docs-only work.

### Phone Viewport Behavior

- The app fills the viewport.
- The smartphone app model is the product surface.
- No marketing layout, desktop dashboard, or split result side panel during questions.
- The first usable screen should be an app screen, not a landing page.
- All visible controls must have user-observable outcomes.

### Desktop Host Behavior

- Desktop Web centers or hosts the smartphone app surface.
- Desktop does not introduce a different product model.
- Extra controls outside the phone surface are allowed only for explicit dev/test mode.
- Quiet background is acceptable; a dashboard shell is not.

### Current `web/` May Donate

- deterministic API wiring
- answer handlers
- result rendering examples
- route display examples
- SVG illustration experiments
- verification-only demo URL patterns
- UI interaction audit learnings

### Current `web/` Must Not Dictate

- final screen list
- final app navigation model
- final information architecture
- final desktop behavior
- final typography/spacing
- persistent question safety footer
- dashboard-like result side panels
- mojibake user-facing copy
- enabled placeholder or console-only actions

### Future Target Files

Later implementation may touch:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- optional new docs under `docs/ui-interaction-audits/`
- optional screenshot evidence under `outputs/runtime/`

Later implementation must not touch without separate approval:

- deterministic rule data
- validators/evaluator tools
- external ingestion policy
- Git setup
- publish/release surfaces

### Future Verification Commands

Use the project Python runtime when available:

```powershell
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\smoke_api.py'
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\validate_symptom_cards.py' --root 'D:\monshin-compass'
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\resolve_jp_emergency_route.py' --root 'D:\monshin-compass' --run-fixtures
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\evaluate_symptom_case.py' --root 'D:\monshin-compass' --locale JP-13 --fixture SCHEMA-TC-001
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\evaluate_symptom_case.py' --root 'D:\monshin-compass' --locale JP-13 --fixture SCHEMA-TC-002
```

Also run:

```powershell
node --check 'D:\monshin-compass\web\app.js'
```

### Screenshot Requirements

Capture and inspect at minimum:

- 360 CSS px wide phone viewport
- 390 CSS px wide phone viewport
- 430 CSS px wide phone viewport
- one P0 result path
- one P1 result path
- one P2/P3 non-urgent path when implemented
- desktop host view

Screenshots must prove:

- no overlapping controls
- no clipped primary actions
- result safety boundary is visible
- #7119 is gated by locale
- P0 prioritizes 119

### UI Interaction Audit Requirements

Audit all visible and menu-revealed controls:

- control label/accessibility name
- expected visible outcome
- verification method
- pass/fail
- safety notes

No enabled control may be placeholder-only, `href="#"`, `javascript:void(0)`, TODO-only, or console.log-only.

## Ticket 6: Integrated Spec Assembly And Consistency Review

### Consistency Review

Pass:

- Safety invariants are separated from screen design.
- Product definition stays action-oriented, not diagnostic.
- State/flow treats unknown and skipped as explicit states.
- Screen specs include purpose, content, actions, forbidden drift, safety notes, and accessibility notes.
- Web conversion is separate from product and safety requirements.
- Current `web/` is fixed as prototype reference, not final architecture.
- P0 prioritizes 119.
- #7119 remains locale-gated.
- Deterministic core remains authoritative.
- RAG/source retrieval does not decide priority.

Strongest risk found:

- Existing docs and data include mojibake-style user-facing labels. If implementation copies those strings directly, the app can become unreadable and unsafe even when logic is correct. Treat all current user-facing Japanese copy as needing a separate copy/encoding pass before production UI adoption.

Unresolved risks:

- No medical professional review has been completed.
- No rights/legal review has cleared raw external source ingestion or embedding.
- No real-device mobile/accessibility test has been run for the rebuilt app architecture.
- The project is not a Git repository, so rollback, branch history, and publication flow are absent.
- The Web UI has not yet been rebuilt from this layered spec.

### Acceptance Criteria

Docs-level acceptance:

- This file is treated as the UI specification authority.
- Safety invariants are readable without screen-design context.
- Product requirements are readable without implementation details.
- State and navigation rules are defined before screen drawing.
- Screen specs do not depend on current Web prototype structure.
- Web conversion is marked as implementation planning, not product authority.
- Current `web/` and screenshots are prototype references only.

Future implementation acceptance:

- Smartphone screen model is implemented before desktop embellishment.
- Deterministic evaluator fixtures still pass.
- JP emergency route fixtures still pass.
- P0 result prominently prioritizes 119.
- #7119 direct display appears only with confirmed locale resolver permission.
- No screen shows diagnosis, disease ranking, treatment, medication, dosage, or reassurance that care is unnecessary.
- Unknown/skipped values remain visible in review and safety logic.
- Visible controls pass UI interaction audit.
- Screenshots at 360, 390, and 430 CSS px widths show no broken layout.
- Result screen prominently shows the safety boundary.

### Experience Extracted

- A polished Web prototype can become an architectural anchor too early. Keep prototype evidence useful, but demote it before product architecture is rewritten.
- Safety requirements must be a separate layer. If they live only inside screen copy, later visual work can accidentally weaken them.
- Unknown and skipped are not UI conveniences; they are safety states.
- Locale routing is not copywriting. It is safety-critical route resolution and must remain gated by deterministic resolver output.
- Evidence retrieval supports user-facing explanation, not priority decisions.
- Mojibake is not cosmetic in a medical-adjacent UI. User-facing copy requires a dedicated encoding and language QA pass before implementation is treated as safe.

### Next Executable Ticket

Ticket: Implement smartphone app shell from layered spec

Objective:

- Rebuild the Web UI as a smartphone app surface that follows this layered specification while preserving the deterministic evaluator API.

Target files:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- optional `docs/ui-interaction-audits/`

Forbidden:

- changing deterministic triage logic
- changing validator fixtures
- changing source ingestion policy
- adding raw external medical text ingestion
- initializing Git
- publishing or releasing

Verification:

- run the Future Verification Commands listed above
- capture screenshots at 360, 390, and 430 CSS px widths
- run a UI interaction audit for visible and menu-revealed controls
- verify P0 119 priority and #7119 locale gating

Done:

- smartphone app screen architecture is implemented
- desktop Web is only a host for the smartphone app surface
- deterministic behavior does not regress
- prototype decisions are deliberately reused or explicitly discarded
