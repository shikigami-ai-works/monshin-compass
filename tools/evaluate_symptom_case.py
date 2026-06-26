#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from resolve_jp_emergency_route import resolve_route
from validate_symptom_cards import evaluate, load_json_subset, load_jsonl


def parse_set_args(items: list[str]) -> list[dict[str, Any]]:
    selected = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"--set expects card_id=value, got {item!r}")
        card_id, value = item.split("=", 1)
        if not card_id or not value:
            raise ValueError(f"--set expects non-empty card_id and value, got {item!r}")
        selected.append({"card_id": card_id, "value": value})
    return selected


def parse_json_input(raw: str) -> list[dict[str, Any]]:
    payload = json.loads(raw)
    if isinstance(payload, dict) and "selected_cards" in payload:
        payload = payload["selected_cards"]
    if isinstance(payload, dict):
        return [{"card_id": key, "value": value} for key, value in payload.items()]
    if isinstance(payload, list):
        return payload
    raise ValueError("--json must be an object, a list, or an object with selected_cards")


def load_fixture(root: Path, case_id: str) -> list[dict[str, Any]]:
    fixtures = load_jsonl(root / "tests" / "fixtures" / "symptom-card-cases.jsonl")
    for case in fixtures:
        if case.get("case_id") == case_id:
            return case.get("selected_cards", [])
    raise ValueError(f"fixture case_id not found: {case_id}")


def validate_selected(selected: list[dict[str, Any]], registry: dict[str, Any]) -> list[str]:
    errors = []
    cards = {card["card_id"]: card for card in registry.get("cards", [])}
    for idx, item in enumerate(selected):
        card_id = item.get("card_id")
        if card_id not in cards:
            errors.append(f"selected[{idx}]: unknown card_id {card_id!r}")
            continue
        allowed_values = {value["value"] for value in cards[card_id].get("input", {}).get("values", [])}
        value = item.get("value", "unknown")
        if value not in allowed_values:
            errors.append(f"selected[{idx}]: unsupported value {value!r} for {card_id}; allowed={sorted(allowed_values)}")
    return errors


def first_rule_for_priority(rule_registry: dict[str, Any], priority: str) -> dict[str, Any] | None:
    for rule in rule_registry.get("rules", []):
        if rule.get("priority") == priority:
            return rule
    return None


def source_records(source_requirements: list[str], evidence_sources: dict[str, Any]) -> list[dict[str, Any]]:
    sources_by_id = {source["source_id"]: source for source in evidence_sources.get("sources", [])}
    records = []
    for source_id in source_requirements:
        source = sources_by_id.get(source_id)
        if source is None:
            continue
        rights = source.get("rights", {})
        records.append(
            {
                "source_id": source_id,
                "title": source.get("title"),
                "publisher": source.get("publisher"),
                "url": source.get("url"),
                "retrieved_at": source.get("retrieved_at"),
                "source_updated_at": source.get("source_updated_at"),
                "status": source.get("status"),
                "raw_rag_ingest_allowed": rights.get("raw_rag_ingest_allowed"),
                "embedding_allowed": rights.get("embedding_allowed"),
                "requires_rights_review_before_storage": rights.get("requires_rights_review_before_storage"),
            }
        )
    return records


def build_output(
    selected: list[dict[str, Any]],
    registry: dict[str, Any],
    rule_registry: dict[str, Any],
    evidence_sources: dict[str, Any],
    jp_routing: dict[str, Any] | None = None,
    locale: str | None = None,
) -> dict[str, Any]:
    result = evaluate(selected, rule_registry)
    rules_by_id = {rule["rule_id"]: rule for rule in rule_registry.get("rules", [])}
    matched_rules = [rules_by_id[rule_id] for rule_id in result["rules"] if rule_id in rules_by_id]
    primary_rule = matched_rules[0] if matched_rules else first_rule_for_priority(rule_registry, result["priority"])
    priority_defaults = {item["priority"]: item for item in rule_registry.get("priorities", [])}
    default_block = priority_defaults.get(result["priority"], {}).get("default_display_block")
    matched_card_ids = []
    for rule in matched_rules:
        for card_id in rule.get("card_ids", []):
            if card_id != "all" and card_id not in matched_card_ids:
                matched_card_ids.append(card_id)
    evidence_types = []
    source_requirements = []
    forbidden_output = []
    for rule in matched_rules:
        evidence_type = rule.get("evidence_type")
        if evidence_type and evidence_type not in evidence_types:
            evidence_types.append(evidence_type)
        for source in rule.get("source_requirements", []):
            if source not in source_requirements:
                source_requirements.append(source)
        for item in rule.get("forbidden_output", []):
            if item not in forbidden_output:
                forbidden_output.append(item)
    needs_more_input = result["next"] is not None or "RF-P2-UNKNOWN-SAFETY-CARDS" in result["rules"]
    output = {
        "triage_priority": result["priority"],
        "matched_rule_ids": result["rules"],
        "matched_card_ids": matched_card_ids,
        "action_code": primary_rule.get("action_code") if primary_rule else "ask_primary_symptom",
        "evidence_types": evidence_types or priority_defaults.get(result["priority"], {}).get("default_evidence_types", []),
        "needs_more_input": needs_more_input,
        "next_question_card_id": result["next"],
        "source_requirements": source_requirements,
        "source_records": source_records(source_requirements, evidence_sources),
        "rag_transfer_mode": evidence_sources.get("source_policy", {}).get("rag_default_mode"),
        "raw_page_text_to_rag_default": evidence_sources.get("source_policy", {}).get("raw_page_text_to_rag_default"),
        "display_block": (primary_rule.get("display_block") if primary_rule else default_block),
        "forbidden_output": forbidden_output or ["diagnosis", "treatment", "reassurance_no_care_needed"],
        "selected_cards": selected,
        "safety_boundary": rule_registry.get("medical_safety_boundary", {}),
    }
    if jp_routing is not None and locale:
        selected_values = {item.get("card_id"): item.get("value") for item in selected}
        risk_group = selected_values.get("risk_group")
        if risk_group in (None, "none", "unknown", "missing"):
            risk_group = None
        concern = "self_harm" if selected_values.get("self_harm") == "yes" else None
        output["jp_emergency_route"] = resolve_route(
            jp_routing,
            evidence_sources,
            locale,
            result["priority"],
            risk_group=risk_group,
            concern=concern,
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--locale", default=None, help="Optional deployment locale, such as JP or JP-13.")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--set", action="append", default=None, metavar="CARD=VALUE")
    input_group.add_argument("--json", default=None)
    input_group.add_argument("--fixture", default=None)
    args = parser.parse_args()

    root = Path(args.root)
    registry = load_json_subset(root / "data" / "symptom-cards.yaml")
    rule_registry = load_json_subset(root / "data" / "red-flag-rules.yaml")
    evidence_sources = load_json_subset(root / "data" / "evidence-sources.yaml")
    jp_routing = load_json_subset(root / "data" / "jp-emergency-routing.yaml") if args.locale else None
    try:
        if args.set is not None:
            selected = parse_set_args(args.set)
        elif args.json is not None:
            selected = parse_json_input(args.json)
        else:
            selected = load_fixture(root, args.fixture)
        errors = validate_selected(selected, registry)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 2
        print(
            json.dumps(
                build_output(selected, registry, rule_registry, evidence_sources, jp_routing, args.locale),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
