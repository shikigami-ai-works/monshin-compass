# Triage Output Contract

作成日: 2026-06-25  
対象: 問診コンパス fever/cough/dyspnea MVP  
実装参照: `tools/evaluate_symptom_case.py`

## 1. 目的

症状カード入力から、UI表示・RAG根拠取得・監査ログへ渡すJSON出力を固定する。

このcontractは診断APIではない。出力は「症状整理」「red flag優先度」「次に確認するカード」「根拠sourceの参照情報」に限定する。

## 2. 入力

入力は症状カードIDと内部値の配列とする。

```json
[
  {"card_id": "fever", "value": "yes"},
  {"card_id": "cough", "value": "yes"},
  {"card_id": "dyspnea", "value": "moderate"}
]
```

CLIでは次の3形式を受け取る。

- `--set fever=yes --set cough=yes`
- `--json '{"fever":"yes","cough":"yes"}'`
- `--fixture SCHEMA-TC-002`

## 3. 出力スキーマ

必須フィールド:

```json
{
  "triage_priority": "P0 | P1 | P2 | P3",
  "matched_rule_ids": ["RF-P1-DYSPNEA-MODERATE"],
  "matched_card_ids": ["dyspnea"],
  "action_code": "seek_urgent_medical_advice",
  "evidence_types": ["seek_care_guidance"],
  "needs_more_input": false,
  "next_question_card_id": null,
  "source_requirements": ["us.medlineplus.emergency_signs"],
  "source_records": [],
  "rag_transfer_mode": "metadata_plus_human_authored_summary",
  "raw_page_text_to_rag_default": false,
  "display_block": "p1_seek_medical_advice",
  "forbidden_output": ["diagnosis", "treatment", "reassurance_no_care_needed"],
  "selected_cards": [],
  "safety_boundary": {}
}
```

## 4. フィールド定義

| field | type | 意味 |
|---|---|---|
| `triage_priority` | string | `P0/P1/P2/P3` の最高優先度 |
| `matched_rule_ids` | string[] | 発火したred flag rule ID。同一priority内は複数可 |
| `matched_card_ids` | string[] | 発火ruleに接続された症状カードID |
| `action_code` | string | UI/文面テンプレ選択用の行動コード |
| `evidence_types` | string[] | RAG・説明文に必要な根拠タイプ |
| `needs_more_input` | boolean | 追加質問が必要か |
| `next_question_card_id` | string/null | 次に1つだけ優先表示する症状カードID |
| `source_requirements` | string[] | 必要なsource_id |
| `source_records` | object[] | sourceのtitle/url/取得日/権利状態 |
| `rag_transfer_mode` | string | RAGへ渡せる情報の既定モード |
| `raw_page_text_to_rag_default` | boolean | 外部ページ本文をRAGへ直接渡す既定許可 |
| `display_block` | string | UI表示テンプレID |
| `forbidden_output` | string[] | LLM/UIが出してはいけない表現カテゴリ |
| `selected_cards` | object[] | 評価に使った入力カード |
| `safety_boundary` | object | 診断・治療ではないことを示す境界 |
| `jp_emergency_route` | object/null | `--locale` 指定時のみ追加される日本向け救急相談導線 |

## 5. priority動作

| priority | UI動作 | RAG動作 |
|---|---|---|
| `P0` | 緊急行動を最上段に出す。病名候補は出さない | emergency_signのみ短く参照 |
| `P1` | 早めの医療相談・受診相談材料を出す | seek_care_guidanceを優先 |
| `P2` | 追加質問または近日中相談を出す | symptom_overview/seek_care_guidanceを制限付きで参照 |
| `P3` | 観察メモと悪化時条件を出す | symptom_overview/self_observationのみ |

P3でも「安全」「受診不要」とは表示しない。

## 6. source_records

`source_records` は本文ではなく、根拠sourceのメタデータと利用境界を返す。

```json
{
  "source_id": "us.medlineplus.er_adult",
  "title": "When to use the emergency room - adult",
  "publisher": "National Library of Medicine / MedlinePlus",
  "url": "https://medlineplus.gov/ency/patientinstructions/000593.htm",
  "retrieved_at": "2026-06-25",
  "source_updated_at": "2024-09-04",
  "status": "metadata_only_until_rights_review",
  "raw_rag_ingest_allowed": false,
  "embedding_allowed": false,
  "requires_rights_review_before_storage": true
}
```

`raw_rag_ingest_allowed=false` のsourceは、本文保存・embedding・vector index化・RAG chunk化をしない。

## 7. 回答不能条件

次のいずれかでは、回答不能テンプレへ落とす。

- `matched_rule_ids` が空で、`selected_cards` も空
- `next_question_card_id` が必要なのにUIが追加質問を出せない
- `source_records` が空で、`evidence_types` が `unsupported` 以外
- rights review未完了sourceの本文をRAGへ渡さないと回答できない
- ユーザーが診断名、治療、薬剤、用量、受診不要断定を求めている

## 8. 検証コマンド

```powershell
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\validate_symptom_cards.py' --root 'D:\monshin-compass'
```

```powershell
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\evaluate_symptom_case.py' --root 'D:\monshin-compass' --fixture SCHEMA-TC-002
```

locale付き出力:

```powershell
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\evaluate_symptom_case.py' --root 'D:\monshin-compass' --locale JP-13 --fixture SCHEMA-TC-002
```
