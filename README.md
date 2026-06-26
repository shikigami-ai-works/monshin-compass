# Monshin Compass

Smartphone-first next-action guidance prototype for symptom intake, with deterministic safety triage and Japan emergency-routing constraints.

Monshin Compass is not a diagnosis app. It does not identify diseases, rank diagnoses, recommend treatment, name medications, provide dosage guidance, or reassure users that care is unnecessary.

## Safety Boundary

- P0/P1/P2/P3 priority is owned by the deterministic evaluator, not by the UI.
- P0 prioritizes calling `119` in the Japan deployment context.
- `#7119` is not shown as a nationwide number. Direct display requires confirmed locale support from the route resolver.
- Unknown or skipped answers are never treated as safe or negative.
- LLM/RAG/source retrieval may support wording and evidence presentation, but must not decide red-flag priority.

## Current Status

This repository contains:

- `docs/`: layered product, safety, screen, routing, and evidence specifications.
- `data/`: symptom cards, red-flag rules, emergency routing data, and evidence source metadata.
- `tools/`: local validators, evaluator fixtures, routing checks, and API smoke checks.
- `app/`: a small Python HTTP server for the local prototype API and static web host.
- `web/`: the smartphone-first prototype shell.
- `tests/fixtures/`: fixture cases for evaluator and routing behavior.

Current `web/` is an implementation prototype surface. It is not the safety authority.

## Run Locally

```powershell
python app\server.py --host 127.0.0.1 --port 8765
```

Then open:

```text
http://127.0.0.1:8765/
```

## Verification

```powershell
node --check web\app.js
python tools\smoke_api.py
python tools\validate_symptom_cards.py --root .
python tools\resolve_jp_emergency_route.py --root . --run-fixtures
python tools\evaluate_symptom_case.py --root . --locale JP-13 --fixture SCHEMA-TC-001
python tools\evaluate_symptom_case.py --root . --locale JP-13 --fixture SCHEMA-TC-002
```

Runtime browser screenshots and click-through audit are still required before claiming final UI verification.

