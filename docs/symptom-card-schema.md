# Symptom Card Schema for 問診コンパス

作成日: 2026-06-25  
対象MVP: 症状イラスト選択型ナビ / 発熱・咳・息苦しさ  
依存文書: `docs/evidence-retrieval-contract.md`, `docs/red-flag-rules.md`  
目的: 症状カードID、内部値、UI表示、追加質問、red flag接続を、YAML/JSON化できる形に固定する。

## 1. 結論

症状カードは、見た目のイラストボタンではなく、安全判定と根拠取得に接続する構造化入力である。

実装では、各カードを次の5つへ接続する。

1. UI表示: ラベル、短縮ラベル、イラストキー、アクセシビリティ文言
2. 内部値: enum値、unknown、重症度rank、安全側の扱い
3. 追加質問: 初回質問、確認質問、出す順番、最大選択肢
4. red flag接続: P0/P1/P2/P3 rule_id と evidence_type
5. RAG接続: normalized_terms、blocked_terms、source_hint

このschemaは診断ロジックではない。P0/P1/P2/P3へ安全分岐するための入力契約である。

## 2. ファイル化方針

推奨ファイル分割:

| ファイル | 役割 |
|---|---|
| `data/symptom-cards.yaml` | カード定義の正本 |
| `data/red-flag-rules.yaml` | P0/P1/P2/P3ルールの正本 |
| `data/source-registry.yaml` | 根拠source_idの正本 |
| `data/ui-copy.yaml` | UI文言の差し替え用 |
| `tests/fixtures/symptom-card-cases.jsonl` | 判定テストケース |

このMarkdownは上記ファイルを作る前の契約書とする。実装時は、この文書のYAMLブロックをそのまま初期データに変換してよい。

## 3. Card Object Schema

```yaml
schema_version: 0.1.0
card:
  card_id: string                 # stable snake_case id. never reuse with changed meaning
  status: active                  # active | draft | deprecated
  category: primary               # primary | safety | context | risk
  ui:
    label_ja: string              # card face label
    short_label_ja: string        # chip label
    group: respiratory            # respiratory | emergency | context | risk | mental_health
    sort_order: integer
    visible_default: boolean      # initial gridに出すか
    illustration_key: string      # asset lookup key, not a filename contract
    icon_hint: string             # temporary design hint
    accessibility_label_ja: string
    helper_text_ja: string
  input:
    value_type: enum              # enum | boolean | multi_enum
    default_value: unknown
    unknown_allowed: boolean
    values:
      - value: string
        label_ja: string
        severity_rank: integer    # 0 none, 1 mild/context, 2 consult, 3 urgent, 4 emergency
        counts_as_present: boolean
        is_unknown: boolean
  question:
    ask_priority: integer         # lower is earlier
    initial_prompt_ja: string
    followup_prompt_ja: string
    answer_style: segmented       # segmented | card_grid | yes_no_unknown | severity_scale
    max_visible_options: integer
    ask_when:
      any_selected: []            # card_ids that trigger this question
      missing_if: []              # values/conditions that trigger when unknown
    skip_allowed: boolean
  normalization:
    normalized_terms_ja: []
    normalized_terms_en: []
    blocked_terms: []             # terms never used for retrieval from this card
  red_flag:
    directly_sets_priority: null  # null | P0 | P1 | P2 | P3
    connected_rule_ids: []
    safety_question: boolean
  retrieval:
    evidence_types: []            # emergency_sign, seek_care_guidance, symptom_overview, risk_context, self_observation, unsupported
    source_hints: []              # source_ids or source lanes
  privacy:
    stores_raw_text: false
    pii_risk: low                 # low | medium | high
```

## 4. Card Registry YAML

```yaml
schema_version: 0.1.0
locale: ja-JP
product: monshin-compass
scope: fever_cough_dyspnea_mvp
cards:
  - card_id: fever
    status: active
    category: primary
    ui:
      label_ja: 熱っぽい
      short_label_ja: 発熱
      group: respiratory
      sort_order: 10
      visible_default: true
      illustration_key: thermometer_forehead_red
      icon_hint: 体温計と赤い額
      accessibility_label_ja: 熱っぽさ、発熱の症状カード
      helper_text_ja: 体温が分からなくても選べます。
    input:
      value_type: enum
      default_value: unknown
      unknown_allowed: true
      values:
        - {value: "yes", label_ja: "ある", severity_rank: 1, counts_as_present: true, is_unknown: false}
        - {value: "no", label_ja: "ない", severity_rank: 0, counts_as_present: false, is_unknown: false}
        - {value: "unknown", label_ja: "わからない", severity_rank: 1, counts_as_present: false, is_unknown: true}
    question:
      ask_priority: 20
      initial_prompt_ja: 熱っぽさや発熱はありますか？
      followup_prompt_ja: 体温や熱っぽさはありますか？
      answer_style: yes_no_unknown
      max_visible_options: 3
      ask_when:
        any_selected: []
        missing_if: []
      skip_allowed: true
    normalization:
      normalized_terms_ja: [発熱, 熱っぽい, 体温]
      normalized_terms_en: [fever, elevated temperature]
      blocked_terms: [解熱剤の用量, 抗生物質]
    red_flag:
      directly_sets_priority: null
      connected_rule_ids: [RF-P1-TROUBLE-BREATHING-WITH-FEVER, RF-P1-FEVER-STIFF-NECK, RF-P1-HIGH-FEVER-WORSENING, RF-P2-FEVER-COUGH-DURATION, RF-P2-RISK-GROUP-FEVER-COUGH, RF-P2-FEVER-UNKNOWN-DURATION]
      safety_question: false
    retrieval:
      evidence_types: [seek_care_guidance, symptom_overview, self_observation]
      source_hints: [us.medlineplus, us.cdc, jp.mhlw]
    privacy: {stores_raw_text: false, pii_risk: low}

  - card_id: cough
    status: active
    category: primary
    ui:
      label_ja: 咳が出る
      short_label_ja: 咳
      group: respiratory
      sort_order: 20
      visible_default: true
      illustration_key: cough_mouth_motion
      icon_hint: 口元と咳の動き
      accessibility_label_ja: 咳の症状カード
      helper_text_ja: 乾いた咳、痰がからむ咳のどちらでも選べます。
    input:
      value_type: enum
      default_value: unknown
      unknown_allowed: true
      values:
        - {value: "yes", label_ja: "ある", severity_rank: 1, counts_as_present: true, is_unknown: false}
        - {value: "no", label_ja: "ない", severity_rank: 0, counts_as_present: false, is_unknown: false}
        - {value: "unknown", label_ja: "わからない", severity_rank: 1, counts_as_present: false, is_unknown: true}
    question:
      ask_priority: 30
      initial_prompt_ja: 咳はありますか？
      followup_prompt_ja: 咳や痰はありますか？
      answer_style: yes_no_unknown
      max_visible_options: 3
      ask_when: {any_selected: [], missing_if: []}
      skip_allowed: true
    normalization:
      normalized_terms_ja: [咳, せき, 痰]
      normalized_terms_en: [cough, sputum]
      blocked_terms: [咳止めの用量, 抗生物質]
    red_flag:
      directly_sets_priority: null
      connected_rule_ids: [RF-P1-BLOOD-SPUTUM-VOMIT, RF-P2-FEVER-COUGH-DURATION, RF-P2-RISK-GROUP-FEVER-COUGH, RF-P3-MILD-FEVER-COUGH]
      safety_question: false
    retrieval:
      evidence_types: [seek_care_guidance, symptom_overview, self_observation]
      source_hints: [us.medlineplus, us.cdc, jp.mhlw]
    privacy: {stores_raw_text: false, pii_risk: low}

  - card_id: dyspnea
    status: active
    category: safety
    ui:
      label_ja: 息苦しい
      short_label_ja: 息苦しさ
      group: emergency
      sort_order: 30
      visible_default: true
      illustration_key: chest_breathing_difficulty
      icon_hint: 胸を押さえる人と呼吸線
      accessibility_label_ja: 息苦しさ、呼吸のつらさの症状カード
      helper_text_ja: 少しでも息がしづらい場合は選んでください。
    input:
      value_type: enum
      default_value: unknown
      unknown_allowed: true
      values:
        - {value: "none", label_ja: "ない", severity_rank: 0, counts_as_present: false, is_unknown: false}
        - {value: "mild", label_ja: "少しある", severity_rank: 2, counts_as_present: true, is_unknown: false}
        - {value: "moderate", label_ja: "はっきりある", severity_rank: 3, counts_as_present: true, is_unknown: false}
        - {value: "severe", label_ja: "かなり強い", severity_rank: 4, counts_as_present: true, is_unknown: false}
        - {value: "unknown", label_ja: "わからない", severity_rank: 2, counts_as_present: false, is_unknown: true}
    question:
      ask_priority: 1
      initial_prompt_ja: 息苦しさはありますか？
      followup_prompt_ja: 息苦しさの強さを選んでください。
      answer_style: severity_scale
      max_visible_options: 5
      ask_when:
        any_selected: [fever, cough]
        missing_if: [dyspnea=unknown]
      skip_allowed: false
    normalization:
      normalized_terms_ja: [息苦しさ, 呼吸困難, 呼吸がつらい]
      normalized_terms_en: [shortness of breath, trouble breathing, difficulty breathing]
      blocked_terms: [酸素投与, 吸入薬の用量]
    red_flag:
      directly_sets_priority: null
      connected_rule_ids: [RF-P0-DYSPNEA-SEVERE, RF-P1-DYSPNEA-MODERATE, RF-P1-TROUBLE-BREATHING-WITH-FEVER, RF-P1-RISK-GROUP-WITH-DYSPNEA, RF-P2-MILD-DYSPNEA, RF-P2-UNKNOWN-SAFETY-CARDS]
      safety_question: true
    retrieval:
      evidence_types: [emergency_sign, seek_care_guidance]
      source_hints: [us.medlineplus.emergency_signs, us.medlineplus.er_adult, us.cdc.covid_symptoms]
    privacy: {stores_raw_text: false, pii_risk: low}

  - card_id: chest_pain
    status: active
    category: safety
    ui:
      label_ja: 胸が痛い
      short_label_ja: 胸痛
      group: emergency
      sort_order: 40
      visible_default: false
      illustration_key: chest_pain_mark
      icon_hint: 胸部と痛みマーク
      accessibility_label_ja: 胸の痛みや圧迫感の確認カード
      helper_text_ja: 痛み、圧迫感、締めつけ感を含みます。
    input:
      value_type: enum
      default_value: unknown
      unknown_allowed: true
      values:
        - {value: "no", label_ja: "ない", severity_rank: 0, counts_as_present: false, is_unknown: false}
        - {value: "mild", label_ja: "少し痛い", severity_rank: 2, counts_as_present: true, is_unknown: false}
        - {value: "moderate", label_ja: "はっきり痛い", severity_rank: 3, counts_as_present: true, is_unknown: false}
        - {value: "severe", label_ja: "強い痛み", severity_rank: 4, counts_as_present: true, is_unknown: false}
        - {value: "pressure", label_ja: "圧迫感・締めつけ", severity_rank: 4, counts_as_present: true, is_unknown: false}
        - {value: "unknown", label_ja: "わからない", severity_rank: 2, counts_as_present: false, is_unknown: true}
    question:
      ask_priority: 2
      initial_prompt_ja: 胸の痛みや圧迫感はありますか？
      followup_prompt_ja: 胸の痛みや圧迫感の強さを選んでください。
      answer_style: severity_scale
      max_visible_options: 6
      ask_when: {any_selected: [dyspnea, cough], missing_if: [chest_pain=unknown]}
      skip_allowed: false
    normalization:
      normalized_terms_ja: [胸痛, 胸の痛み, 胸の圧迫感]
      normalized_terms_en: [chest pain, chest discomfort, chest pressure]
      blocked_terms: [心筋梗塞診断, ニトログリセリン用量]
    red_flag:
      directly_sets_priority: null
      connected_rule_ids: [RF-P0-CHEST-SEVERE, RF-P0-FAINTING, RF-P1-CHEST-MODERATE, RF-P2-UNKNOWN-SAFETY-CARDS]
      safety_question: true
    retrieval:
      evidence_types: [emergency_sign, seek_care_guidance]
      source_hints: [us.medlineplus.emergency_signs, us.medlineplus.er_adult]
    privacy: {stores_raw_text: false, pii_risk: low}

  - card_id: confusion
    status: active
    category: safety
    ui:
      label_ja: ぼんやりする
      short_label_ja: 意識変化
      group: emergency
      sort_order: 50
      visible_default: false
      illustration_key: head_confusion_mark
      icon_hint: 頭部と混乱マーク
      accessibility_label_ja: 意識がぼんやりする、普段と様子が違う確認カード
      helper_text_ja: 受け答えが変、起きにくい、普段と違う様子を含みます。
    input:
      value_type: enum
      default_value: unknown
      unknown_allowed: true
      values:
        - {value: "yes", label_ja: "ある", severity_rank: 4, counts_as_present: true, is_unknown: false}
        - {value: "no", label_ja: "ない", severity_rank: 0, counts_as_present: false, is_unknown: false}
        - {value: "unknown", label_ja: "わからない", severity_rank: 2, counts_as_present: false, is_unknown: true}
    question:
      ask_priority: 3
      initial_prompt_ja: 意識がぼんやりする、受け答えが普段と違う感じはありますか？
      followup_prompt_ja: 急にぼんやりしたり、普段と様子が違ったりしますか？
      answer_style: yes_no_unknown
      max_visible_options: 3
      ask_when: {any_selected: [fever, dyspnea], missing_if: [confusion=unknown]}
      skip_allowed: false
    normalization:
      normalized_terms_ja: [意識変化, 混乱, ぼんやりする]
      normalized_terms_en: [confusion, change in mental status, difficulty arousing]
      blocked_terms: [認知症診断]
    red_flag:
      directly_sets_priority: null
      connected_rule_ids: [RF-P0-CONFUSION-ACUTE, RF-P0-FAINTING, RF-P0-SUDDEN-NEURO, RF-P2-UNKNOWN-SAFETY-CARDS]
      safety_question: true
    retrieval:
      evidence_types: [emergency_sign]
      source_hints: [us.medlineplus.emergency_signs]
    privacy: {stores_raw_text: false, pii_risk: low}

  - card_id: blood
    status: active
    category: safety
    ui:
      label_ja: 血が混じる
      short_label_ja: 血
      group: emergency
      sort_order: 60
      visible_default: false
      illustration_key: red_drop_cough_vomit
      icon_hint: 赤いしずくと咳・嘔吐の記号
      accessibility_label_ja: 咳、痰、吐いたものに血が混じる確認カード
      helper_text_ja: 咳や痰、吐いたもの、出血が止まらない場合を含みます。
    input:
      value_type: enum
      default_value: unknown
      unknown_allowed: true
      values:
        - {value: "none", label_ja: "ない", severity_rank: 0, counts_as_present: false, is_unknown: false}
        - {value: "sputum", label_ja: "痰や咳に少し混じる", severity_rank: 3, counts_as_present: true, is_unknown: false}
        - {value: "vomit", label_ja: "吐いたものに混じる", severity_rank: 3, counts_as_present: true, is_unknown: false}
        - {value: "heavy", label_ja: "多い・止まらない", severity_rank: 4, counts_as_present: true, is_unknown: false}
        - {value: "unknown", label_ja: "わからない", severity_rank: 2, counts_as_present: false, is_unknown: true}
    question:
      ask_priority: 4
      initial_prompt_ja: 咳や痰、吐いたものに血が混じりますか？
      followup_prompt_ja: 血が混じる場合、どの程度ですか？
      answer_style: segmented
      max_visible_options: 5
      ask_when: {any_selected: [cough, vomiting_diarrhea], missing_if: [blood=unknown]}
      skip_allowed: false
    normalization:
      normalized_terms_ja: [血痰, 吐血, 出血]
      normalized_terms_en: [coughing blood, vomiting blood, bleeding]
      blocked_terms: [止血手技, 薬の用量]
    red_flag:
      directly_sets_priority: null
      connected_rule_ids: [RF-P0-BLOOD-HEAVY, RF-P1-BLOOD-SPUTUM-VOMIT, RF-P2-UNKNOWN-SAFETY-CARDS]
      safety_question: true
    retrieval:
      evidence_types: [emergency_sign, seek_care_guidance]
      source_hints: [us.medlineplus.emergency_signs, us.medlineplus.er_adult]
    privacy: {stores_raw_text: false, pii_risk: low}

  - card_id: sudden_onset
    status: active
    category: safety
    ui:
      label_ja: 急に始まった
      short_label_ja: 急な発症
      group: emergency
      sort_order: 70
      visible_default: false
      illustration_key: clock_lightning
      icon_hint: 時計と稲妻
      accessibility_label_ja: 症状が急に始まったかの確認カード
      helper_text_ja: いつもと違う急な変化を拾うための確認です。
    input:
      value_type: enum
      default_value: unknown
      unknown_allowed: true
      values:
        - {value: "yes", label_ja: "急に始まった", severity_rank: 3, counts_as_present: true, is_unknown: false}
        - {value: "no", label_ja: "徐々に", severity_rank: 0, counts_as_present: false, is_unknown: false}
        - {value: "unknown", label_ja: "わからない", severity_rank: 1, counts_as_present: false, is_unknown: true}
    question:
      ask_priority: 7
      initial_prompt_ja: 症状は急に始まりましたか？
      followup_prompt_ja: 急に悪くなった感じはありますか？
      answer_style: yes_no_unknown
      max_visible_options: 3
      ask_when: {any_selected: [dyspnea, chest_pain, confusion, severe_pain], missing_if: []}
      skip_allowed: true
    normalization:
      normalized_terms_ja: [急な発症, 急な悪化, 突然]
      normalized_terms_en: [sudden onset, sudden worsening]
      blocked_terms: [病名確定]
    red_flag:
      directly_sets_priority: null
      connected_rule_ids: [RF-P0-CONFUSION-ACUTE, RF-P0-SUDDEN-NEURO]
      safety_question: true
    retrieval:
      evidence_types: [emergency_sign, seek_care_guidance]
      source_hints: [us.medlineplus.emergency_signs]
    privacy: {stores_raw_text: false, pii_risk: low}

  - card_id: cyanosis
    status: active
    category: safety
    ui:
      label_ja: 顔色や唇が変
      short_label_ja: 顔色・唇
      group: emergency
      sort_order: 80
      visible_default: false
      illustration_key: lips_color_change
      icon_hint: 唇と色変化のスウォッチ
      accessibility_label_ja: 唇や顔色が青い、灰色、白っぽい確認カード
      helper_text_ja: 肌色差があるため、青い・灰色・白っぽいなど幅を持たせます。
    input:
      value_type: enum
      default_value: unknown
      unknown_allowed: true
      values:
        - {value: "yes", label_ja: "ある", severity_rank: 4, counts_as_present: true, is_unknown: false}
        - {value: "no", label_ja: "ない", severity_rank: 0, counts_as_present: false, is_unknown: false}
        - {value: "unknown", label_ja: "わからない", severity_rank: 2, counts_as_present: false, is_unknown: true}
    question:
      ask_priority: 5
      initial_prompt_ja: 唇や顔色が青い、灰色、白っぽい感じはありますか？
      followup_prompt_ja: 顔色や唇の色が普段と大きく違いますか？
      answer_style: yes_no_unknown
      max_visible_options: 3
      ask_when: {any_selected: [dyspnea], missing_if: []}
      skip_allowed: false
    normalization:
      normalized_terms_ja: [チアノーゼ, 顔色が悪い, 唇が青い]
      normalized_terms_en: [cyanosis, bluish lips, gray skin color]
      blocked_terms: [皮膚疾患診断]
    red_flag:
      directly_sets_priority: P0
      connected_rule_ids: [RF-P0-CYANOSIS]
      safety_question: true
    retrieval:
      evidence_types: [emergency_sign]
      source_hints: [us.medlineplus.emergency_signs]
    privacy: {stores_raw_text: false, pii_risk: low}

  - card_id: risk_group
    status: active
    category: risk
    ui:
      label_ja: 小児・高齢・妊娠・持病あり
      short_label_ja: リスク背景
      group: risk
      sort_order: 150
      visible_default: false
      illustration_key: family_pregnancy_chronic_condition
      icon_hint: 家族、妊娠、医療カードの組み合わせ
      accessibility_label_ja: 小児、高齢、妊娠、持病、免疫低下などの背景確認カード
      helper_text_ja: 当てはまる場合、受診相談の優先度を上げます。
    input:
      value_type: multi_enum
      default_value: unknown
      unknown_allowed: true
      values:
        - {value: "none", label_ja: "当てはまらない", severity_rank: 0, counts_as_present: false, is_unknown: false}
        - {value: "child", label_ja: "小児", severity_rank: 2, counts_as_present: true, is_unknown: false}
        - {value: "older_adult", label_ja: "高齢", severity_rank: 2, counts_as_present: true, is_unknown: false}
        - {value: "pregnant", label_ja: "妊娠中・可能性あり", severity_rank: 2, counts_as_present: true, is_unknown: false}
        - {value: "chronic_condition", label_ja: "持病あり", severity_rank: 2, counts_as_present: true, is_unknown: false}
        - {value: "immunocompromised", label_ja: "免疫低下", severity_rank: 2, counts_as_present: true, is_unknown: false}
        - {value: "multiple", label_ja: "複数あり", severity_rank: 3, counts_as_present: true, is_unknown: false}
        - {value: "unknown", label_ja: "わからない", severity_rank: 1, counts_as_present: false, is_unknown: true}
    question:
      ask_priority: 8
      initial_prompt_ja: 小児、高齢、妊娠、持病、免疫低下に当てはまりますか？
      followup_prompt_ja: 注意が必要な背景に当てはまるものはありますか？
      answer_style: card_grid
      max_visible_options: 8
      ask_when: {any_selected: [fever, cough, dyspnea], missing_if: []}
      skip_allowed: true
    normalization:
      normalized_terms_ja: [小児, 高齢者, 妊娠, 基礎疾患, 免疫低下]
      normalized_terms_en: [child, older adult, pregnant, chronic condition, immunocompromised]
      blocked_terms: [個別診断, 薬の用量]
    red_flag:
      directly_sets_priority: null
      connected_rule_ids: [RF-P1-RISK-GROUP-WITH-DYSPNEA, RF-P2-RISK-GROUP-FEVER-COUGH]
      safety_question: true
    retrieval:
      evidence_types: [risk_context, seek_care_guidance]
      source_hints: [us.medlineplus, us.cdc, jp.mhlw]
    privacy: {stores_raw_text: false, pii_risk: medium}
```

## 5. Compact Card List

実装時はまず次の19カードを正本とする。

| card_id | category | visible_default | ask_priority | primary red flag connection |
|---|---|---:|---:|---|
| `fever` | primary | true | 20 | P1/P2 context |
| `cough` | primary | true | 30 | P1/P2 context |
| `dyspnea` | safety | true | 1 | P0/P1/P2 |
| `chest_pain` | safety | false | 2 | P0/P1 |
| `confusion` | safety | false | 3 | P0 |
| `blood` | safety | false | 4 | P0/P1 |
| `cyanosis` | safety | false | 5 | P0 |
| `unable_to_wake` | safety | false | 3 | P0 |
| `fainting` | safety | false | 6 | P0 |
| `seizure` | safety | false | 6 | P0 |
| `sudden_onset` | safety | false | 7 | P0 modifier |
| `stiff_neck` | safety | false | 6 | P1 with fever |
| `severe_pain` | safety | false | 6 | P0/P1 |
| `vomiting_diarrhea` | safety | false | 9 | P1 |
| `dehydration_signs` | safety | false | 9 | P1 |
| `risk_group` | risk | false | 8 | P1/P2 modifier |
| `duration` | context | false | 10 | P2 modifier |
| `worsening` | context | false | 9 | P1/P2 modifier |
| `self_harm` | safety | false | 0 | P0 |

未実装カードの扱い:

- 初期UIに出さないカードでも、schemaには含める
- safetyカードはred flag判定のために優先質問として出せる
- `self_harm` は呼吸器MVPの主導線には出さないが、自由入力や緊急ボタンから出た場合はP0へ直行する

## 6. Question Flow Contract

```yaml
question_flow:
  max_questions_per_step: 2
  default_questions_per_step: 1
  first_screen_cards: [fever, cough, dyspnea]
  always_available_button: emergency_symptoms
  next_question_priority:
    - dyspnea
    - chest_pain
    - confusion
    - blood
    - cyanosis
    - stiff_neck
    - risk_group
    - duration
    - worsening
  stop_conditions:
    - matched_priority: P0
      action: show_p0_output
    - matched_priority: P1
      action: show_p1_output_after_minimum_summary
    - answered_cards_count_gte: 6
      action: summarize_without_more_questions
    - user_selects_unknown_repeatedly: true
      action: show_unanswerable_template
```

## 7. Normalized Selection JSON

アプリ内部で保持するカード選択は、次の形に固定する。

```json
{
  "schema_version": "0.1.0",
  "session_id": "local-or-anonymous-id",
  "locale": "ja-JP",
  "selected_cards": [
    {
      "card_id": "fever",
      "value": "yes",
      "source": "user_selected",
      "asked_at_step": 1,
      "confidence": "explicit"
    },
    {
      "card_id": "dyspnea",
      "value": "moderate",
      "source": "user_selected",
      "asked_at_step": 2,
      "confidence": "explicit"
    }
  ],
  "triage_result": {
    "triage_priority": "P1",
    "matched_rule_ids": ["RF-P1-DYSPNEA-MODERATE"],
    "matched_card_ids": ["dyspnea"],
    "next_question_card_id": null,
    "forbidden_output": ["diagnosis", "treatment", "reassurance_no_care_needed"]
  },
  "retrieval_plan": {
    "evidence_types": ["seek_care_guidance", "emergency_sign"],
    "source_hints": ["us.medlineplus.emergency_signs", "us.medlineplus.er_adult"],
    "blocked_terms": ["diagnosis", "treatment", "dosage"]
  }
}
```

## 8. Validation Rules

カードschemaの機械検証では、最低限これをチェックする。

```yaml
validation_rules:
  required_fields:
    - card_id
    - category
    - ui.label_ja
    - ui.illustration_key
    - input.default_value
    - input.values
    - question.ask_priority
    - red_flag.connected_rule_ids
    - retrieval.evidence_types
  invariants:
    - card_id must be snake_case
    - every default_value must exist in input.values
    - unknown_allowed true requires a value named unknown
    - safety cards must have safety_question true
    - cards connected to P0/P1 must include emergency_sign or seek_care_guidance in retrieval.evidence_types
    - blocked_terms must not be empty for primary or safety cards
    - visible_default true cards must have sort_order <= 30
    - no card may directly output diagnosis or treatment
  cross_file_checks:
    - every connected_rule_id must exist in docs/red-flag-rules.md or data/red-flag-rules.yaml
    - every source_hint must exist in docs/evidence-retrieval-contract.md or data/source-registry.yaml
    - every evidence_type must be one of the contract values
```

## 9. Test Fixtures

```jsonl
{"case_id":"SCHEMA-TC-001","selected_cards":[{"card_id":"dyspnea","value":"severe"}],"expected_priority":"P0","expected_next":null,"expected_rules":["RF-P0-DYSPNEA-SEVERE"]}
{"case_id":"SCHEMA-TC-002","selected_cards":[{"card_id":"fever","value":"yes"},{"card_id":"cough","value":"yes"},{"card_id":"dyspnea","value":"moderate"}],"expected_priority":"P1","expected_next":null,"expected_rules":["RF-P1-DYSPNEA-MODERATE"]}
{"case_id":"SCHEMA-TC-003","selected_cards":[{"card_id":"fever","value":"yes"},{"card_id":"cough","value":"yes"},{"card_id":"duration","value":"days_4_plus"}],"expected_priority":"P2","expected_next":"dyspnea","expected_rules":["RF-P2-FEVER-COUGH-DURATION"]}
{"case_id":"SCHEMA-TC-004","selected_cards":[{"card_id":"cough","value":"yes"},{"card_id":"dyspnea","value":"none"},{"card_id":"chest_pain","value":"no"},{"card_id":"blood","value":"none"},{"card_id":"duration","value":"days_1_3"}],"expected_priority":"P3","expected_next":null,"expected_rules":["RF-P3-MILD-FEVER-COUGH"]}
{"case_id":"SCHEMA-TC-005","selected_cards":[{"card_id":"fever","value":"yes"},{"card_id":"dyspnea","value":"unknown"}],"expected_priority":"P2","expected_next":"dyspnea","expected_rules":["RF-P2-UNKNOWN-SAFETY-CARDS"]}
```

## 10. UI Rules

- 初回グリッドは `visible_default=true` のカードだけ出す
- safetyカードは選択状況に応じて追加質問として出す
- `unknown` は常に選択肢として表示する
- P0/P1ヒット後は通常の質問を止める
- P0/P1ヒット後に病名候補カードや治療カードを出さない
- カードの色だけで重症度を伝えない。ラベルとアクセシビリティ文言を併用する
- イラストは症状の象徴に留め、恐怖を煽る表現にしない
- enabledなボタンは必ず状態更新、次質問、結果表示のいずれかを起こす

## 11. Forbidden Schema Drift

次の変更は禁止、または別ADRを必要とする。

- 既存 `card_id` の意味を変える
- `unknown` を削除する
- `dyspnea=severe` をP0以外に下げる
- `chest_pain=pressure` をP0以外に下げる
- P3を「安全」や「受診不要」に変換する
- 薬剤、用量、治療法カードを初期MVPへ追加する
- 外部LLMや外部画像生成APIへカード入力を自動送信する
- RAG本文から直接カード値を生成して、ユーザー確認なしに確定する

## 12. Implementation Ticket

```text
Ticket: Materialize symptom card registry
Objective: docs/symptom-card-schema.md のYAML定義から data/symptom-cards.yaml と tests/fixtures/symptom-card-cases.jsonl を作る。
Scope: 発熱・咳・息苦しさMVPのカード定義のみ。
Forbidden: 診断ロジック、治療推奨、外部API実行、外部repo導入、患者個人情報保存。
Verification:
- YAML parse succeeds
- every card has unknown if unknown_allowed=true
- every connected_rule_id resolves
- P0/P1/P2/P3 fixture expectations pass in a pure local rule evaluator
Done:
- schema file, YAML registry, fixture JSONL, and validation command are documented
```

## 13. 完了条件

この文書が満たすべき条件:

- カードIDが固定されている
- 内部値と `unknown` の扱いが固定されている
- UI表示とイラストキーが固定されている
- 追加質問の優先順位が固定されている
- red flag rule_id との接続が明記されている
- RAGに渡す evidence_type と source_hint が接続されている
- YAML/JSON化できる例がある
- テストフィクスチャがある
- 診断・治療・受診不要判断への逸脱が禁止されている