"""Snapshot fal.ai's text-to-image and image-to-image catalogue with list prices.

Usage: with-secrets uv run python scripts/fal_catalogue.py
Writes catalogue/fal-YYYY-MM-DD.jsonl, one row per active endpoint, sorted by category then price.

Endpoints (fal Platform API, checked 2026-10-28):
  GET https://api.fal.ai/v1/models?category=<cat>&status=active&limit=100&cursor=<c>
  GET https://api.fal.ai/v1/models/pricing?endpoint_id=<id>&endpoint_id=<id>...
Pricing is rate-limited (429 after ~2 quick calls); a batch fails with 404 if any id in it has
no price, so those batches fall back to one id at a time.

Caveat: token-billed models (OpenAI GPT Image, Google Nano Banana Lite, Microsoft MAI) come back
as unit_price 1 with unit "units" or "credits". That is a placeholder, not a price: read the
model page (https://fal.ai/models/<endpoint_id>) for the real per-image cost.
"""
import datetime
import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.fal.ai/v1"
KEY = os.environ["FAL_KEY"]
CATEGORIES = ["text-to-image", "image-to-image"]


def get(path, params):
    req = urllib.request.Request(f"{API}{path}?{urllib.parse.urlencode(params)}",
                                 headers={"Authorization": f"Key {KEY}"})
    for attempt in range(5):
        try:
            return json.load(urllib.request.urlopen(req))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"rate-limited: {path}")


def list_models():
    models = []
    for cat in CATEGORIES:
        cursor = None
        while True:
            params = {"category": cat, "status": "active", "limit": 100}
            if cursor:
                params["cursor"] = cursor
            page = get("/models", params)
            models += page["models"]
            cursor = page.get("next_cursor")
            if not page.get("has_more") or not cursor:
                break
    return models


def prices_for(ids):
    prices = {}
    for i in range(0, len(ids), 20):
        chunk = ids[i:i + 20]
        try:
            page = get("/models/pricing", [("endpoint_id", e) for e in chunk])
            prices.update({p["endpoint_id"]: p for p in page["prices"]})
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            for eid in chunk:
                try:
                    prices[eid] = get("/models/pricing", {"endpoint_id": eid})["prices"][0]
                except urllib.error.HTTPError:
                    pass
                time.sleep(0.5)
        time.sleep(1.5)
    return prices


def main():
    models = list_models()
    prices = prices_for([m["endpoint_id"] for m in models])
    rows = []
    for m in models:
        md, p = m["metadata"], prices.get(m["endpoint_id"], {})
        rows.append({
            "endpoint_id": m["endpoint_id"],
            "category": md.get("category"),
            "display_name": md.get("display_name"),
            "released": (md.get("date") or "")[:10],
            "unit_price": p.get("unit_price"),
            "unit": p.get("unit"),
            "currency": p.get("currency"),
            "tags": md.get("tags", []),
        })
    rows.sort(key=lambda r: (r["category"], r["unit_price"] if r["unit_price"] is not None else 1e9))
    out = pathlib.Path(__file__).resolve().parent.parent / "catalogue" / f"fal-{datetime.date.today()}.jsonl"
    out.parent.mkdir(exist_ok=True)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(f"{len(rows)} endpoints, {sum(r['unit_price'] is not None for r in rows)} priced -> {out}")


if __name__ == "__main__":
    main()
