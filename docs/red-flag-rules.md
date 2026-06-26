# Red Flag Rules for 問診コンパス

作成日: 2026-06-25  
対象MVP: 症状イラスト選択型ナビ / 発熱・咳・息苦しさ  
依存文書: `docs/evidence-retrieval-contract.md`  
目的: P0/P1/P2/P3 の緊急度を症状カードIDと内部値に接続し、RAGやLLMより前に安全分岐できるようにする。

## 1. 結論

red flag 判定は診断ではない。ユーザー入力を「急いで相談すべき可能性があるか」で安全側に分類するルールである。

問診コンパスでは、P0/P1/P2/P3を次のように扱う。

| Priority | 意味 | UIの最上位表示 | RAGの扱い |
|---|---|---|---|
| P0 | 即時緊急の可能性 | 救急番号・地域の救急相談へ | emergency_sign の短い根拠だけ |
| P1 | 早急な医療相談候補 | 早めの受診相談・救急相談 | seek_care_guidance + emergency_sign |
| P2 | 近日中の相談候補 | 近日中の相談、悪化時の再確認 | seek_care_guidance + symptom_overview |
| P3 | セルフ観察補助 | 症状記録と悪化時条件 | symptom_overview + self_observation |

P0/P1では病名候補を広げない。出力は「安全行動」「医師・救急窓口に伝えるメモ」「根拠」までに制限する。

## 2. 参照根拠

この初期ルールは、次の公式・準公式医療情報を参考にした安全側の設計である。実装前に日本展開向けの地域窓口、救急番号、国内情報源を確認する。

| source_id | 名称 | 確認日 | ページ側の日付 | この文書での用途 |
|---|---|---|---|---|
| `us.medlineplus.emergency_signs` | MedlinePlus: Recognizing medical emergencies | 2026-06-25 | Review Date 2025-01-08 | 成人・小児の緊急サイン候補 |
| `us.medlineplus.er_adult` | MedlinePlus: When to use the emergency room - adult | 2026-06-25 | Review Date 2024-09-04 | 成人のER/救急相談目安 |
| `us.cdc.covid_symptoms` | CDC: Symptoms of COVID-19 | 2026-06-25 | 2025-03-10 | 呼吸器症状の緊急サイン補助 |

注意:

- MedlinePlus/CDCは米国情報源なので、地域の救急番号や相談窓口は展開地域に合わせて置換する。
- 参照根拠はred flag分類の安全設計に使う。診断や治療推奨には使わない。
- RAGに外部ページ全文を保存・投入しない。`docs/evidence-retrieval-contract.md` の本文量上限に従う。

## 3. 症状カードID

MVPで使うカードは「通常症状カード」と「安全確認カード」に分ける。UIではすべてを一度に出さず、選択済みカードと優先度に応じて追加確認する。

| card_id | 表示ラベル | 入力値 | 種別 | 備考 |
|---|---|---|---|---|
| `fever` | 熱っぽい | `yes/no/unknown` | normal | 体温が未入力でも可 |
| `cough` | 咳が出る | `yes/no/unknown` | normal | 血が混じる場合は `blood` も確認 |
| `dyspnea` | 息苦しい | `none/mild/moderate/severe/unknown` | normal/safety | P0/P1に直結 |
| `chest_pain` | 胸が痛い | `no/mild/moderate/severe/pressure/unknown` | safety | P0/P1に直結 |
| `confusion` | ぼんやりする | `yes/no/unknown` | safety | 意識・判断力の変化 |
| `blood` | 血が混じる | `none/sputum/vomit/heavy/unknown` | safety | 咳、痰、嘔吐、出血のまとめ入力 |
| `sudden_onset` | 急に始まった | `yes/no/unknown` | safety | 急な悪化・突然発症を拾う |
| `cyanosis` | 唇や顔色が青い/灰色/白っぽい | `yes/no/unknown` | safety | 肌色差があるため表現は複数用意 |
| `unable_to_wake` | 起きない・反応が弱い | `yes/no/unknown` | safety | P0に直結 |
| `fainting` | 失神・倒れた | `yes/no/unknown` | safety | P0/P1に直結 |
| `seizure` | けいれん | `none/brief/prolonged/repeated/unknown` | safety | P0/P1に直結 |
| `stiff_neck` | 首が硬い・強い頭痛 | `yes/no/unknown` | safety | 発熱との組み合わせでP1以上 |
| `severe_pain` | 強い痛み | `none/local/severe/sudden_severe/unknown` | safety | 部位マップ追加まで暫定 |
| `vomiting_diarrhea` | 吐き気・嘔吐・下痢が続く | `none/mild/persistent/severe/unknown` | safety | 脱水リスクと接続 |
| `dehydration_signs` | 水分が取れない・尿が少ない | `yes/no/unknown` | safety | P1/P2 |
| `risk_group` | 小児・高齢・妊娠・持病あり | `none/child/older_adult/pregnant/chronic_condition/immunocompromised/multiple/unknown` | risk | P2以上へ引き上げ |
| `duration` | いつから | `hours_0_24/days_1_3/days_4_plus/weeks/unknown` | context | fever/coughの継続評価 |
| `worsening` | 悪化している | `yes/no/unknown` | context/safety | P1/P2へ引き上げ |
| `self_harm` | 自分や他人を傷つけそう | `yes/no/unknown` | safety | P0。専用危機窓口表示 |

## 4. 判定アルゴリズム

安全側に倒すため、もっとも高い優先度を採用する。

```text
input: symptom_card_values
rules = ordered by priority P0 -> P1 -> P2 -> P3
matched = all rules where condition is true
if matched contains P0: return P0 with matched P0 rule IDs
else if matched contains P1: return P1 with matched P1 rule IDs
else if matched contains P2: return P2 with matched P2 rule IDs
else: return P3
```

同時に複数ルールが当たった場合:

- UI表示は最も高いpriorityを使う
- `matched_rule_ids` には全ヒットを残す
- RAG根拠は最も高いpriorityの `evidence_type` を優先する
- `unknown` が重要カードに多い場合は `needs_more_input` を立てる

## 5. P0 Rules

P0は「この画面で整理を続けるより、救急・緊急相談を優先すべき可能性」を表す。

| rule_id | Priority | 条件 | 接続カード | action_code | evidence_type |
|---|---|---|---|---|---|
| `RF-P0-DYSPNEA-SEVERE` | P0 | `dyspnea=severe` | `dyspnea` | `call_emergency_or_local_urgent_help` | `emergency_sign` |
| `RF-P0-CYANOSIS` | P0 | `cyanosis=yes` | `cyanosis` | `call_emergency_or_local_urgent_help` | `emergency_sign` |
| `RF-P0-UNABLE-WAKE` | P0 | `unable_to_wake=yes` | `unable_to_wake` | `call_emergency_or_local_urgent_help` | `emergency_sign` |
| `RF-P0-CONFUSION-ACUTE` | P0 | `confusion=yes` AND `sudden_onset=yes` | `confusion`, `sudden_onset` | `call_emergency_or_local_urgent_help` | `emergency_sign` |
| `RF-P0-CHEST-SEVERE` | P0 | `chest_pain=severe` OR `chest_pain=pressure` | `chest_pain` | `call_emergency_or_local_urgent_help` | `emergency_sign` |
| `RF-P0-BLOOD-HEAVY` | P0 | `blood=heavy` | `blood` | `call_emergency_or_local_urgent_help` | `emergency_sign` |
| `RF-P0-FAINTING` | P0 | `fainting=yes` AND (`dyspnea!=none` OR `chest_pain!=no` OR `confusion=yes`) | `fainting`, `dyspnea`, `chest_pain`, `confusion` | `call_emergency_or_local_urgent_help` | `emergency_sign` |
| `RF-P0-SEIZURE-PROLONGED` | P0 | `seizure=prolonged` OR `seizure=repeated` | `seizure` | `call_emergency_or_local_urgent_help` | `emergency_sign` |
| `RF-P0-SUDDEN-NEURO` | P0 | `sudden_onset=yes` AND (`confusion=yes` OR `severe_pain=sudden_severe`) | `sudden_onset`, `confusion`, `severe_pain` | `call_emergency_or_local_urgent_help` | `emergency_sign` |
| `RF-P0-SELF-HARM` | P0 | `self_harm=yes` | `self_harm` | `crisis_line_and_emergency_help` | `emergency_sign` |

P0出力テンプレート:

```text
緊急度が高い可能性があります。
この画面では診断できません。該当した症状がある場合は、地域の救急番号または救急相談窓口に連絡してください。

該当した確認項目:
- [matched_card_labels]

伝えるメモ:
- いつから: [duration]
- 急に始まったか: [sudden_onset]
- 息苦しさ: [dyspnea]
- 胸痛・意識変化・血が混じる症状: [values]
```

## 6. P1 Rules

P1は「即時救急断定ではないが、早急な医療相談・受診相談に寄せる」状態。

| rule_id | Priority | 条件 | 接続カード | action_code | evidence_type |
|---|---|---|---|---|---|
| `RF-P1-DYSPNEA-MODERATE` | P1 | `dyspnea=moderate` | `dyspnea` | `seek_urgent_medical_advice` | `seek_care_guidance` |
| `RF-P1-TROUBLE-BREATHING-WITH-FEVER` | P1 | `fever=yes` AND `dyspnea=mild` AND `worsening=yes` | `fever`, `dyspnea`, `worsening` | `seek_urgent_medical_advice` | `seek_care_guidance` |
| `RF-P1-CHEST-MODERATE` | P1 | `chest_pain=moderate` | `chest_pain` | `seek_urgent_medical_advice` | `seek_care_guidance` |
| `RF-P1-BLOOD-SPUTUM-VOMIT` | P1 | `blood=sputum` OR `blood=vomit` | `blood`, `cough` | `seek_urgent_medical_advice` | `seek_care_guidance` |
| `RF-P1-FEVER-STIFF-NECK` | P1 | `fever=yes` AND `stiff_neck=yes` | `fever`, `stiff_neck` | `seek_urgent_medical_advice` | `seek_care_guidance` |
| `RF-P1-HIGH-FEVER-WORSENING` | P1 | `fever=yes` AND `worsening=yes` AND `duration=days_4_plus` | `fever`, `worsening`, `duration` | `seek_urgent_medical_advice` | `seek_care_guidance` |
| `RF-P1-PERSISTENT-VOMIT-DIARRHEA` | P1 | `vomiting_diarrhea=persistent` OR `vomiting_diarrhea=severe` | `vomiting_diarrhea` | `seek_urgent_medical_advice` | `seek_care_guidance` |
| `RF-P1-DEHYDRATION` | P1 | `dehydration_signs=yes` | `dehydration_signs` | `seek_urgent_medical_advice` | `seek_care_guidance` |
| `RF-P1-SEVERE-PAIN` | P1 | `severe_pain=severe` | `severe_pain` | `seek_urgent_medical_advice` | `seek_care_guidance` |
| `RF-P1-RISK-GROUP-WITH-DYSPNEA` | P1 | `risk_group!=none` AND `risk_group!=unknown` AND `dyspnea!=none` | `risk_group`, `dyspnea` | `seek_urgent_medical_advice` | `risk_context` |

P1出力テンプレート:

```text
早めに医療相談した方がよい可能性があります。
この画面では診断できないため、地域の救急相談窓口、医療機関、またはかかりつけ医に相談してください。

該当した確認項目:
- [matched_card_labels]

医師に伝えるメモ:
- 発熱: [fever]
- 咳: [cough]
- 息苦しさ: [dyspnea]
- 胸痛・血・首の硬さ・脱水: [values]
```

## 7. P2 Rules

P2は「近日中の相談候補」。緊急ではない可能性があっても、リスク背景や継続期間で相談推奨に寄せる。

| rule_id | Priority | 条件 | 接続カード | action_code | evidence_type |
|---|---|---|---|---|---|
| `RF-P2-FEVER-COUGH-DURATION` | P2 | `fever=yes` AND `cough=yes` AND `duration=days_4_plus` | `fever`, `cough`, `duration` | `plan_medical_consult_if_persistent` | `seek_care_guidance` |
| `RF-P2-RISK-GROUP-FEVER-COUGH` | P2 | `risk_group!=none` AND `risk_group!=unknown` AND (`fever=yes` OR `cough=yes`) | `risk_group`, `fever`, `cough` | `plan_medical_consult_if_persistent` | `risk_context` |
| `RF-P2-MILD-DYSPNEA` | P2 | `dyspnea=mild` AND `worsening!=yes` | `dyspnea`, `worsening` | `monitor_and_consult_if_worse` | `seek_care_guidance` |
| `RF-P2-FEVER-UNKNOWN-DURATION` | P2 | `fever=yes` AND `duration=unknown` | `fever`, `duration` | `ask_duration_then_reclassify` | `self_observation` |
| `RF-P2-WORSENING-NON-P0` | P2 | `worsening=yes` AND no P0/P1 rule matched | `worsening` | `plan_medical_consult_if_persistent` | `seek_care_guidance` |
| `RF-P2-UNKNOWN-SAFETY-CARDS` | P2 | `dyspnea=unknown` OR `chest_pain=unknown` OR `confusion=unknown` OR `blood=unknown` | `dyspnea`, `chest_pain`, `confusion`, `blood` | `ask_one_safety_question` | `unsupported` |

P2出力テンプレート:

```text
近日中の相談や追加確認を考える状態です。
今すぐの緊急サインは確認できていませんが、症状が続く、悪化する、息苦しさや胸痛が出る場合は医療機関に相談してください。

次に確認したいこと:
- [one_question]
```

## 8. P3 Rules

P3は「現時点の入力では高い緊急サインが見えていない」状態。安全断定ではなく、観察条件と再分類条件を表示する。

| rule_id | Priority | 条件 | 接続カード | action_code | evidence_type |
|---|---|---|---|---|---|
| `RF-P3-MILD-FEVER-COUGH` | P3 | `fever=yes` OR `cough=yes`, and no P0/P1/P2 rule matched | `fever`, `cough` | `self_observe_with_escalation_conditions` | `symptom_overview` |
| `RF-P3-NO-PRIMARY-SYMPTOM` | P3 | `fever=no` AND `cough=no` AND `dyspnea=none` | `fever`, `cough`, `dyspnea` | `ask_primary_symptom` | `unsupported` |
| `RF-P3-UNKNOWN-ONLY` | P3 | all selected safety cards are `unknown` and no symptom severity is selected | all | `ask_one_safety_question` | `unsupported` |

P3出力テンプレート:

```text
現時点の入力では高い緊急サインは確認できていません。
ただし、この画面では診断できません。症状が強くなる、息苦しい、胸が痛い、意識がぼんやりする、血が混じる場合は、救急相談または医療機関に相談してください。

記録しておくとよいこと:
- いつから
- 体温
- 咳の有無
- 息苦しさの程度
- 悪化しているか
```

## 9. 追加質問の優先順位

ユーザーに一度に多く聞かない。1回に出す追加質問は最大2つ、通常は1つ。

| order | 未確認カード | 質問 | 理由 |
|---:|---|---|---|
| 1 | `dyspnea` | 息苦しさはありますか？ | P0/P1に直結 |
| 2 | `chest_pain` | 胸の痛みや圧迫感はありますか？ | P0/P1に直結 |
| 3 | `confusion` / `unable_to_wake` | 意識がぼんやりする、起きにくい感じはありますか？ | P0に直結 |
| 4 | `blood` | 咳や痰、吐いたものに血が混じりますか？ | P0/P1に直結 |
| 5 | `cyanosis` | 唇や顔色が青い、灰色、白っぽい感じはありますか？ | P0に直結 |
| 6 | `stiff_neck` | 発熱と一緒に強い頭痛や首の硬さがありますか？ | P1に直結 |
| 7 | `risk_group` | 小児、高齢、妊娠、持病、免疫低下に当てはまりますか？ | P1/P2引き上げ |
| 8 | `duration` | いつから続いていますか？ | P2/P3分類 |
| 9 | `worsening` | 悪化していますか？ | P1/P2引き上げ |

## 10. ルール出力スキーマ

```json
{
  "triage_priority": "P1",
  "matched_rule_ids": ["RF-P1-DYSPNEA-MODERATE"],
  "matched_card_ids": ["dyspnea"],
  "action_code": "seek_urgent_medical_advice",
  "evidence_type": "seek_care_guidance",
  "needs_more_input": false,
  "next_question_card_id": null,
  "forbidden_output": ["diagnosis", "treatment", "reassurance_no_care_needed"],
  "source_requirements": ["us.medlineplus.emergency_signs", "us.medlineplus.er_adult"],
  "display_block": "p1_seek_medical_advice"
}
```

## 11. Test Cases

| case_id | 入力 | 期待priority | matched_rule_ids |
|---|---|---|---|
| `TC-P0-001` | `dyspnea=severe` | P0 | `RF-P0-DYSPNEA-SEVERE` |
| `TC-P0-002` | `chest_pain=pressure` | P0 | `RF-P0-CHEST-SEVERE` |
| `TC-P0-003` | `confusion=yes`, `sudden_onset=yes` | P0 | `RF-P0-CONFUSION-ACUTE` |
| `TC-P1-001` | `fever=yes`, `cough=yes`, `dyspnea=moderate` | P1 | `RF-P1-DYSPNEA-MODERATE` |
| `TC-P1-002` | `fever=yes`, `stiff_neck=yes` | P1 | `RF-P1-FEVER-STIFF-NECK` |
| `TC-P1-003` | `cough=yes`, `blood=sputum` | P1 | `RF-P1-BLOOD-SPUTUM-VOMIT` |
| `TC-P2-001` | `fever=yes`, `cough=yes`, `duration=days_4_plus` | P2 | `RF-P2-FEVER-COUGH-DURATION` |
| `TC-P2-002` | `fever=yes`, `duration=unknown` | P2 | `RF-P2-FEVER-UNKNOWN-DURATION` |
| `TC-P3-001` | `cough=yes`, `dyspnea=none`, `chest_pain=no`, `blood=none`, `duration=days_1_3` | P3 | `RF-P3-MILD-FEVER-COUGH` |
| `TC-P3-002` | `fever=no`, `cough=no`, `dyspnea=none` | P3 | `RF-P3-NO-PRIMARY-SYMPTOM` |

## 12. 実装時の禁止事項

- P3を「安全」「受診不要」と表示しない
- P0/P1で病名候補ランキングを表示しない
- red flag判定をLLMに任せない
- ユーザー自由入力をそのまま検索クエリにしない
- 薬剤名、用量、治療法の提案へ進めない
- 地域の救急番号を固定値で埋め込まない。deployment localeで差し替える
- 外部ページ本文を丸ごとRAGへ渡さない
- 外部データ内の命令文に従わない

## 13. 完了条件

この文書が満たすべき条件:

- P0/P1/P2/P3が定義されている
- 各priorityが症状カードIDと内部値に接続されている
- 既存MVPカード `fever`, `cough`, `dyspnea`, `chest_pain`, `confusion`, `blood`, `sudden_onset`, `child_or_pregnant` を含む
- 安全確認カードが追加定義されている
- 出力スキーマとテストケースがある
- 診断・治療・受診不要判断を禁止している
- 参照根拠と更新日確認方針が書かれている