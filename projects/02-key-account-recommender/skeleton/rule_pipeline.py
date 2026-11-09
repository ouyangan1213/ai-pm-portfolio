"""Illustrative skeleton of a rule-based recommender with a rule log.

Synthetic data only. Not production code.
"""
from collections import defaultdict

ALIASES = {"tgt-a": "TARGET_A", "target a": "TARGET_A", "tgt-b": "TARGET_B"}

CATALOG = [  # (product_code, target, species, family, discontinued)
    ("P-001", "TARGET_A", "human", "protein", False),
    ("P-002", "TARGET_A", "mouse", "protein", False),
    ("P-003", "TARGET_B", "human", "assay_kit", True),
]

PIPELINE = {  # account_site -> list of (raw target name, modality, stage)
    "Site-1": [("tgt-a", "antibody", "Phase 2"), ("TGT-B", "cell therapy", "Preclinical")],
}

TOP_CAP_PER_FAMILY = 2


def gates(site, product, context, log):
    code, target, species, family, discontinued = product
    if species != "human" and context.get("human_only"):
        log.append((site, code, "BLOCK", "species gate: context is human-only"))
        return False
    log.append((site, code, "PASS", "all gates"))
    return True


def recommend(site):
    log, candidates = [], []
    for raw, modality, stage in PIPELINE[site]:
        target = ALIASES.get(raw.lower())
        if target is None:
            log.append((site, raw, "MISS", "target not in alias table"))
            continue
        for p in CATALOG:
            if p[1] == target and gates(site, p, {"human_only": False}, log):
                score = {"Phase 2": 3, "Phase 1": 2}.get(stage, 1) + (1 if p[2] == "human" else 0)
                note = "discontinued, may need custom production" if p[4] else ""
                candidates.append((score, p, note))

    candidates.sort(key=lambda c: -c[0])
    top, optional, per_family = [], [], defaultdict(int)
    for score, p, note in candidates:
        if per_family[p[3]] < TOP_CAP_PER_FAMILY and p[2] == "human":
            top.append((p[0], note)); per_family[p[3]] += 1
        else:
            optional.append((p[0], note))
    return {"top": top, "optional": optional}, log


if __name__ == "__main__":
    result, rule_log = recommend("Site-1")
    print(result)
    for line in rule_log:
        print(line)
