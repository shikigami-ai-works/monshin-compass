#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ALLOWED_EVIDENCE_TYPES = {
    "emergency_sign",
    "seek_care_guidance",
    "symptom_overview",
    "risk_context",
    "self_observation",
    "unsupported",
}
SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")
RULE_ID_RE = re.compile(r"^RF-P[0-3]-[A-Z0-9-]+$")
SOURCE_ID_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")
PRIORITIES = ["P0", "P1", "P2", "P3"]


def load_json_subset(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: expected JSON-compatible YAML subset: {exc}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSONL: {exc}") from exc
    return rows


def collect_doc_rule_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(re.findall(r"RF-P[0-3]-[A-Z0-9-]+", path.read_text(encoding="utf-8", errors="replace")))


def selected_map(selected_cards: list[dict[str, Any]]) -> dict[str, Any]:
    return {item["card_id"]: item.get("value", "unknown") for item in selected_cards}


def val(values: dict[str, Any], card_id: str) -> Any:
    return values.get(card_id, "missing")


def known_present(value: Any) -> bool:
    if isinstance(value, list):
        return any(known_present(v) for v in value)
    return value not in (None, "", "no", "none", "unknown", "missing")


def risk_present(value: Any) -> bool:
    if isinstance(value, list):
        return any(v not in ("none", "unknown", "missing") for v in value)
    return value not in (None, "", "none", "unknown", "missing")


def c_p0_dyspnea_severe(values: dict[str, Any]) -> bool:
    return val(values, "dyspnea") == "severe"


def c_p0_cyanosis(values: dict[str, Any]) -> bool:
    return val(values, "cyanosis") == "yes"


def c_p0_unable_wake(values: dict[str, Any]) -> bool:
    return val(values, "unable_to_wake") == "yes"


def c_p0_confusion_acute(values: dict[str, Any]) -> bool:
    return val(values, "confusion") == "yes" and val(values, "sudden_onset") == "yes"


def c_p0_chest_severe(values: dict[str, Any]) -> bool:
    return val(values, "chest_pain") in {"severe", "pressure"}


def c_p0_blood_heavy(values: dict[str, Any]) -> bool:
    return val(values, "blood") == "heavy"


def c_p0_fainting(values: dict[str, Any]) -> bool:
    return val(values, "fainting") == "yes" and (
        known_present(val(values, "dyspnea"))
        or known_present(val(values, "chest_pain"))
        or val(values, "confusion") == "yes"
    )


def c_p0_seizure_prolonged(values: dict[str, Any]) -> bool:
    return val(values, "seizure") in {"prolonged", "repeated"}


def c_p0_sudden_neuro(values: dict[str, Any]) -> bool:
    return val(values, "sudden_onset") == "yes" and (
        val(values, "confusion") == "yes" or val(values, "severe_pain") == "sudden_severe"
    )


def c_p0_self_harm(values: dict[str, Any]) -> bool:
    return val(values, "self_harm") == "yes"


def c_p1_dyspnea_moderate(values: dict[str, Any]) -> bool:
    return val(values, "dyspnea") == "moderate"


def c_p1_trouble_breathing_with_fever(values: dict[str, Any]) -> bool:
    return val(values, "fever") == "yes" and val(values, "dyspnea") == "mild" and val(values, "worsening") == "yes"


def c_p1_chest_moderate(values: dict[str, Any]) -> bool:
    return val(values, "chest_pain") == "moderate"


def c_p1_blood_sputum_vomit(values: dict[str, Any]) -> bool:
    return val(values, "blood") in {"sputum", "vomit"}


def c_p1_fever_stiff_neck(values: dict[str, Any]) -> bool:
    return val(values, "fever") == "yes" and val(values, "stiff_neck") == "yes"


def c_p1_high_fever_worsening(values: dict[str, Any]) -> bool:
    return val(values, "fever") == "yes" and val(values, "worsening") == "yes" and val(values, "duration") == "days_4_plus"


def c_p1_persistent_vomit_diarrhea(values: dict[str, Any]) -> bool:
    return val(values, "vomiting_diarrhea") in {"persistent", "severe"}


def c_p1_dehydration(values: dict[str, Any]) -> bool:
    return val(values, "dehydration_signs") == "yes"


def c_p1_severe_pain(values: dict[str, Any]) -> bool:
    return val(values, "severe_pain") == "severe"


def c_p1_risk_group_with_dyspnea(values: dict[str, Any]) -> bool:
    return risk_present(val(values, "risk_group")) and known_present(val(values, "dyspnea"))


def c_p2_fever_cough_duration(values: dict[str, Any]) -> bool:
    return val(values, "fever") == "yes" and val(values, "cough") == "yes" and val(values, "duration") == "days_4_plus"


def c_p2_risk_group_fever_cough(values: dict[str, Any]) -> bool:
    return risk_present(val(values, "risk_group")) and (val(values, "fever") == "yes" or val(values, "cough") == "yes")


def c_p2_mild_dyspnea(values: dict[str, Any]) -> bool:
    return val(values, "dyspnea") == "mild" and val(values, "worsening") != "yes"


def c_p2_fever_unknown_duration(values: dict[str, Any]) -> bool:
    return val(values, "fever") == "yes" and val(values, "duration") == "unknown"


def c_p2_worsening_non_p0(values: dict[str, Any]) -> bool:
    return val(values, "worsening") == "yes"


def c_p2_unknown_safety_cards(values: dict[str, Any]) -> bool:
    return any(val(values, c) == "unknown" for c in ["dyspnea", "chest_pain", "confusion", "blood"])


def c_p3_mild_fever_cough(values: dict[str, Any]) -> bool:
    return val(values, "fever") == "yes" or val(values, "cough") == "yes"


def c_p3_no_primary_symptom(values: dict[str, Any]) -> bool:
    return val(values, "fever") == "no" and val(values, "cough") == "no" and val(values, "dyspnea") == "none"


def c_p3_unknown_only(values: dict[str, Any]) -> bool:
    return bool(values) and all(v == "unknown" for v in values.values())


RULE_CONDITIONS = {
    "RF-P0-DYSPNEA-SEVERE": c_p0_dyspnea_severe,
    "RF-P0-CYANOSIS": c_p0_cyanosis,
    "RF-P0-UNABLE-WAKE": c_p0_unable_wake,
    "RF-P0-CONFUSION-ACUTE": c_p0_confusion_acute,
    "RF-P0-CHEST-SEVERE": c_p0_chest_severe,
    "RF-P0-BLOOD-HEAVY": c_p0_blood_heavy,
    "RF-P0-FAINTING": c_p0_fainting,
    "RF-P0-SEIZURE-PROLONGED": c_p0_seizure_prolonged,
    "RF-P0-SUDDEN-NEURO": c_p0_sudden_neuro,
    "RF-P0-SELF-HARM": c_p0_self_harm,
    "RF-P1-DYSPNEA-MODERATE": c_p1_dyspnea_moderate,
    "RF-P1-TROUBLE-BREATHING-WITH-FEVER": c_p1_trouble_breathing_with_fever,
    "RF-P1-CHEST-MODERATE": c_p1_chest_moderate,
    "RF-P1-BLOOD-SPUTUM-VOMIT": c_p1_blood_sputum_vomit,
    "RF-P1-FEVER-STIFF-NECK": c_p1_fever_stiff_neck,
    "RF-P1-HIGH-FEVER-WORSENING": c_p1_high_fever_worsening,
    "RF-P1-PERSISTENT-VOMIT-DIARRHEA": c_p1_persistent_vomit_diarrhea,
    "RF-P1-DEHYDRATION": c_p1_dehydration,
    "RF-P1-SEVERE-PAIN": c_p1_severe_pain,
    "RF-P1-RISK-GROUP-WITH-DYSPNEA": c_p1_risk_group_with_dyspnea,
    "RF-P2-FEVER-COUGH-DURATION": c_p2_fever_cough_duration,
    "RF-P2-RISK-GROUP-FEVER-COUGH": c_p2_risk_group_fever_cough,
    "RF-P2-MILD-DYSPNEA": c_p2_mild_dyspnea,
    "RF-P2-FEVER-UNKNOWN-DURATION": c_p2_fever_unknown_duration,
    "RF-P2-WORSENING-NON-P0": c_p2_worsening_non_p0,
    "RF-P2-UNKNOWN-SAFETY-CARDS": c_p2_unknown_safety_cards,
    "RF-P3-MILD-FEVER-COUGH": c_p3_mild_fever_cough,
    "RF-P3-NO-PRIMARY-SYMPTOM": c_p3_no_primary_symptom,
    "RF-P3-UNKNOWN-ONLY": c_p3_unknown_only,
}


def rules_by_priority(rule_registry: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped = {priority: [] for priority in PRIORITIES}
    for rule in rule_registry.get("rules", []):
        grouped.setdefault(rule.get("priority"), []).append(rule)
    return grouped


def rule_priority_map(rule_registry: dict[str, Any]) -> dict[str, str]:
    return {rule["rule_id"]: rule["priority"] for rule in rule_registry.get("rules", []) if "rule_id" in rule and "priority" in rule}


def evaluate(selected_cards: list[dict[str, Any]], rule_registry: dict[str, Any]) -> dict[str, Any]:
    values = selected_map(selected_cards)
    grouped = rules_by_priority(rule_registry)
    matched = {priority: [] for priority in PRIORITIES}
    for priority in ["P0", "P1"]:
        for rule in grouped.get(priority, []):
            rule_id = rule["rule_id"]
            if RULE_CONDITIONS[rule_id](values):
                matched[priority].append(rule_id)
    if matched["P0"]:
        priority = "P0"
    elif matched["P1"]:
        priority = "P1"
    else:
        for rule in grouped.get("P2", []):
            rule_id = rule["rule_id"]
            if RULE_CONDITIONS[rule_id](values):
                matched["P2"].append(rule_id)
        if matched["P2"]:
            priority = "P2"
        else:
            for rule in grouped.get("P3", []):
                rule_id = rule["rule_id"]
                if RULE_CONDITIONS[rule_id](values):
                    matched["P3"].append(rule_id)
            priority = "P3"
    next_question = None
    if priority == "P2":
        explicit_unknown = [c for c in ["dyspnea", "chest_pain", "confusion", "blood"] if values.get(c) == "unknown"]
        if explicit_unknown:
            next_question = explicit_unknown[0]
        elif (values.get("fever") == "yes" or values.get("cough") == "yes") and "dyspnea" not in values:
            next_question = "dyspnea"
    return {"priority": priority, "rules": matched[priority], "next": next_question}


def validate_evidence_sources(evidence_sources: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = evidence_sources.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["evidence_sources.sources must be a non-empty list"]
    policy = evidence_sources.get("source_policy", {})
    forbidden = set(policy.get("forbidden_use", []))
    if "unreviewed_raw_page_embedding" not in forbidden:
        errors.append("evidence_sources.source_policy.forbidden_use must include unreviewed_raw_page_embedding")
    ids: set[str] = set()
    required_fields = policy.get("required_source_fields", [])
    if not isinstance(required_fields, list) or not required_fields:
        errors.append("evidence_sources.source_policy.required_source_fields must be a non-empty list")
    for idx, source in enumerate(sources):
        prefix = f"evidence_sources.sources[{idx}]"
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not SOURCE_ID_RE.match(source_id):
            errors.append(f"{prefix}: invalid source_id")
            continue
        if source_id in ids:
            errors.append(f"{prefix}: duplicate source_id {source_id}")
        ids.add(source_id)
        for field in required_fields:
            if field not in source:
                errors.append(f"{source_id}: missing {field}")
        for evidence_type in source.get("evidence_types", []):
            if evidence_type not in ALLOWED_EVIDENCE_TYPES:
                errors.append(f"{source_id}: unsupported evidence_type {evidence_type}")
        rights = source.get("rights", {})
        for field in ["raw_rag_ingest_allowed", "embedding_allowed", "ai_training_allowed", "requires_rights_review_before_storage"]:
            if not isinstance(rights.get(field), bool):
                errors.append(f"{source_id}: rights.{field} must be boolean")
        if rights.get("raw_rag_ingest_allowed") is False and "unreviewed_raw_page_embedding" not in forbidden:
            errors.append(f"{source_id}: raw RAG ingest is false but global forbidden_use does not block unreviewed embeddings")
        if rights.get("raw_rag_ingest_allowed") is True and source.get("status") != "rights_reviewed_for_raw_rag":
            errors.append(f"{source_id}: raw_rag_ingest_allowed=true requires status=rights_reviewed_for_raw_rag")
        if not source.get("retrieved_at") or not source.get("source_updated_at"):
            errors.append(f"{source_id}: retrieved_at and source_updated_at are required")
    return errors


def validate_rule_registry(
    rule_registry: dict[str, Any],
    symptom_registry: dict[str, Any],
    evidence_sources: dict[str, Any],
    doc_rule_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    rules = rule_registry.get("rules")
    if not isinstance(rules, list) or not rules:
        return ["red_flag_rules.rules must be a non-empty list"]
    card_ids = {card.get("card_id") for card in symptom_registry.get("cards", [])}
    sources_by_id = {source.get("source_id"): source for source in evidence_sources.get("sources", [])}
    priority_order = rule_registry.get("priority_order")
    if priority_order != PRIORITIES:
        errors.append("red_flag_rules.priority_order must be ['P0', 'P1', 'P2', 'P3']")
    ids: set[str] = set()
    for idx, rule in enumerate(rules):
        prefix = f"red_flag_rules.rules[{idx}]"
        rule_id = rule.get("rule_id")
        priority = rule.get("priority")
        if not isinstance(rule_id, str) or not RULE_ID_RE.match(rule_id):
            errors.append(f"{prefix}: invalid rule_id")
            continue
        if rule_id in ids:
            errors.append(f"{prefix}: duplicate rule_id {rule_id}")
        ids.add(rule_id)
        if priority not in PRIORITIES:
            errors.append(f"{rule_id}: invalid priority {priority}")
        elif not rule_id.startswith(f"RF-{priority}-"):
            errors.append(f"{rule_id}: priority does not match rule_id prefix")
        condition = rule.get("condition", {})
        if condition.get("language") != "validator_builtin_v1":
            errors.append(f"{rule_id}: unsupported condition.language")
        if condition.get("implementation_key") != rule_id:
            errors.append(f"{rule_id}: condition.implementation_key must match rule_id")
        if rule_id not in RULE_CONDITIONS:
            errors.append(f"{rule_id}: missing validator condition implementation")
        if not condition.get("expression"):
            errors.append(f"{rule_id}: condition.expression must not be empty")
        for card_id in rule.get("card_ids", []):
            if card_id != "all" and card_id not in card_ids:
                errors.append(f"{rule_id}: unknown card_id {card_id}")
        evidence_type = rule.get("evidence_type")
        if evidence_type not in ALLOWED_EVIDENCE_TYPES:
            errors.append(f"{rule_id}: unsupported evidence_type {evidence_type}")
        source_requirements = rule.get("source_requirements", [])
        if evidence_type != "unsupported" and not source_requirements:
            errors.append(f"{rule_id}: non-unsupported rules must define source_requirements")
        for source_id in source_requirements:
            source = sources_by_id.get(source_id)
            if source is None:
                errors.append(f"{rule_id}: unknown source_requirement {source_id}")
                continue
            if evidence_type not in source.get("evidence_types", []):
                errors.append(f"{rule_id}: source {source_id} does not support evidence_type {evidence_type}")
        for field in ["action_code", "display_block"]:
            if not isinstance(rule.get(field), str) or not rule.get(field):
                errors.append(f"{rule_id}: missing {field}")
        forbidden = set(rule.get("forbidden_output", []))
        for required in ["diagnosis", "treatment", "reassurance_no_care_needed"]:
            if required not in forbidden:
                errors.append(f"{rule_id}: forbidden_output missing {required}")
        if doc_rule_ids and rule_id not in doc_rule_ids:
            errors.append(f"{rule_id}: not found in docs/red-flag-rules.md")
    missing_impl = sorted(set(RULE_CONDITIONS) - ids)
    if missing_impl:
        errors.append(f"red_flag_rules: validator has conditions not present in data: {missing_impl}")
    return errors


def validate_registry(registry: dict[str, Any], rule_registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rule_priorities = rule_priority_map(rule_registry)
    cards = registry.get("cards")
    if not isinstance(cards, list) or not cards:
        return ["registry.cards must be a non-empty list"]
    allowed = set(registry.get("allowed_evidence_types", [])) or ALLOWED_EVIDENCE_TYPES
    ids: set[str] = set()
    for idx, card in enumerate(cards):
        prefix = f"cards[{idx}]"
        card_id = card.get("card_id")
        if not isinstance(card_id, str) or not SNAKE_CASE.match(card_id):
            errors.append(f"{prefix}: invalid card_id")
            continue
        if card_id in ids:
            errors.append(f"{prefix}: duplicate card_id {card_id}")
        ids.add(card_id)
        for section in ["category", "ui", "input", "question", "normalization", "red_flag", "retrieval", "privacy"]:
            if section not in card:
                errors.append(f"{card_id}: missing {section}")
        ui = card.get("ui", {})
        for field in ["label_ja", "short_label_ja", "group", "sort_order", "visible_default", "illustration_key", "accessibility_label_ja"]:
            if field not in ui:
                errors.append(f"{card_id}: missing ui.{field}")
        if ui.get("visible_default") is True and ui.get("sort_order", 999) > 30:
            errors.append(f"{card_id}: visible_default cards must sort <= 30")
        input_spec = card.get("input", {})
        values = input_spec.get("values", [])
        value_names = {v.get("value") for v in values if isinstance(v, dict)}
        if input_spec.get("default_value") not in value_names:
            errors.append(f"{card_id}: default_value not present in input.values")
        if input_spec.get("unknown_allowed") and "unknown" not in value_names:
            errors.append(f"{card_id}: unknown_allowed requires unknown value")
        red = card.get("red_flag", {})
        if card.get("category") == "safety" and red.get("safety_question") is not True:
            errors.append(f"{card_id}: safety cards must set safety_question=true")
        for rule_id in red.get("connected_rule_ids", []):
            if rule_id not in rule_priorities:
                errors.append(f"{card_id}: unknown connected_rule_id {rule_id}")
        evidence = set(card.get("retrieval", {}).get("evidence_types", []))
        if not evidence:
            errors.append(f"{card_id}: retrieval.evidence_types must not be empty")
        for item in evidence:
            if item not in allowed:
                errors.append(f"{card_id}: unsupported evidence_type {item}")
        p0_p1 = [r for r in red.get("connected_rule_ids", []) if rule_priorities.get(r) in {"P0", "P1"}]
        if p0_p1 and not (evidence & {"emergency_sign", "seek_care_guidance"}):
            errors.append(f"{card_id}: P0/P1-connected cards need emergency_sign or seek_care_guidance")
        if card.get("category") in {"primary", "safety"} and not card.get("normalization", {}).get("blocked_terms"):
            errors.append(f"{card_id}: primary/safety cards must define blocked_terms")
    for card_id in registry.get("question_flow", {}).get("next_question_priority", []):
        if card_id not in ids:
            errors.append(f"question_flow references unknown card {card_id}")
    return errors


def validate_fixtures(fixtures: list[dict[str, Any]], registry: dict[str, Any], rule_registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    card_ids = {card["card_id"] for card in registry["cards"]}
    rule_ids = {rule["rule_id"] for rule in rule_registry["rules"]}
    for case in fixtures:
        case_id = case.get("case_id", "<missing>")
        for item in case.get("selected_cards", []):
            if item.get("card_id") not in card_ids:
                errors.append(f"{case_id}: selected unknown card {item.get('card_id')}")
        for rule_id in case.get("expected_rules", []):
            if rule_id not in rule_ids:
                errors.append(f"{case_id}: expected unknown rule {rule_id}")
        result = evaluate(case.get("selected_cards", []), rule_registry)
        if result["priority"] != case.get("expected_priority"):
            errors.append(f"{case_id}: priority {result['priority']} != expected {case.get('expected_priority')}")
        expected_rules = set(case.get("expected_rules", []))
        actual_rules = set(result["rules"])
        if not expected_rules.issubset(actual_rules):
            errors.append(f"{case_id}: rules {sorted(actual_rules)} do not include expected {sorted(expected_rules)}")
        if result["next"] != case.get("expected_next"):
            errors.append(f"{case_id}: next {result['next']} != expected {case.get('expected_next')}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    root = Path(args.root)
    registry = load_json_subset(root / "data" / "symptom-cards.yaml")
    rule_registry = load_json_subset(root / "data" / "red-flag-rules.yaml")
    evidence_sources = load_json_subset(root / "data" / "evidence-sources.yaml")
    fixtures = load_jsonl(root / "tests" / "fixtures" / "symptom-card-cases.jsonl")
    doc_rule_ids = collect_doc_rule_ids(root / "docs" / "red-flag-rules.md")
    errors = validate_evidence_sources(evidence_sources)
    errors.extend(validate_rule_registry(rule_registry, registry, evidence_sources, doc_rule_ids))
    errors.extend(validate_registry(registry, rule_registry))
    errors.extend(validate_fixtures(fixtures, registry, rule_registry))
    if errors:
        print("FAIL: symptom card validation found issues", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"OK: {len(registry['cards'])} cards, {len(rule_registry['rules'])} red-flag rules, "
        f"{len(evidence_sources['sources'])} evidence sources, "
        f"and {len(fixtures)} fixtures validated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
