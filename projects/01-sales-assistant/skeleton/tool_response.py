"""Illustrative skeleton: how every assistant tool shapes its response.

Synthetic data only. Not production code.
"""
from dataclasses import dataclass, field


@dataclass
class Caller:
    subject: str            # opaque user id after identity verification
    territories: set[str]   # e.g. {"US-East"}
    is_global: bool = False


@dataclass
class ToolResult:
    result: dict
    steps_for_user: list[str]          # plain language, no tool/table names
    data_as_of: str                    # snapshot date shown to the user
    gaps: list[str] = field(default_factory=list)  # "not in snapshot" vs "no evidence"


# Synthetic example rows: (account, region, recommended product family, reason)
SNAPSHOT = [
    ("Account Alpha", "US-East", "Target-A proteins", "pipeline lists a Target-A program in Phase 2"),
    ("Account Beta", "EU-West", "Assay kits", "bought related reagents last quarter"),
]


def recommend_for_region(caller: Caller, region: str) -> ToolResult:
    rows = [r for r in SNAPSHOT if r[1] == region]
    steps = [f"Looked up recommendations for accounts in {region}."]

    if not (caller.is_global or region in caller.territories):
        # Out of territory: counts only, never details.
        steps.append("This region is outside your territory, so only a count is shown.")
        return ToolResult({"region": region, "accounts_with_recommendations": len(rows)},
                          steps, data_as_of="2000-01-01")

    if not rows:
        return ToolResult({"region": region, "items": []}, steps, "2000-01-01",
                          gaps=["identifier_not_in_snapshot: no accounts for this region in the current snapshot"])

    steps.append(f"Found {len(rows)} account(s); listing the top product family and the reason for each.")
    items = [{"account": a, "offer": p, "why": why} for a, _, p, why in rows]
    return ToolResult({"region": region, "items": items}, steps, data_as_of="2000-01-01")


if __name__ == "__main__":
    me = Caller(subject="user-001", territories={"US-East"})
    print(recommend_for_region(me, "US-East"))
    print(recommend_for_region(me, "EU-West"))
