"""Illustrative skeleton: template-first parsing, LLM fallback, append-only version check.

Synthetic data only. Not production code.
"""
from __future__ import annotations

import re

TEMPLATE = re.compile(r"Catalog#\s*(?P<code>[A-Z0-9-]+).*?Price:\s*\$(?P<price>[\d.]+)", re.S)


def parse_page(html: str) -> dict | None:
    m = TEMPLATE.search(html)
    if m:
        return {"catalog_no": m["code"], "price_usd": float(m["price"]), "parsed_by": "template"}
    return None


def llm_normalize(html: str) -> dict:
    """Fallback: send only the public product page text to a LOCAL model and ask for JSON.
    Output is validated; any field the model cannot ground in the text stays "NOT FOUND"."""
    raise NotImplementedError("call local model here")


def build_increment(previous: list[dict], pages: list[tuple[str, str]], vendor: str) -> list[dict]:
    new_rows = []
    for url, html in pages:
        row = parse_page(html) or llm_normalize(html)
        if str(row["price_usd"]) not in html and f"{row['price_usd']:.2f}" not in html:
            raise ValueError(f"price not found in source text: {url}")
        new_rows.append({"vendor": vendor, "source_url": url, "target": "NOT FOUND", **row})

    merged = previous + new_rows
    keys = [(r["vendor"], r["catalog_no"]) for r in merged]
    assert len(keys) == len(set(keys)), "duplicate (vendor, catalog_no)"
    assert merged[: len(previous)] == previous, "previous rows must not change"
    return merged


if __name__ == "__main__":
    pages = [("https://vendor.example/p/1", "Catalog# VX-100 ... Price: $250.00")]
    print(build_increment([], pages, vendor="Vendor X"))
