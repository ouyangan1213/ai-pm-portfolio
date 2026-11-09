"""Illustrative skeleton: rule-first batch with a grounded local-LLM fallback.

Synthetic data only. Not production code.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import urllib.request

LOCKS = ["./project_a/llm_busy.lock", "./shared/llm_busy.lock"]
SHARED_LOCK = LOCKS[1]
ENDPOINT = "http://localhost:8000/v1/chat/completions"   # local OpenAI-compatible server
MODALITY_RULES = {"car-t": "cell therapy", "adc": "antibody-drug conjugate", "mab": "antibody"}


def locks_free() -> bool:
    return all(not os.path.exists(p) or os.path.getsize(p) == 0 for p in LOCKS)


def acquire(owner: str):
    with open(SHARED_LOCK, "w") as f:
        f.write(f"{owner} {dt.datetime.now().isoformat(timespec='seconds')}\n")


def release(owner: str):
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    os.rename(SHARED_LOCK, f"{SHARED_LOCK}.released_{owner}_{stamp}")  # keep history, never delete


def rule_modality(text: str) -> str | None:
    t = text.lower()
    return next((v for k, v in MODALITY_RULES.items() if k in t), None)


def llm_modality(text: str) -> str:
    body = {"model": "local-quality", "temperature": 0,
            "messages": [{"role": "system", "content": "Return JSON {\"modality\": str, \"evidence\": str}. "
                          "evidence must be an exact substring of the input. If unsure, modality=\"NOT FOUND\"."},
                         {"role": "user", "content": text}]}
    req = urllib.request.Request(ENDPOINT, json.dumps(body).encode(), {"Content-Type": "application/json"})
    out = json.loads(json.load(urllib.request.urlopen(req))["choices"][0]["message"]["content"])
    return out["modality"] if out.get("evidence") and out["evidence"] in text else "NOT FOUND"


def run(rows: list[str], owner: str = "workstream-b") -> list[dict]:
    results, pending = [], []
    for r in rows:
        m = rule_modality(r)
        (results.append({"text": r, "modality": m, "by": "rule"}) if m else pending.append(r))
    if pending:
        if not locks_free():
            raise RuntimeError("local model busy; reschedule")
        acquire(owner)
        try:
            results += [{"text": r, "modality": llm_modality(r), "by": "llm"} for r in pending]
        finally:
            release(owner)
    return results


if __name__ == "__main__":
    print(run(["Program X is a CAR-T against Target A", "Program Y, bispecific format"]))
