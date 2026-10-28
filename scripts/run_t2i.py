"""Informal text-to-image round on fal: every prompt x model x N generations, saved for annotation.

Usage:
  with-secrets uv run python scripts/run_t2i.py configs/<run_id>.json           # generate
  with-secrets uv run python scripts/run_t2i.py configs/<run_id>.json --dry-run # plan and cost only

Writes runs/<run_id>/manifest.jsonl, images/<gen_id>.png and spend.json. Resumable: a gen_id
whose image already exists is skipped. gen_ids are opaque hashes and the manifest is shuffled,
so the annotation Space doesn't reveal the model before an annotation is saved.

Calls https://fal.run/<endpoint> (synchronous). Model-specific inputs go in the config's `args`;
switch off prompt expansion wherever a model has it, or the model rewrites the exact strings.
fal responses carry no cost, so spend is the config's usd_per_image (from the model page or
the pricing API) summed per success; the fal usage dashboard is the check. Each manifest row
records that price as usd_per_image, which the Space shows so value for money can be rated.
"""
import argparse
import hashlib
import json
import os
import pathlib
import random
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent


def call(endpoint, payload):
    req = urllib.request.Request(f"https://fal.run/{endpoint}", data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Key {os.environ['FAL_KEY']}",
                                          "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=600))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cfg = json.loads(pathlib.Path(a.config).read_text())
    prompts = {p["id"]: p for p in map(json.loads, (ROOT / "data/prompts.jsonl").read_text().splitlines())}
    n = cfg["generations_per_prompt"]
    jobs = [(prompts[pid], m, k) for pid in cfg["prompts"] for m in cfg["models"] for k in range(1, n + 1)]
    est = sum(m["usd_per_image"] for _, m, _ in jobs)
    print(f"{len(jobs)} images, estimated ${est:.2f} (budget ${cfg['budget_usd']:.2f})")
    if est > cfg["budget_usd"]:
        raise SystemExit("estimate over budget: cut models or prompts")
    if a.dry_run:
        return

    run = ROOT / "runs" / cfg["run_id"]
    (run / "images").mkdir(parents=True, exist_ok=True)
    mpath = run / "manifest.jsonl"
    rows = {r["gen_id"]: r for r in map(json.loads, mpath.read_text().splitlines())} if mpath.exists() else {}
    spend = 0.0
    for p, m, k in jobs:
        gen_id = hashlib.sha1(f"{cfg['run_id']}|{p['id']}|{m['endpoint']}|{k}".encode()).hexdigest()[:12]
        img = run / "images" / f"{gen_id}.png"
        if img.exists():
            continue
        try:
            out = call(m["endpoint"], {"prompt": p["prompt"], "num_images": 1, **m.get("args", {})})
            urllib.request.urlretrieve(out["images"][0]["url"], img)
        except Exception as e:
            print(f"FAIL {m['label']} {p['id']} #{k}: {e}")
            continue
        spend += m["usd_per_image"]
        rows[gen_id] = {"gen_id": gen_id, "run_id": cfg["run_id"], "prompt_id": p["id"], "model": m["label"],
                        "endpoint": m["endpoint"], "provider": "fal", "attempt": k,
                        "image": f"{cfg['run_id']}/images/{gen_id}.png", "seed": out.get("seed"),
                        "usd_per_image": m["usd_per_image"], "price_basis": m.get("price_basis", "list price"),
                        "created": __import__("datetime").datetime.now().isoformat(timespec="seconds")}
        print(f"ok   {m['label']} {p['id']} #{k} -> {gen_id}")
    order = list(rows.values())
    random.Random(cfg["run_id"]).shuffle(order)
    mpath.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in order))
    (run / "spend.json").write_text(json.dumps({"estimated_usd_this_invocation": round(spend, 4),
                                                "basis": "config usd_per_image x successful images"}, indent=2) + "\n")
    print(f"{len(order)} in manifest, ~${spend:.2f} this invocation")


if __name__ == "__main__":
    main()
