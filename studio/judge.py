#!/usr/bin/env python3
"""
The bedtime judge — Bonsai scores a story against canon/RUBRIC.md.

The judgment schema is grammar-pinned at decode time (llama-server json_schema),
so a 1.7B judge cannot return malformed scores. Same contract trick as the app.

Usage:
    python3 studio/judge.py story.txt --seed gilgamesh_enkidu
    cat story.txt | python3 studio/judge.py - --seed apollo13
"""
import argparse
import json
import pathlib
import sys
import urllib.request

WRITER = "http://127.0.0.1:8080"
ROOT = pathlib.Path(__file__).resolve().parents[1]

DIMENSIONS = ["imagination_spark", "resilience_modeled", "pride_in_humanity", "wonder_to_sleep_arc", "truth_anchor"]

SCHEMA = {
    "type": "object",
    "properties": {
        **{d: {"type": "number", "minimum": 0, "maximum": 1} for d in DIMENSIONS},
        "strongest_moment": {"type": "string", "minLength": 10, "maxLength": 200},
        "revision_note": {"type": "string", "minLength": 10, "maxLength": 200},
    },
    "required": DIMENSIONS + ["strongest_moment", "revision_note"],
    "additionalProperties": False,
}


def load_seed(seed_id: str) -> dict:
    canon = json.loads((ROOT / "canon" / "canon.json").read_text())
    for s in canon["seeds"]:
        if s["id"] == seed_id:
            return s
    sys.exit(f"unknown seed '{seed_id}' — see canon/canon.json")


def judge(story: str, seed: dict) -> dict:
    rubric = (ROOT / "canon" / "RUBRIC.md").read_text()
    prompt = (
        f"You are a strict editor of bedtime stories. Score this story against the rubric.\n\n"
        f"RUBRIC:\n{rubric}\n\n"
        f"SOURCE the story must honor: {seed['title']} — {seed['truth']}\n\n"
        f"STORY:\n{story}\n\n"
        f"Score every dimension 0-1. Be honest: 0.9+ is rare."
    )
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_schema", "json_schema": {"name": "judgment", "schema": SCHEMA}},
        "max_tokens": 300,
        "temperature": 0.2,
    }).encode()
    req = urllib.request.Request(
        WRITER + "/v1/chat/completions", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(json.load(r)["choices"][0]["message"]["content"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("story", help="path to story text, or - for stdin")
    ap.add_argument("--seed", required=True, help="canon seed id the story claims to honor")
    args = ap.parse_args()

    story = sys.stdin.read() if args.story == "-" else pathlib.Path(args.story).read_text()
    seed = load_seed(args.seed)
    verdict = judge(story, seed)

    scores = {d: verdict[d] for d in DIMENSIONS}
    composite = sum(scores.values()) / len(scores)
    sleep_gate = scores["wonder_to_sleep_arc"] >= 0.6

    print(json.dumps({
        "seed": seed["id"],
        "scores": {k: round(v, 2) for k, v in scores.items()},
        "composite": round(composite, 3),
        "sleep_gate": "PASS" if sleep_gate else "FAIL (absolute — the job is sleep)",
        "strongest_moment": verdict["strongest_moment"],
        "revision_note": verdict["revision_note"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
