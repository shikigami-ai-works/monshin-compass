# Implementation Notes

## 2026-06-26: Runtime UI Audit And Scroll Reset

Target files:

- `web/app.js`
- `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-26_asocfull-20ticket-runtime.md`
- `docs/implementation-notes.md`
- `docs/development-progress.md`

Decision:

1. `showScreen()` now resets window scroll to the top after screen changes.
   - Reason: runtime Playwright audit found that moving from a scrolled Result screen to Evidence preserved the prior page scroll offset, clipping the header controls above the viewport.
   - Tradeoff accepted: every app screen transition returns to the top of the new screen instead of preserving scroll position. This matches the smartphone app model better than carrying body scroll across distinct screens.
   - Impact: Evidence, Review, Settings, and Result transitions start with their header and primary content visible.
   - Spec update needed later: optional. The current state/flow spec implies screen-level navigation; it does not explicitly name scroll restoration.
2. Runtime UI verification can use the existing bundled Node Playwright runtime when the target localhost browser path is allowed.
   - Reason: no install was needed, and the check exercised the actual local server and static/API route.
   - Tradeoff accepted: `.codex/runtime_ui_audit.cjs` is an ignored local verification harness, not a source-controlled product test suite yet.
   - Impact: screenshots and JSON evidence were written under ignored `outputs/runtime/2026-06-26-runtime-ui-audit/`.
   - Spec update needed later: consider promoting the runtime audit harness into a committed test if this UI remains active.

Verification:

- `node --check .\web\app.js`
- `python .\tools\smoke_api.py`
- `python .\tools\validate_symptom_cards.py --root D:\monshin-compass`
- `python .\tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
- `python .\tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001`
- `python .\tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`
- `rg -n -e 'href="#"' -e 'javascript:void' -e 'console\.log' -e 'TODO' -e 'onclick=' web`
- Runtime Playwright audit: 205 pass / 0 fail, 14 screenshots, 0 console errors/warnings.

Experience extracted:

- Runtime interaction audits should be allowed to produce small UI fixes; otherwise the audit becomes documentation of known breakage.
- A screen router owns scroll state as much as visible screen state in a smartphone shell.
- External evidence links need click behavior verification while still avoiding raw external page ingestion.

## 2026-06-25: ASOCFULL 20-Ticket Smartphone App Shell Implementation

Target files:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-25_asocfull-20ticket-source.md`
- `docs/implementation-notes.md`
- `docs/development-progress.md`

Decisions:

1. The Web UI was rebuilt as a smartphone app shell instead of polishing the prototype card page.
   - Reason: `docs/smartphone-app-screen-spec.md` now separates product screens, state, safety invariants, and Web conversion rules. The previous UI was useful evidence but had prototype-era information architecture and mojibake user-facing copy.
   - Impact: the app now exposes Launch, Region Confirmation, Question Card, Safety Confirmation, Result / Next Action, Evidence / Source, Settings / Help, and Review Answers screens.
2. Readable UI copy now lives in `web/app.js` instead of using mojibake labels from `data/` or `/api/cards`.
   - Reason: existing data labels are valid fixture/source artifacts but unsafe as user-facing medical-adjacent copy.
   - Impact: API data remains authoritative for deterministic values, while user-facing copy is curated in the UI layer until a fuller copy/encoding pass exists.
3. The deterministic evaluator API remains unchanged.
   - Reason: the implementation pass must not rewrite P0/P1/P2/P3 logic, validators, route resolver behavior, or source policy.
   - Impact: `web/app.js` sends structured `selected_cards` and uses evaluator/route outputs for priority and route display.
4. #7119 display is gated in UI text.
   - Reason: direct #7119 display is allowed only when the route resolver returns `show_7119_direct=true` and a consultation phone.
   - Impact: Tokyo / JP-13 can show #7119 for P1; Japan / area unconfirmed does not display #7119 as a direct phone route.
5. Runtime browser QA is recorded as blocked, not passed.
   - Reason: the browser automation layer rejected `http://127.0.0.1:8765/` and disallowed workaround through alternate browser surfaces.
   - Impact: static/API validation passed, but screenshots and click proof remain manual confirmation items.

Removed existing functionality:

- The prototype single question/result surface was replaced by the layered smartphone app flow.
- Mojibake user-facing UI strings were removed from the Web shell.
- No deterministic core, data, validator, or route resolver functionality was removed.

Verification:

- `node --check web\app.js`
- `python tools\smoke_api.py`
- `python tools\validate_symptom_cards.py --root D:\monshin-compass`
- `python tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`
- Source scan for placeholder links, TODO-only controls, console-only handlers, and inline click handlers.

Not verified:

- Browser screenshots at 360 / 390 / 430.
- Runtime click path and visual overlap inspection.
- Real-device mobile behavior.

Experience extracted:

- For this project, "copy layer" is a safety layer: readable Japanese cannot be treated as cosmetic polish.
- Browser QA blockers must be recorded as blockers, not converted into unofficial Playwright/Chrome workarounds.
- Data fixtures can remain mojibake while UI copy is clean, as long as deterministic IDs/values remain the contract boundary.
- Route display should depend on resolver fields, not string matching or locale names.

## 2026-06-25: Layered Smartphone App Spec Rewrite

Target files:

- `docs/smartphone-app-screen-spec.md`
- `docs/implementation-notes.md`
- `docs/development-progress.md`

Decision:

1. `docs/smartphone-app-screen-spec.md` was rewritten as a layered specification instead of a single mixed screen document.
   - Reason: safety invariants, product intent, state/flow, screen requirements, and Web implementation planning were beginning to overlap. That creates a high risk that later UI polish weakens safety behavior or treats prototype layout as product architecture.
   - Impact: the next implementation pass can start from authority order: safety/core contracts, deterministic data, product journey, state/flow, screens, then Web conversion.
2. The current `web/` implementation remains a prototype reference only.
   - Reason: it has useful wiring and verification evidence, but its information architecture was shaped by earlier Web/mobile-card experiments.
   - Impact: future UI work may reuse handlers, result rendering ideas, and audit lessons only after deliberate review.
3. The deterministic core remains unchanged.
   - Reason: this pass is docs-only and must not alter P0/P1/P2/P3 logic, evaluator fixtures, route resolver behavior, source policy, or validators.
   - Impact: implementation work remains bounded to UI architecture unless Shiki explicitly opens a safety/core change.
4. User-facing copy and encoding were called out as a separate risk.
   - Reason: some existing docs/data contain mojibake-style labels. Copying them directly into a medical-adjacent UI would be a safety and trust failure even if logic passes.
   - Impact: the implementation pass should either use reviewed copy or include a separate copy/encoding QA step.

Removed existing functionality:

- None. This was a documentation authority rewrite, not a runtime change.

Verification:

- Re-read the rewritten `docs/smartphone-app-screen-spec.md`.
- Confirmed the spec keeps P0 119 priority, #7119 locale gating, deterministic core authority, and the diagnosis/treatment/medication prohibition.
- Confirmed `web/`, `data/`, `tools/`, and runtime files were not edited in this pass.

Experience extracted:

- Layered specs are safer than one large UI spec when a product has medical-adjacent safety boundaries.
- Prototype evidence should be explicitly demoted before writing implementation tickets.
- Unknown/skipped answers need state semantics, not just button labels.
- Locale routing must be treated as a deterministic safety layer, not as copy.
- Encoding and Japanese copy QA should be planned as its own pass before the UI is considered user-safe.

## 2026-06-25: Smartphone App Spec Reset

Target files:

- `docs/smartphone-app-screen-spec.md`
- `docs/mobile-question-wizard-spec.md`
- `docs/development-progress.md`
- `docs/implementation-notes.md`

Decision:

1. The screen-design source of truth moved from `docs/mobile-question-wizard-spec.md` to `docs/smartphone-app-screen-spec.md`.
   - Reason: the current Web UI was successfully repaired, but the product should be designed as a smartphone-only app first, then expressed through a Web shell.
   - Impact: the next UI pass starts from app screens, navigation, one-handed operation, priority displays, and Web conversion rules instead of polishing the existing Web page.
2. The deterministic core remains authoritative.
   - Reason: red flag rules, triage output, symptom card values, JP routing, and validators already define the safety-critical behavior.
   - Impact: no triage logic, source policy, or evaluator fixtures are rolled back by this UI reset.
3. `docs/mobile-question-wizard-spec.md` is retained as prototype-era evidence.
   - Reason: the large-card Web prototype produced useful visual and interaction evidence, including screenshot and audit results.
   - Impact: current `web/` can donate implementation patterns, but it no longer dictates product screen architecture.

Removed existing functionality:

- None. This was a documentation authority reset, not a runtime rollback.

Experience extracted:

- A polished Web prototype can become an anchor too early; before continuing UI work, separate product screen architecture from Web viewport implementation.
- For this product, the correct design order is smartphone app model first, Web shell second, desktop presentation last.
- Keep safety-critical deterministic logic below the UI reset line so visual iteration cannot accidentally weaken triage behavior.

## 2026-06-25: ASOCFULL Mobile Skillpass Recovery

Target files:

- `web/styles.css`
- `web/app.js`
- `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-25_mobile-skillpass.md`

Decisions:

1. The mobile question screen was tightened to fit exactly inside `390 x 844` and `360 x 844` question viewports.
   - Reason: the previous recovery pass visually worked, but the rendered question surface still had a 2 px vertical overflow.
   - Impact: first-screen question states now report matching viewport and scroll heights with no clipped controls.
2. The mobile bottom padding was reduced by 3 px inside the question view.
   - Reason: the compact compass meter had enough bottom breathing room, and the extra padding caused a tiny scroll tail.
   - Impact: the compact meter remains visible while the whole question screen fits the target smartphone viewport.
3. Menu skip now closes the menu after advancing.
   - Reason: opening the menu and choosing skip advanced to the next question but left the menu panel covering the new card.
   - Impact: skip has a cleaner user-observable result: optional card is skipped, next card appears, and menu state resets.
4. Browser plugin was used for DOM, console, and page-state checks. Screenshot capture through the in-app Browser timed out on `Page.captureScreenshot`, so Playwright with installed Chrome was used for accurate saved screenshots.
   - Reason: the Browser screenshot failure is tooling-specific; DOM and console checks succeeded.
   - Impact: screenshot evidence is produced from a stable `390 x 844` / `360 x 844` mobile context without changing app runtime code.

Removed existing functionality:

- None.

Verification:

- `node --check web\app.js`
- `python tools\smoke_api.py`
- `python tools\validate_symptom_cards.py --root D:\monshin-compass`
- `python tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`
- Playwright mobile screenshots:
  - `outputs/runtime/asocfull-mobile-skillpass-final-initial-390x844-20260625.png`
  - `outputs/runtime/asocfull-mobile-skillpass-final-breathing-390x844-20260625.png`
  - `outputs/runtime/asocfull-mobile-skillpass-final-breathing-360x844-20260625.png`
  - `outputs/runtime/asocfull-mobile-skillpass-final-p1-result-390x844-20260625.png`

Experience extracted:

- For this app, "premium" must mean single-focus clinical flow, not landing-page hero structure.
- Accurate mobile screenshots need explicit browser viewport emulation; Chrome CLI `--screenshot` can crop misleadingly at small widths.
- A UI audit should include menu-revealed actions, because hidden secondary actions can leave stale overlay state even when the main answer buttons pass.

## 2026-06-25: ASOCFULL Reference-Copy GUI Tightening

Target files:

- `web/styles.css`
- `web/app.js`
- `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-25_reference-copy.md`

Decisions:

1. The progress row now visually matches the reference structure: horizontal rule segments flank the centered `N / 7` step label.
   - Reason: the previous row placed the line and number as separate stacked elements, which weakened the card-deck rhythm.
   - Impact: current step, completed cards, active card, and future cards read as one navigational object.
2. The active card and illustration were enlarged, especially for the breathing/lungs card.
   - Reason: the reference image makes the body-part card the main emotional and functional object, not a compact form panel.
   - Impact: the breathing question now feels closer to a tactile card and less like a generic mobile form.
3. Mobile framing now applies up to 540 px wide.
   - Reason: Chrome headless and some small desktop preview environments report a wider CSS viewport than the intended phone screenshot. The UI should still present the mobile app surface cleanly.
   - Impact: narrow preview screenshots no longer show a floating framed app with cropped right-side controls.
4. The compact compass meter received clearer zone marks.
   - Reason: the reference meter has a quick visual read for observe / consult / emergency. The previous meter relied too heavily on labels alone.
   - Impact: the meter remains secondary but now communicates the three zones faster.
5. Verification-only URL presets were added:
   - `?demo=breathing`
   - `?demo=p1-result`
   - Reason: deterministic visual verification needs stable access to the reference step and result screen without changing normal user flow.
   - Impact: normal launch still starts at the fever card; these presets are not visible controls.

Removed existing functionality:

- None.

Verification:

- `node --check web\app.js`
- `python tools\smoke_api.py`
- `python tools\validate_symptom_cards.py --root D:\monshin-compass`
- `python tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-001`
- `python tools\evaluate_symptom_case.py --root D:\monshin-compass --locale JP-13 --fixture SCHEMA-TC-002`
- Chrome headless screenshots saved under `outputs/runtime/`
- Browser error/warning log check returned no entries.

## 2026-06-25: ASOCFULL GUI Refinement Pass

Target files:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `web/favicon.svg`
- `docs/ui-interaction-audits/UI_INTERACTION_AUDIT_2026-06-25_main-wizard.md`

Decisions:

1. The mobile question screen now follows the large-card compass direction from `docs/mobile-question-wizard-spec.md` and the provided reference image.
   - Reason: the previous two-column/prototype layout weakened the card-deck metaphor and made the app feel like an internal tool.
   - Impact: the first screen is now a focused tactile card interaction with header, progress markers, illustrated card, primary answers, secondary answers, and compact compass meter.
2. The always-visible result side panel was removed from question screens.
   - Reason: it competed with the active question and made the mobile first viewport feel like a dashboard.
   - Impact: result details still exist, but only on the result screen after a stop or completion condition.
3. The persistent question-screen safety footer was removed.
   - Reason: `docs/mobile-question-wizard-spec.md` explicitly keeps the question screen focused and moves the safety boundary to the result screen.
   - Impact: safety boundary appears prominently on the result screen; no diagnostic/treatment reassurance copy is introduced.
4. The optional skip control moved from the main answer grid into the menu.
   - Reason: keeping skip visible beside primary answers added a third decision lane and pushed the compass below the fold.
   - Impact: skip is still available for optional questions; the main question screen now matches the reference two-primary plus two-secondary control hierarchy.
5. Raw rule IDs and English route warnings are translated to user-facing Japanese summaries on the result screen.
   - Reason: internal IDs and English warnings make the UI feel unfinished and reduce trust.
   - Impact: JSON output still contains raw deterministic data inside the details disclosure for debugging.

Verification:

- `node --check web\app.js`
- `python tools\smoke_api.py`
- `python tools\validate_symptom_cards.py --root D:\monshin-compass`
- `python tools\resolve_jp_emergency_route.py --root D:\monshin-compass --run-fixtures`
- Browser mobile screenshots at `390 x 844`
- Browser desktop screenshot at `1280 x 720`
- UI interaction audit saved under `docs/ui-interaction-audits/`

作成日: 2026-06-25

## 2026-06-25: Symptom Cards / Red Flag Local Data

対象ファイル:

- `data/symptom-cards.yaml`
- `data/red-flag-rules.yaml`
- `tests/fixtures/symptom-card-cases.jsonl`
- `tools/validate_symptom_cards.py`
- `tools/evaluate_symptom_case.py`

決定事項:

1. `*.yaml` は当面 JSON-compatible YAML subset とする。
   - 理由: 現在のローカルPython runtimeに PyYAML が無いため、標準ライブラリだけでvalidatorを動かす。
   - 影響: YAMLパーサでは読めるが、実体はJSON構文。後で依存関係を許可する場合は通常YAMLへ移行可能。

2. red flag の優先度・action_code・evidence_type・source_requirements は `data/red-flag-rules.yaml` を正とする。
   - 理由: 症状カード、fixture、validator内のルールIDが分散してズレるのを防ぐ。
   - 影響: validatorは `data/red-flag-rules.yaml` を読み、カード側の `connected_rule_ids` とfixtureの `expected_rules` を検証する。

3. red flag 条件評価の実行関数は `tools/validate_symptom_cards.py` 内の `RULE_CONDITIONS` に固定する。
   - 理由: 医療安全に関わる優先度判定をLLM/RAGへ委譲しないため。
   - 影響: `data/red-flag-rules.yaml` の `condition.implementation_key` とvalidator実装が1対1で一致しない場合は検証失敗にする。

4. `tools/evaluate_symptom_case.py` は1件の問診入力を評価する開発用CLIとする。
   - 入力: `--set card=value`、`--json`、または `--fixture case_id`
   - 出力: `triage_priority`, `matched_rule_ids`, `next_question_card_id`, `source_requirements`, `forbidden_output` などのJSON。

5. `data/evidence-sources.yaml` を根拠sourceの機械可読レジストリとする。
   - 理由: red flag ruleが要求する `source_id`、`evidence_type`、取得日、更新確認日、RAG投入境界をvalidatorで検証するため。
   - 影響: `tools/validate_symptom_cards.py` は `source_requirements` が存在するか、sourceが該当 `evidence_type` を扱えるかを検証する。

6. MedlinePlus / A.D.A.M. 系ページは raw RAG ingest 不可として扱う。
   - 理由: A.D.A.M. footerに automated extraction、embedding、retrieval-system indexing、AI training を書面許可なしで禁止する趣旨の記載があるため。
   - 影響: `data/evidence-sources.yaml` では `raw_rag_ingest_allowed=false`, `embedding_allowed=false`, `status=metadata_only_until_rights_review` とする。
   - 当面の利用: source metadata citation と human-authored short summary after review まで。raw page textを保存、埋め込み、インデックス化しない。

7. 日本向けsource laneを `data/evidence-sources.yaml` に追加し、red flag rulesの `source_requirements` を日本source優先に切り替える。
   - 追加source: 厚生労働省 #7119、総務省消防庁 #7119、#7119実施エリア、厚生労働省 #8000、消防庁 救急車利用マニュアル、消防庁 Q助、医療情報ネット（ナビイ）、厚生労働省COVID相談情報、厚生労働省まもろうよこころ、東京消防庁 #7119。
   - 理由: 日本国内展開でUS sourceを一次導線にすると、電話番号、相談制度、医療機関検索、地域実施エリアがズレるため。
   - 影響: 29 red flag rulesの `source_requirements` はすべて `jp.*` sourceに置換。US sourceは比較・補助・英語圏参考として残すが、通常評価出力には出さない。
   - 注意: #7119は全国一律ではなく実施エリア依存。東京消防庁sourceは自治体実装例または東京展開時のlocal laneとして扱う。

8. `data/jp-emergency-routing.yaml` と `tools/resolve_jp_emergency_route.py` で deployment locale 別の救急相談resolverを固定する。
   - 理由: #7119を全国一律の電話番号として表示する事故を防ぐため。
   - 影響: P0は常に119優先。`JP-13` / Tokyoでは#7119を表示可能。`JP` / unknownでは#7119を直接表示せず、消防庁実施エリア確認とQ助/医療情報ネットへ落とす。
   - 連携: `tools/evaluate_symptom_case.py --locale JP-13 ...` で評価結果に `jp_emergency_route` を同梱する。

## 2026-06-25: Mobile Question Wizard UI

対象ファイル:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `docs/mobile-question-wizard-spec.md`

決定事項:

1. スマホ主導線はカード一覧ではなく、1ページ1質問のウィザードにする。
   - 理由: 複数カードと3択以上の同格ボタンをスマホに並べると、イラスト、質問文、押下領域が小さくなり、問診の迷いが増えるため。
   - 影響: 初期表示は発熱1問だけを表示し、大きなSVGイラスト、質問文、`はい` / `いいえ` の2大ボタン、補助の `わからない` / `スキップ`、`戻る` / `リセット` を持つ。
2. UIは二択中心だが、内部triage値は単純なbooleanに潰さない。
   - 理由: 息苦しさなどの安全質問は、`ある/ない` だけではP0/P1の区別を失うため。
   - 影響: `dyspnea` は二択の追加質問を挟み、`none | mild | moderate | severe | unknown` に写像する。
3. P0/P1に到達したら通常質問を止め、結果確認状態に遷移する。
   - 理由: 緊急または早期相談のシグナルが出た後に通常質問を続けると、行動の優先順位が薄まるため。
   - 影響: P0では119優先表示、P1ではlocaleに応じた#7119/実施エリア確認表示を先に見せる。
4. 現在の初期質問は、しきの指定に合わせて発熱から開始する。
   - リスク: 安全ゲートを先頭に置かないため、強い息苦しさなどのP0候補が数問後になる。
   - 当面の緩和: safety footerで119優先条件を常時表示し、息苦しさ到達時にP0/P1なら即停止する。
   - 次の検討: 初回だけ「今すぐ危ない症状」へジャンプできる導線、または安全ゲート先行版との比較。

禁止事項:

- P0/P1/P2/P3判定をLLMの自由生成に任せない。
- P3を「安全」「受診不要」と表現しない。
- 診断名、治療、薬剤名、用量、受診不要断定を出力しない。
- RAG取得本文をそのまま長文でUIや回答へ流さない。
- rights review未完了の外部ページ本文をベクトルDB、検索index、学習データ、RAG chunkとして保存しない。

次の実装候補:

1. `tools/evaluate_symptom_case.py` の出力JSONをアプリAPIの契約に昇格する。
2. `data/evidence-sources.yaml` の日本sourceに対して、rights review結果を別フィールドで管理する。
3. `data/jp-emergency-routing.yaml` に東京以外の実施確認済み自治体laneを段階追加する。
4. 症状イラストUIの最小プロトタイプで、カード選択から評価CLI相当の結果までつなぐ。
