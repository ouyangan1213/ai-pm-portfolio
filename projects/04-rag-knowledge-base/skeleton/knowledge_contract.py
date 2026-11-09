"""Illustrative skeleton of the knowledge-tool response contract.

Synthetic data only. Not production code.
"""
from __future__ import annotations

import datetime as dt
import hashlib

UNITS = [
    {"id": "u1", "text": "Kit Z lower limit of quantification is 5 units/uL.", "identifiers": {"KIT-Z"},
     "src_class": "internal_training", "locator": "Kit Z training deck, slide 7",
     "date": "2000-01-01", "valid_until": None, "conflict_group": "kitz-lloq"},
    {"id": "u2", "text": "Kit Z lower limit of quantification is 2 units/uL.", "identifiers": {"KIT-Z"},
     "src_class": "official", "locator": "Kit Z datasheet, page 2",
     "date": "2000-06-01", "valid_until": None, "conflict_group": "kitz-lloq"},
]
SNAPSHOT_IDENTIFIERS = {"KIT-Z"}
MANIFEST_SHA = hashlib.sha256(b"synthetic-manifest").hexdigest()


def search(query_identifier: str, query_text: str, top_k: int = 5) -> dict:
    top_k = min(top_k, 8)
    if query_identifier not in SNAPSHOT_IDENTIFIERS:
        # Only means "not in this snapshot", not "product does not exist".
        return {"do_not_guess": "identifier_not_in_snapshot", "manifest_sha": MANIFEST_SHA}

    hits = [u for u in UNITS if query_identifier in u["identifiers"]][:top_k]
    if not hits:
        return {"do_not_guess": "no_evidence", "manifest_sha": MANIFEST_SHA}

    groups = {u["conflict_group"] for u in hits if u["conflict_group"]}
    out = []
    for u in hits:
        conflicted = u["conflict_group"] in groups and sum(h["conflict_group"] == u["conflict_group"] for h in hits) > 1
        out.append({
            "snippet": u["text"][:300],
            "locator_human": u["locator"],
            "source_date": u["date"],
            "stale": bool(u["valid_until"] and u["valid_until"] < dt.date.today().isoformat()),
            "conflict": conflicted,
            "preferred": conflicted and u["src_class"] == "official",
        })
    return {"hits": out, "manifest_sha": MANIFEST_SHA}


if __name__ == "__main__":
    print(search("KIT-Z", "lower limit of quantification"))
    print(search("KIT-Q", "anything"))
