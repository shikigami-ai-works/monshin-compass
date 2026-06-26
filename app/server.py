#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
WEB = ROOT / "web"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from evaluate_symptom_case import build_output, validate_selected  # noqa: E402
from validate_symptom_cards import load_json_subset  # noqa: E402


SAFE_CARD_COPY: dict[str, dict[str, str]] = {
    "fever": {"label": "発熱・熱っぽさ", "hint": "熱っぽさや発熱感"},
    "cough": {"label": "咳・痰", "hint": "咳や痰がある"},
    "dyspnea": {"label": "息苦しさ", "hint": "呼吸のしづらさ"},
    "chest_pain": {"label": "胸の痛み・圧迫感", "hint": "胸の痛みや締めつけ"},
    "confusion": {"label": "意識や受け答え", "hint": "普段と違う反応"},
    "blood": {"label": "血が混じる", "hint": "痰や吐物などの血"},
    "cyanosis": {"label": "唇や顔色の変化", "hint": "青い・灰色・白っぽい変化"},
    "unable_to_wake": {"label": "起こしても反応が弱い", "hint": "目覚めにくい状態"},
    "fainting": {"label": "失神・倒れた", "hint": "気を失った、倒れた"},
    "seizure": {"label": "けいれん", "hint": "長い、または繰り返すけいれん"},
    "sudden_onset": {"label": "急な発症・急な悪化", "hint": "急に始まった、急に悪化"},
    "stiff_neck": {"label": "首が硬い", "hint": "発熱と首の硬さ"},
    "severe_pain": {"label": "強い痛み", "hint": "急な強い痛みを含む"},
    "vomiting_diarrhea": {"label": "嘔吐・下痢", "hint": "続く、強い嘔吐や下痢"},
    "dehydration_signs": {"label": "水分・尿の少なさ", "hint": "水分が取れない、尿が少ない"},
    "risk_group": {"label": "注意が必要な背景", "hint": "子ども・高齢・妊娠・持病など"},
    "duration": {"label": "続いている期間", "hint": "いつから続いているか"},
    "worsening": {"label": "悪化している", "hint": "時間とともに悪くなっている"},
    "self_harm": {"label": "自傷・他害のおそれ", "hint": "今すぐ安全確保が必要な危機"},
}

SAFE_VALUE_COPY: dict[str, str] = {
    "yes": "ある",
    "no": "ない",
    "unknown": "わからない",
    "none": "ない",
    "mild": "少し",
    "moderate": "はっきりある",
    "severe": "かなり強い",
    "pressure": "圧迫感・締めつけ",
    "sputum": "痰に少し",
    "vomit": "吐いたものに混じる",
    "heavy": "多い・止まらない",
    "prolonged": "長い",
    "repeated": "繰り返す",
    "sudden_severe": "急に強い",
    "persistent": "続いている",
    "hours_0_24": "24時間以内",
    "days_1_3": "1-3日",
    "days_4_plus": "4日以上",
    "weeks": "数週間",
    "child": "子ども",
    "older_adult": "高齢",
    "pregnant": "妊娠中・可能性あり",
    "chronic_condition": "持病あり",
    "immunocompromised": "免疫低下",
    "multiple": "複数あり",
}


class AppData:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.registry = load_json_subset(root / "data" / "symptom-cards.yaml")
        self.rule_registry = load_json_subset(root / "data" / "red-flag-rules.yaml")
        self.evidence_sources = load_json_subset(root / "data" / "evidence-sources.yaml")
        self.jp_routing = load_json_subset(root / "data" / "jp-emergency-routing.yaml")

    def cards_payload(self) -> dict[str, Any]:
        cards = []
        for card in sorted(self.registry.get("cards", []), key=lambda item: item.get("ui", {}).get("sort_order", 999)):
            card_id = card["card_id"]
            copy = SAFE_CARD_COPY.get(card_id, {"label": card_id.replace("_", " "), "hint": card_id})
            values = []
            for value in card.get("input", {}).get("values", []):
                raw_value = value.get("value")
                values.append(
                    {
                        "value": raw_value,
                        "label": SAFE_VALUE_COPY.get(raw_value, str(raw_value)),
                        "severity_rank": value.get("severity_rank", 0),
                        "is_unknown": value.get("is_unknown", False),
                    }
                )
            cards.append(
                {
                    "card_id": card_id,
                    "label": copy["label"],
                    "hint": copy["hint"],
                    "category": card.get("category"),
                    "group": card.get("ui", {}).get("group"),
                    "sort_order": card.get("ui", {}).get("sort_order"),
                    "visible_default": card.get("ui", {}).get("visible_default", False),
                    "skip_allowed": card.get("question", {}).get("skip_allowed", True),
                    "answer_style": card.get("question", {}).get("answer_style"),
                    "values": values,
                }
            )
        return {
            "schema_version": self.registry.get("schema_version"),
            "cards": cards,
            "first_screen_cards": self.registry.get("question_flow", {}).get("first_screen_cards", []),
            "next_question_priority": self.registry.get("question_flow", {}).get("next_question_priority", []),
            "safety_boundary": self.rule_registry.get("medical_safety_boundary", {}),
        }

    def evaluate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        selected = normalize_selected_cards(payload.get("selected_cards", []))
        locale = str(payload.get("locale") or "JP-13")
        errors = validate_selected(selected, self.registry)
        if errors:
            raise ValueError("; ".join(errors))
        return build_output(
            selected,
            self.registry,
            self.rule_registry,
            self.evidence_sources,
            self.jp_routing,
            locale,
        )


def normalize_selected_cards(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, dict):
        return [{"card_id": key, "value": value} for key, value in raw.items() if value not in (None, "", "missing")]
    if isinstance(raw, list):
        selected = []
        for item in raw:
            if not isinstance(item, dict):
                raise ValueError("selected_cards must contain objects")
            card_id = item.get("card_id")
            value = item.get("value")
            if card_id and value not in (None, "", "missing"):
                selected.append({"card_id": card_id, "value": value})
        return selected
    raise ValueError("selected_cards must be an object or list")


def create_handler(data: AppData) -> type[BaseHTTPRequestHandler]:
    class MonshinHandler(BaseHTTPRequestHandler):
        server_version = "MonshinCompass/0.1"

        def log_message(self, fmt: str, *args: Any) -> None:
            sys.stderr.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), fmt % args))

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/api/health":
                self.send_json({"ok": True, "service": "monshin-compass"})
                return
            if parsed.path == "/api/cards":
                self.send_json(data.cards_payload())
                return
            self.serve_static(parsed.path)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/api/evaluate":
                self.send_error(404, "Unknown API endpoint")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length > 65536:
                    self.send_error(413, "Request too large")
                    return
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
                self.send_json({"ok": True, "result": data.evaluate_payload(payload)})
            except (json.JSONDecodeError, ValueError) as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=400)

        def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def serve_static(self, request_path: str) -> None:
            relative = unquote(request_path.lstrip("/")) or "index.html"
            if relative.endswith("/"):
                relative += "index.html"
            web_root = WEB.resolve()
            target = (web_root / relative).resolve()
            if not str(target).startswith(str(web_root)) or not target.is_file():
                self.send_error(404, "File not found")
                return
            content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            body = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8" if content_type.startswith("text/") else content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return MonshinHandler


def create_server(host: str, port: int, root: Path = ROOT) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), create_handler(AppData(root)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    httpd = create_server(args.host, args.port)
    print(f"Monshin Compass serving on http://{args.host}:{httpd.server_port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
