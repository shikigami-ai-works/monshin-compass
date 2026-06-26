#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.server import create_server  # noqa: E402


def get_json(base: str, path: str) -> dict:
    with urlopen(f"{base}{path}", timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(base: str, path: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        f"{base}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> int:
    server = create_server("127.0.0.1", 0, ROOT)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        health = get_json(base, "/api/health")
        assert_equal("health.ok", health["ok"], True)

        cards = get_json(base, "/api/cards")
        assert_equal("first_screen_cards", cards["first_screen_cards"], ["fever", "cough", "dyspnea"])

        p0 = post_json(
            base,
            "/api/evaluate",
            {"locale": "JP-13", "selected_cards": [{"card_id": "dyspnea", "value": "severe"}]},
        )["result"]
        assert_equal("p0 priority", p0["triage_priority"], "P0")
        assert_equal("p0 action", p0["jp_emergency_route"]["primary_action"], "call_119_now")
        assert_equal("p0 show_7119_direct", p0["jp_emergency_route"]["consultation_route"]["show_7119_direct"], False)

        p1_tokyo = post_json(
            base,
            "/api/evaluate",
            {
                "locale": "JP-13",
                "selected_cards": [
                    {"card_id": "fever", "value": "yes"},
                    {"card_id": "cough", "value": "yes"},
                    {"card_id": "dyspnea", "value": "moderate"},
                ],
            },
        )["result"]
        assert_equal("p1 tokyo priority", p1_tokyo["triage_priority"], "P1")
        assert_equal("p1 tokyo #7119", p1_tokyo["jp_emergency_route"]["consultation_route"]["consultation_phone"], "#7119")

        p1_jp = post_json(
            base,
            "/api/evaluate",
            {
                "locale": "JP",
                "selected_cards": [
                    {"card_id": "fever", "value": "yes"},
                    {"card_id": "cough", "value": "yes"},
                    {"card_id": "dyspnea", "value": "moderate"},
                ],
            },
        )["result"]
        assert_equal("p1 jp priority", p1_jp["triage_priority"], "P1")
        assert_equal("p1 jp action", p1_jp["jp_emergency_route"]["primary_action"], "check_7119_area_before_display")
        assert_equal("p1 jp show_7119_direct", p1_jp["jp_emergency_route"]["consultation_route"]["show_7119_direct"], False)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print("OK: API smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
