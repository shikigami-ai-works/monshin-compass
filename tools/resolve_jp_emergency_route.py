#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PRIORITIES = {"P0", "P1", "P2", "P3"}


def load_json(path: Path) -> dict[str, Any]:
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


def normalize(value: str | None) -> str:
    return (value or "").strip().casefold()


def find_route(routing: dict[str, Any], locale: str) -> dict[str, Any]:
    needle = normalize(locale)
    default = None
    for route in routing.get("routes", []):
        if route.get("route_id") == "jp-default":
            default = route
        keys = [route.get("deployment_locale"), route.get("route_id"), *route.get("aliases", [])]
        if needle and needle in {normalize(key) for key in keys if key}:
            return route
    if default is None:
        raise ValueError("routing data must include route_id=jp-default")
    return default


def source_records(source_ids: list[str], evidence_sources: dict[str, Any]) -> list[dict[str, Any]]:
    sources_by_id = {source["source_id"]: source for source in evidence_sources.get("sources", [])}
    records = []
    for source_id in source_ids:
        source = sources_by_id.get(source_id)
        if source is None:
            records.append({"source_id": source_id, "missing": True})
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


def unique(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def resolve_route(
    routing: dict[str, Any],
    evidence_sources: dict[str, Any],
    locale: str,
    triage_priority: str,
    risk_group: str | None = None,
    concern: str | None = None,
) -> dict[str, Any]:
    priority = triage_priority.upper()
    if priority not in PRIORITIES:
        raise ValueError(f"triage_priority must be one of {sorted(PRIORITIES)}")

    route = find_route(routing, locale)
    policy = routing.get("policy", {})
    special_routes = routing.get("special_routes", {})
    warnings = list(route.get("warnings", []))
    source_ids: list[str] = []

    if priority == "P0":
        primary_action = "call_119_now"
        show_7119_direct = False
        consultation_phone = None
        source_ids.extend(route.get("fallback_source_ids", []))
        source_ids.insert(0, "jp.fdma.ambulance_manual")
        warnings.append("P0 overrides #7119 consultation. Show 119/emergency routing first.")
    elif route.get("show_7119_direct") is True:
        primary_action = "offer_confirmed_7119"
        show_7119_direct = True
        consultation_phone = route.get("consultation_phone")
        source_ids.extend(policy.get("national_consultation_source_ids", []))
        source_ids.extend(route.get("local_source_ids", []))
    else:
        primary_action = "check_7119_area_before_display"
        show_7119_direct = False
        consultation_phone = None
        source_ids.extend(policy.get("national_consultation_source_ids", []))
        source_ids.append(route.get("area_check_source_id"))
        source_ids.extend(route.get("fallback_source_ids", []))
        warnings.append("#7119 is not displayed directly because deployment locale is not confirmed.")

    secondary_routes = []
    if risk_group == "child":
        child = special_routes.get("child", {})
        secondary_routes.append(
            {
                "route_id": child.get("route_id"),
                "consultation_phone": child.get("consultation_phone"),
                "source_id": child.get("source_id"),
                "reason": "risk_group=child",
            }
        )
        source_ids.append(child.get("source_id"))
        warnings.extend(child.get("warnings", []))

    if concern == "self_harm":
        self_harm = special_routes.get("self_harm", {})
        secondary_routes.append(
            {
                "route_id": self_harm.get("route_id"),
                "consultation_phone": None,
                "source_id": self_harm.get("source_id"),
                "reason": "concern=self_harm",
            }
        )
        source_ids.append(self_harm.get("source_id"))
        warnings.extend(self_harm.get("warnings", []))

    source_ids = unique(source_ids)
    return {
        "deployment_locale": route.get("deployment_locale"),
        "requested_locale": locale,
        "jurisdiction_label_ja": route.get("jurisdiction_label_ja"),
        "triage_priority": priority,
        "primary_action": primary_action,
        "emergency_phone": policy.get("emergency_phone", "119"),
        "consultation_route": {
            "show_7119_direct": show_7119_direct,
            "consultation_phone": consultation_phone,
            "status": route.get("consultation_7119_status"),
            "area_check_source_id": route.get("area_check_source_id"),
            "local_source_ids": route.get("local_source_ids", []),
        },
        "secondary_routes": secondary_routes,
        "source_requirements": source_ids,
        "source_records": source_records(source_ids, evidence_sources),
        "warnings": unique(warnings),
        "forbidden_output": policy.get("forbidden_output", []),
    }


def validate_routing_data(routing: dict[str, Any], evidence_sources: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source_ids = {source["source_id"] for source in evidence_sources.get("sources", [])}
    if routing.get("policy", {}).get("p0_overrides_consultation") is not True:
        errors.append("routing.policy.p0_overrides_consultation must be true")
    route_ids = set()
    for route in routing.get("routes", []):
        route_id = route.get("route_id")
        if not route_id:
            errors.append("route missing route_id")
            continue
        if route_id in route_ids:
            errors.append(f"duplicate route_id {route_id}")
        route_ids.add(route_id)
        for field in ["deployment_locale", "consultation_7119_status", "show_7119_direct", "area_check_source_id"]:
            if field not in route:
                errors.append(f"{route_id}: missing {field}")
        for source_id in route.get("local_source_ids", []) + route.get("fallback_source_ids", []) + [route.get("area_check_source_id")]:
            if source_id and source_id not in source_ids:
                errors.append(f"{route_id}: unknown source_id {source_id}")
        if route.get("show_7119_direct") is True and not route.get("consultation_phone"):
            errors.append(f"{route_id}: show_7119_direct requires consultation_phone")
        if route.get("show_7119_direct") is False and route.get("consultation_phone"):
            errors.append(f"{route_id}: hidden #7119 route must not expose consultation_phone")
    if "jp-default" not in route_ids:
        errors.append("routing.routes must include jp-default")
    for special_id, route in routing.get("special_routes", {}).items():
        source_id = route.get("source_id")
        if source_id not in source_ids:
            errors.append(f"special_routes.{special_id}: unknown source_id {source_id}")
    return errors


def run_fixtures(root: Path, routing: dict[str, Any], evidence_sources: dict[str, Any]) -> list[str]:
    errors = []
    fixtures = load_jsonl(root / "tests" / "fixtures" / "jp-emergency-routing-cases.jsonl")
    for case in fixtures:
        result = resolve_route(
            routing,
            evidence_sources,
            case["locale"],
            case["triage_priority"],
            case.get("risk_group"),
            case.get("concern"),
        )
        case_id = case.get("case_id", "<missing>")
        checks = {
            "expected_primary_action": result["primary_action"],
            "expected_show_7119_direct": result["consultation_route"]["show_7119_direct"],
            "expected_consultation_phone": result["consultation_route"]["consultation_phone"],
        }
        secondary_phone = None
        if result["secondary_routes"]:
            secondary_phone = result["secondary_routes"][0].get("consultation_phone")
        checks["expected_secondary_phone"] = secondary_phone
        for expected_key, actual in checks.items():
            if case.get(expected_key) != actual:
                errors.append(f"{case_id}: {expected_key} expected {case.get(expected_key)!r}, got {actual!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--locale", default="JP")
    parser.add_argument("--priority", default="P2")
    parser.add_argument("--risk-group", default=None)
    parser.add_argument("--concern", default=None)
    parser.add_argument("--run-fixtures", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    routing = load_json(root / "data" / "jp-emergency-routing.yaml")
    evidence_sources = load_json(root / "data" / "evidence-sources.yaml")
    errors = validate_routing_data(routing, evidence_sources)
    if args.run_fixtures:
        errors.extend(run_fixtures(root, routing, evidence_sources))
    if errors:
        print("FAIL: jp emergency routing validation found issues", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.run_fixtures:
        print("OK: jp emergency routing data and fixtures validated")
        return 0
    print(
        json.dumps(
            resolve_route(evidence_sources=evidence_sources, routing=routing, locale=args.locale, triage_priority=args.priority, risk_group=args.risk_group, concern=args.concern),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
