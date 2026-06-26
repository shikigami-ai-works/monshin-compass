# Japanese Copy And Encoding QA For Monshin Compass

Created: 2026-06-25  
Status: report-first QA; no implementation replacement performed  
Scope: `docs/`, `data/`, `web/`, `app/server.py` display-copy path, and relevant `tools/` output paths

## Executive Summary

This pass audited Japanese UI copy, mojibake-like strings, and dangerous medical wording before the next smartphone UI implementation.

Key findings:

- `web/index.html`, `web/app.js`, `app/server.py`, and `data/*.yaml` are readable as UTF-8 through `rg`. Some PowerShell `Get-Content` output renders mojibake, but that is a terminal/display decoding artifact and should not be treated as file-level corruption by itself.
- The highest user-visible risk is not mass mojibake replacement. The real risk is promoting copy from the wrong layer:
  - visible UI copy needs medical-boundary review,
  - `data/symptom-cards.yaml` UI labels are future UI candidates,
  - `blocked_terms` intentionally contain dangerous diagnosis/treatment/dosage terms and must be preserved as internal safety filters,
  - source titles/publishers are metadata and should not be rewritten as app copy.
- `web/app.js` currently contains readable Japanese copy and passes `node --check`, but several strings still need copy review before the next UI rebuild.
- `app/server.py` exposes card/value labels through `/api/cards`; this is a UI-visible path and must be included in the future replacement ticket even though it is not part of the user-specified `web/` files.
- The only confirmed mojibake-like file paths found by `rg` are historical archive pointer paths in `docs/development-logs/`; these are internal evidence pointers, not UI copy.

Highest-risk decision:

- Do not blindly normalize or delete all suspicious Japanese strings. Some suspicious terms are deliberate guardrails, especially `blocked_terms` containing diagnosis, medication, dosage, and "受診不要判断".

## Source And Reachability Map

| Area | User-visible reach | QA result | Treatment |
|---|---:|---|---|
| `web/index.html` | Directly visible | Readable UTF-8; several strings need final-copy review | Replace in future implementation pass only |
| `web/app.js` | Directly visible | Readable UTF-8; core result/question copy needs final-copy review | Replace in future implementation pass only |
| `app/server.py` | Visible through `/api/cards` | Readable UTF-8; API copy can reach fallback UI | Include in future copy replacement ticket |
| `data/symptom-cards.yaml` | Potentially visible if consumed by API/UI | Readable UTF-8; many usable labels, plus internal blocked terms | Separate UI copy fields from internal guard fields |
| `data/jp-emergency-routing.yaml` | Route labels and warnings can reach UI | Readable UTF-8; #7119 gating is preserved | Preserve semantics; review wording only |
| `data/evidence-sources.yaml` | Source screen metadata | Source metadata, not app copy | Preserve source titles/publishers |
| `tools/*.py` | CLI/debug output | Mostly debug/test labels and JSON fields | Keep internal/debug-only unless surfaced in UI |
| `docs/development-logs/*` | Not UI visible | Archive pointer paths include mojibake-like path text | Preserve as historical evidence pointer |

## Highest-Risk User-Facing Strings

| File | Approx location | Current string | Classification | User-visible risk | Proposed canonical Japanese copy | Fix now or defer |
|---|---:|---|---|---|---|---|
| `web/app.js` | 75-77 | `動くと息切れ` / `動くと息切れしますか？` / `「いいえ」は軽い息苦しさとして扱います。` | `user-facing-needs-copy-review` | "No" meaning mild dyspnea can be misunderstood as ordinary denial. This is a safety-state mapping question and must be clearer. | `動くと息が切れますか？` / `強い息苦しさではない場合も、つらさが残るときは次の確認に進みます。` | Defer to implementation ticket |
| `web/app.js` | 434-442 | `#7119は全国番号として直接表示せず、実施エリア確認へ案内します。` | `user-facing-needs-copy-review` | Safe intent is correct, but this should be route-block copy tied to resolver state, not generic warning. | `地域が未確認のため、#7119は直接表示しません。実施エリアを確認してください。強い症状や急な悪化では119を優先してください。` | Defer |
| `web/app.js` | 439-440 | `${jurisdiction}: #7119 を表示できます。` | `user-facing-needs-copy-review` | Could sound like unconditional permission if copied outside confirmed-locale branch. | `${jurisdiction}: 確認済みの地域相談先として #7119 を表示します。強い症状や急な悪化では119を優先してください。` | Defer |
| `web/index.html` | 46 | `このプロトタイプは診断ではなく、ローカルルールで次の行動を整理します。` | `user-facing-needs-copy-review` | "Prototype" is acceptable for dev but not final app copy. | `この画面は診断ではありません。入力から次の行動の目安を整理します。` | Defer |
| `web/index.html` | 121 | `この画面は診断・治療ではありません。強い症状や急な悪化がある場合は119を最優先してください。` | `user-facing-needs-copy-review` | Direction is good; should name example red flags more concretely. | `この画面は診断・治療ではありません。強い息苦しさ、胸痛、意識の変化、血が混じる、急な悪化がある場合は119を優先してください。` | Defer |
| `web/app.js` | 191 | `現時点の入力では高い緊急サインは未確認` | `user-facing-needs-copy-review` | Good boundary, but result screen must pair it with escalation conditions so P3 is not read as safe. | `現時点の入力では高い緊急サインは確認されていません。症状が強くなる、急に悪化する、息苦しさや胸痛が出る場合は相談してください。` | Defer |
| `app/server.py` | 24-72 | `SAFE_CARD_COPY`, `SAFE_VALUE_COPY` labels | `user-facing-needs-copy-review` | API-visible fallback copy can reach UI; must match final UI vocabulary. | Use canonical copy table below. | Defer |
| `data/symptom-cards.yaml` | `ui.*_ja`, `question.*_prompt_ja` | Card labels, prompts, helper copy | `user-facing-needs-copy-review` | Many are readable and useful, but they are data-layer copy. Promoting them without QA can bypass UI style and safety rules. | Use as input candidates, not automatic UI source. | Defer |

## Classification Table

Label coverage note:

- `user-facing-broken`: no confirmed source-level UTF-8 instance found in current visible UI files. If browser-rendered screenshots show mojibake, classify that rendered string as `user-facing-broken` immediately.
- `unknown-needs-human-decision`: used for crisis/self-harm and medical-risk wording that should not be finalized by copy cleanup alone.

| File | Approx location | Current string or pattern | Classification | User-visible risk | Proposed canonical Japanese copy, if applicable | Fix now or defer |
|---|---:|---|---|---|---|---|
| `web/index.html` | 15 | `本文へ移動` | `internal-only-ok` | Low; accessibility skip link is fine. | Keep. | Defer/no fix |
| `web/index.html` | 19, 24, 50, 53, 80, 99 | `アプリヘッダー`, `メニュー`, `質問の進捗`, `質問カード`, `回答`, `暫定アクションメーター` | `user-facing-needs-copy-review` | Low-to-medium; mostly accessible names. Need consistency with final app shell. | Keep meaning; polish in final UI audit. | Defer |
| `web/index.html` | 44-46 | Menu reset/skip and prototype disclaimer | `user-facing-needs-copy-review` | Medium; final app should not say prototype, and skip must not imply required safety questions can be skipped. | `最初からやり直す`; `この質問をスキップ`; disclaimer copy from style guide. | Defer |
| `web/index.html` | 81-95 | `はい`, `いいえ`, `わからない`, `戻る` | `user-facing-needs-copy-review` | Low; safe if mapped correctly. Need ensure no button appears without outcome. | Keep, but pair with question-specific meaning when severity scale is used. | Defer |
| `web/index.html` | 102-104 | `観察`, `相談`, `救急` | `user-facing-needs-copy-review` | Medium; can be read as final safety state if shown during questions. | `記録`, `相談`, `救急` or keep only with `判定中` status. | Defer |
| `web/index.html` | 119-121 | Safety boundary block | `user-facing-needs-copy-review` | High-value copy; must remain visible on result. | Use expanded safety boundary copy. | Defer |
| `web/index.html` | 126-141 | `該当した確認項目`, `回答メモ`, `ルート注意`, `参照ソース` | `user-facing-needs-copy-review` | Low; good structure, final wording can be simpler. | `該当した項目`, `回答メモ`, `地域ルートの注意`, `参照した情報源`. | Defer |
| `web/app.js` | 18-105 | Hard-coded MVP question text | `user-facing-needs-copy-review` | Medium; readable but should align with layered spec and safety confirmation model. | Use canonical question table. | Defer |
| `web/app.js` | 150-161 | `actionCopy`, `actionHeading` | `user-facing-needs-copy-review` | High; result headings shape medical risk perception. | Use priority heading table. | Defer |
| `web/app.js` | 164-181 | `cardCopy`, `valueCopy` | `user-facing-needs-copy-review` | Medium; labels are readable but need shared canonical map with API copy. | Use canonical card/value labels. | Defer |
| `web/app.js` | 184-192 | `ruleCopy` | `user-facing-needs-copy-review` | Medium; matched reason summaries must not diagnose. | Keep symptom/reason phrasing only; no disease names. | Defer |
| `web/app.js` | 194-201 | `warningCopy` for #7119 | `user-facing-needs-copy-review` | Medium-high; wording must preserve locale gating and P0 119 priority. | Use route copy table. | Defer |
| `web/app.js` | 206-252 | SVG `aria-label`s: `体温計`, `咳`, `肺`, `注意`, `カレンダー`, `悪化` | `user-facing-needs-copy-review` | Low; accessible names are readable. | Keep or make symptom-specific in final audit. | Defer |
| `web/app.js` | 320-342 | Meter status copy | `user-facing-needs-copy-review` | Medium; "傾いています" can imply provisional triage certainty. | `入力をもとに確認中`; `救急の確認が必要です`; `相談の確認が必要です`. | Defer |
| `web/app.js` | 434-442 | Route copy | `user-facing-needs-copy-review` | High; #7119 and 119 handling are safety-critical. | Use route copy table. | Defer |
| `web/app.js` | 477 | `JSON.stringify(result)` in visible details | `debug-only` | Low if details remain developer/audit-only; risk if exposed to general users. | Hide behind dev/audit mode for production. | Defer |
| `web/app.js` | 520-532 | Source rows: source title, publisher, raw flag | `source-metadata` | Low; source metadata is expected. Avoid raw technical booleans in final user UI. | `本文取り込み: 未許可` instead of raw boolean for user UI. | Defer |
| `app/server.py` | 24-72 | API card/value copy | `user-facing-needs-copy-review` | Medium-high because `/api/cards` can feed UI fallback labels. | Align with canonical card/value labels. | Defer |
| `data/symptom-cards.yaml` | `ui.label_ja`, `short_label_ja`, `helper_text_ja` | readable card copy | `user-facing-needs-copy-review` | Medium; data copy should not automatically become final UI copy. | Treat as candidate source, then centralize final copy. | Defer |
| `data/symptom-cards.yaml` | `blocked_terms` | `解熱剤の用量`, `心筋梗塞診断`, `受診不要判断`, etc. | `fixture-preserve` | High if displayed; positive if kept internal. These are guardrail terms. | Do not display. Do not delete. Preserve as blocked terms. | Defer/no direct rewrite |
| `data/jp-emergency-routing.yaml` | 42, 69 | `日本（地域未特定）`, `東京都` | `source-metadata` | Low; route labels are valid and needed. | Keep. | Defer/no fix |
| `data/jp-emergency-routing.yaml` | 53-55, 82-84, 96-107 | English route warnings | `debug-only` / `source-metadata` | Medium if shown raw to users. `web/app.js` already maps some warnings; unmapped warnings can leak English. | Map all route warnings to reviewed Japanese or mark debug-only. | Defer |
| `data/evidence-sources.yaml` | publisher/title/url fields | Source names and titles | `source-metadata` | Low; these should remain faithful to sources. | Keep source titles; wrap with user-facing explanation. | Defer/no rewrite |
| `data/symptom-cards.yaml` | `self_harm` card copy | `自分や他人を傷つけそう`, `今すぐ安全確保が必要ですか？` | `unknown-needs-human-decision` | High; crisis wording needs human/medical/legal review and must not improvise counseling. | Keep P0 emergency priority; draft reviewed crisis copy separately. | Defer |
| `tools/evaluate_symptom_case.py` | JSON output keys | `forbidden_output`, `source_records`, etc. | `debug-only` | Low; only visible through JSON details. | Keep. Hide raw JSON outside audit/dev. | Defer |
| `tools/resolve_jp_emergency_route.py` | route warnings | English warning strings | `debug-only` | Medium if passed raw to UI without mapping. | Keep internally; require UI warning mapper coverage. | Defer |
| `docs/development-logs/2026-06-25-card-compass-spec-session-ledger.md` | 52-53 | mojibake-like archive path | `internal-only-ok` | None for app UI; historical evidence pointer. | Preserve. | No fix |
| `docs/mobile-question-wizard-spec.md` | prototype copy | readable Japanese prototype strings | `internal-only-ok` | Medium if treated as current authority. | Use only as reference; current authority is layered spec. | No direct fix |
| `docs/smartphone-app-screen-spec.md` | layered spec | mostly English safety spec | `internal-only-ok` | Low; not UI. | Keep as authority. | No fix |

## Canonical Copy Proposals

### Core Boundary Copy

| Use | Proposed copy |
|---|---|
| Short boundary | `この画面は診断ではありません。入力から次の行動の目安を整理します。` |
| Result boundary | `この画面は診断・治療ではありません。強い息苦しさ、胸痛、意識の変化、血が混じる、急な悪化がある場合は119を優先してください。` |
| Evidence boundary | `優先度はローカルの安全ルールで判定しています。情報源は説明文と確認材料のために表示しています。` |
| Unknown explanation | `わからない場合は「わからない」を選んでください。安全上必要な項目は追加で確認します。` |

### Primary Controls

| Current role | Proposed copy |
|---|---|
| yes | `はい` |
| no | `いいえ` |
| unknown | `わからない` |
| back | `戻る` |
| reset | `最初からやり直す` |
| skip optional | `この質問をスキップ` |
| review answers | `回答を見直す` |
| evidence/source | `参照した情報を見る` |
| emergency escape | `今すぐ危ない症状がある` |

### MVP Questions

| Card | Proposed title | Proposed question | Notes |
|---|---|---|---|
| `fever` | `熱っぽい` | `熱っぽさや発熱はありますか？` | Do not require measured temperature. |
| `cough` | `咳が出る` | `咳はありますか？` | Include dry cough/sputum in helper only. |
| `dyspnea` | `息苦しさ` | `息苦しさはありますか？` | Safety-relevant; do not skip silently. |
| `dyspnea_severe` | `強い息苦しさ` | `じっとしていても強く息苦しいですか？` | P0-facing confirmation. |
| `dyspnea_moderate` | `動いた時の息切れ` | `少し動くと息切れしますか？` | Avoid saying "no means mild" too bluntly. |
| `duration` | `続いている期間` | `発熱や咳は4日以上続いていますか？` | Unknown allowed. |
| `worsening` | `悪化している` | `時間とともに悪化していますか？` | Escalation-sensitive. |

### Priority Headings

| Priority | Proposed heading | Notes |
|---|---|---|
| P0 | `119を優先してください` | Must dominate result. |
| P1 | `早めに医療相談してください` | Include 119 caveat for strong/rapid worsening symptoms. |
| P2 | `追加確認または近日中の相談を検討してください` | Avoid "safe". |
| P3 | `記録しながら変化を確認してください` | Pair with escalation conditions; never "受診不要". |

### Route Copy

| Resolver state | Proposed copy |
|---|---|
| P0 / `call_119_now` | `119を優先してください。#7119より前に表示します。` |
| Confirmed JP-13 / `offer_confirmed_7119` | `東京都で確認済みの相談先として #7119 を表示しています。強い症状や急な悪化がある場合は119を優先してください。` |
| Unconfirmed JP / `check_7119_area_before_display` | `地域が未確認のため、#7119は直接表示しません。実施エリアを確認してください。強い症状や急な悪化では119を優先してください。` |
| Child secondary route | `子どもの相談先として #8000 が使える場合があります。利用時間や対象地域を確認してください。` |
| Self-harm support | `今すぐ危険がある場合は119を優先してください。相談窓口の情報は補助として表示します。` |

### Source Display

| Current data | Proposed user-facing display |
|---|---|
| `publisher` | `発行元: {publisher}` |
| `title` | `{title}` |
| `retrieved_at` | `取得日: {date}` |
| `source_updated_at` | `更新日: {date or 未確認}` |
| `raw_rag_ingest_allowed=false` | `本文取り込み: 未許可（メタデータのみ）` |

## Strings To Preserve

Preserve these as internal safety, fixture, or metadata strings:

- `data/symptom-cards.yaml` `blocked_terms`, including:
  - `解熱剤の用量`
  - `咳止めの用量`
  - `吸入薬の用量`
  - `心筋梗塞診断`
  - `ニトログリセリン用量`
  - `認知症診断`
  - `病名確定`
  - `皮膚疾患診断`
  - `原因診断`
  - `抗けいれん薬の用量`
  - `髄膜炎診断`
  - `鎮痛薬の用量`
  - `下痢止めの用量`
  - `個別診断`
  - `受診不要判断`
- `forbidden_output` values such as `diagnosis`, `treatment`, `reassurance_no_care_needed`.
- Source titles, publishers, URLs, `source_id`s, and evidence metadata in `data/evidence-sources.yaml`.
- Route policy keys and fixture expectations in `data/jp-emergency-routing.yaml`, `tools/`, and tests.
- Historical archive pointer paths in `docs/development-logs/`.

These strings may look dangerous or strange, but their purpose is to prevent unsafe output or preserve auditability.

## Strings Requiring Human Or Medical Review

These should not be treated as final production copy without review:

- Any wording that tells the user what to do after P0/P1/P2/P3.
- Any P3 wording. It must avoid "安全", "大丈夫", "受診不要", or equivalent reassurance.
- Self-harm / crisis wording. The app must route immediate danger to emergency help and should not improvise mental-health advice.
- Child, pregnancy, older-adult, immunocompromised, chronic-condition wording. These can change risk interpretation and should stay action-guidance only.
- #7119/#8000 route wording. Availability and hours can vary by region.
- Source/evidence wording that could imply external sources made the deterministic priority decision.

## Japanese Copy Style Guide

### Principles

- Lead with the next action, not a diagnosis.
- Use short, plain Japanese.
- Use "確認", "相談", "記録", "119を優先" instead of "安全", "治療", "診断".
- Treat "わからない" as a first-class answer.
- Say "確認されていません" instead of "ありません" when the app lacks enough certainty.
- Say "相談してください" or "119を優先してください"; do not say "受診不要です".
- Keep route copy tied to resolver output.
- Keep source copy as metadata. Do not turn source title into medical instruction.

### Forbidden UI Phrases

Do not use:

- `診断名は...`
- `あなたは...病です`
- `治療してください`
- `この薬を飲んでください`
- `用量は...`
- `受診不要です`
- `安全です`
- `大丈夫です`
- `緊急性はありません`
- `#7119は全国で使えます`

### Allowed Patterns

Use:

- `この画面は診断ではありません。`
- `入力から次の行動の目安を整理します。`
- `現時点の入力では高い緊急サインは確認されていません。`
- `症状が強くなる、急に悪化する、息苦しさや胸痛が出る場合は相談してください。`
- `119を優先してください。`
- `地域が未確認のため、#7119は直接表示しません。`
- `本文取り込みは未許可のため、メタデータのみ表示します。`

## Implementation Replacement Plan

Ticket: Apply reviewed Japanese copy without changing deterministic logic

Objective:

- Replace visible UI copy and API-visible copy with reviewed Japanese while preserving all evaluator, route, and fixture semantics.

Target files:

- `web/index.html`
- `web/app.js`
- `app/server.py`
- optional docs update to `docs/ui-interaction-audits/`

Possible target after review:

- `data/symptom-cards.yaml` only if Shiki explicitly opens data-copy cleanup. Do not touch blocked terms.

Forbidden:

- deterministic triage logic changes
- red flag rule meaning changes
- fixture normalization
- deleting or replacing `blocked_terms`
- changing #7119 locale gating
- weakening P0 119 priority
- adding diagnosis, treatment, medication, dosage, or "care unnecessary" reassurance

Steps:

1. Add a small centralized UI copy map for visible labels and result text.
2. Replace `web/index.html` static labels with canonical copy.
3. Replace `web/app.js` question, action, route, warning, meter, and result copy.
4. Replace `app/server.py` `SAFE_CARD_COPY` and `SAFE_VALUE_COPY` with the same canonical vocabulary.
5. Ensure `data/symptom-cards.yaml` `blocked_terms` are never shown in visible UI.
6. Ensure raw JSON output remains debug/audit-only.
7. Ensure all route warnings shown to users have reviewed Japanese mappings.

Done criteria:

- No visible mojibake in UI.
- No forbidden medical copy appears.
- P0 route copy prioritizes 119.
- #7119 appears only when resolver allows `show_7119_direct=true`.
- P3 does not imply safety or care unnecessary.
- Internal/fixture/blocked terms are preserved.

## Verification Plan

### Report-Only Verification Performed

- Searched `docs/`, `data/`, `web/`, `app/server.py`, and relevant `tools/` paths for:
  - mojibake-like strings
  - non-ASCII Japanese copy
  - dangerous medical wording
  - #7119 / 119 routing text
  - UI reachability points
- Confirmed `node --check web/app.js` passes.
- Confirmed no implementation files were intentionally changed in this report pass.
- Confirmed current `data/symptom-cards.yaml` dangerous diagnosis/treatment/dosage terms are in `blocked_terms`, so they should be preserved rather than rewritten.
- Confirmed P0 / 119 and #7119 locale-gating rules are not weakened by this report.
- `git status --short` could not run because `D:\monshin-compass` is not a Git repository.

### Future Implementation Verification

- Run:

```powershell
node --check 'D:\monshin-compass\web\app.js'
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\smoke_api.py'
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\validate_symptom_cards.py' --root 'D:\monshin-compass'
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\resolve_jp_emergency_route.py' --root 'D:\monshin-compass' --run-fixtures
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\evaluate_symptom_case.py' --root 'D:\monshin-compass' --locale JP-13 --fixture SCHEMA-TC-001
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\evaluate_symptom_case.py' --root 'D:\monshin-compass' --locale JP-13 --fixture SCHEMA-TC-002
```

- Capture mobile screenshots at 360 / 390 / 430 CSS px.
- Run UI interaction audit.
- Search rendered DOM text for mojibake-like patterns.
- Confirm no `blocked_terms` appear in visible UI.
- Confirm deterministic evaluator output is unchanged before and after copy replacement.

## Experience Extracted

- Encoding QA must distinguish actual file encoding from terminal display corruption. PowerShell output alone is not enough evidence of broken source text.
- The dangerous strings in this project are often guardrails, not bugs. `blocked_terms` should be protected, not cleaned up.
- UI copy should be centralized enough that `web/` and `/api/cards` cannot drift into different medical wording.
- P3 copy is a special risk. "No high-priority red flag confirmed" is acceptable only when paired with escalation conditions.
- Route copy is safety logic in words. #7119 wording must be generated from resolver state, not pasted as static copy.
