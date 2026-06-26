# JP Emergency Routing Resolver

作成日: 2026-06-25  
対象: 問診コンパス 日本向け救急相談導線

## 1. 目的

`#7119` は全国一律ではないため、問診コンパスでは deployment locale を見ずに `#7119` を表示しない。

resolverは次を機械的に決める。

- P0では `#7119` より `119` を優先する
- deployment locale が `#7119` 実施確認済みなら `#7119` を表示する
- deployment locale が未確認なら `#7119` を直接表示せず、消防庁の実施エリアsource確認へ落とす
- 子どもでは `#8000` をsecondary routeとして追加できる
- 自傷・他害リスクでは厚労省「まもろうよこころ」sourceを追加するが、直ちに危険がある場合は119を優先する

## 2. 入力

```json
{
  "deployment_locale": "JP-13",
  "triage_priority": "P1",
  "risk_group": null,
  "concern": null
}
```

`deployment_locale` は `JP`, `JP-13`, `Tokyo`, `東京都`, `ja-JP-Tokyo` などを受け付ける。未知のlocaleは `JP` default routeに落ちる。

## 3. 出力

```json
{
  "deployment_locale": "JP-13",
  "requested_locale": "JP-13",
  "jurisdiction_label_ja": "東京都",
  "triage_priority": "P1",
  "primary_action": "offer_confirmed_7119",
  "emergency_phone": "119",
  "consultation_route": {
    "show_7119_direct": true,
    "consultation_phone": "#7119",
    "status": "confirmed_local",
    "area_check_source_id": "jp.fdma.7119_area_list",
    "local_source_ids": ["jp.tokyo_fire.7119_center"]
  },
  "secondary_routes": [],
  "source_requirements": [],
  "source_records": [],
  "warnings": [],
  "forbidden_output": ["display_7119_as_nationwide_without_locale_check"]
}
```

## 4. primary_action

| primary_action | 意味 |
|---|---|
| `call_119_now` | P0。#7119ではなく119を最優先表示する |
| `offer_confirmed_7119` | localeで#7119実施確認済み。#7119を表示できる |
| `check_7119_area_before_display` | locale未確認。#7119を直接表示しない |

## 5. UI必須ルール

- `consultation_route.show_7119_direct=false` のとき、`#7119` を電話番号として表示しない
- P0では `primary_action=call_119_now` を最優先にする
- `display_7119_as_nationwide_without_locale_check` を禁止表現として扱う
- 東京消防庁sourceは `JP-13` / Tokyo deploymentでのみlocal routeとして扱う
- `source_records.raw_rag_ingest_allowed=false` の本文をRAG chunk化しない

## 6. 検証コマンド

```powershell
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\resolve_jp_emergency_route.py' --root 'D:\monshin-compass' --run-fixtures
```

```powershell
& 'C:\Users\sakur\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\monshin-compass\tools\evaluate_symptom_case.py' --root 'D:\monshin-compass' --locale JP-13 --fixture SCHEMA-TC-002
```
