"""Annotation Space for Tech-Graphics-Benchmark.

Reads generations from the public runs dataset, shows each one next to its prompt
(and input image for image-to-image), and writes one JSON file per annotated
generation to the private ratings dataset. The model name stays hidden until the
annotation is saved.

Env (Space secrets/variables):
  HF_TOKEN      write access to RATINGS_REPO
  RUNS_REPO     default danielrosehill/Tech-Graphics-Benchmark-Runs
  PROMPTS_REPO  default danielrosehill/Tech-Graphics-Benchmark
  RATINGS_REPO  default danielrosehill/Tech-Graphics-Benchmark-Ratings
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import gradio as gr
from huggingface_hub import HfApi, snapshot_download

TOKEN = os.environ.get("HF_TOKEN")
RUNS_REPO = os.environ.get("RUNS_REPO", "danielrosehill/Tech-Graphics-Benchmark-Runs")
PROMPTS_REPO = os.environ.get("PROMPTS_REPO", "danielrosehill/Tech-Graphics-Benchmark")
RATINGS_REPO = os.environ.get("RATINGS_REPO", "danielrosehill/Tech-Graphics-Benchmark-Ratings")

api = HfApi(token=TOKEN)


def load_all():
    prompts_dir = Path(snapshot_download(PROMPTS_REPO, repo_type="dataset", token=TOKEN))
    runs_dir = Path(snapshot_download(RUNS_REPO, repo_type="dataset", token=TOKEN))
    ratings_dir = Path(snapshot_download(RATINGS_REPO, repo_type="dataset", token=TOKEN))

    prompts = {}
    pf = prompts_dir / "prompts.jsonl"
    if pf.exists():
        for line in pf.read_text().splitlines():
            if line.strip():
                p = json.loads(line)
                prompts[p["id"]] = p

    gens = []
    for manifest in sorted(runs_dir.glob("*/manifest.jsonl")):
        for line in manifest.read_text().splitlines():
            if line.strip():
                g = json.loads(line)
                g["_image_path"] = str(runs_dir / g["image"])
                gens.append(g)

    done = {}
    for f in ratings_dir.glob("annotations/*/*.json"):
        a = json.loads(f.read_text())
        done[(a["run_id"], a["gen_id"])] = a

    return prompts_dir, prompts, gens, done


PROMPTS_DIR, PROMPTS, GENS, DONE = load_all()


def label(i):
    g = GENS[i]
    tick = "✓" if (g["run_id"], g["gen_id"]) in DONE else "·"
    return f"{tick} {g['run_id']} / {g['prompt_id']} / #{i + 1}"


def first_unrated():
    for i, g in enumerate(GENS):
        if (g["run_id"], g["gen_id"]) not in DONE:
            return i
    return 0


def show(i):
    if not GENS:
        empty = "No generations yet. Push a run to the runs dataset, then restart the Space."
        return (None, None, empty, "", False, "", False, False, "", "", gr.update())
    i = int(i)
    g = GENS[i]
    p = PROMPTS.get(g["prompt_id"], {})
    input_img = str(PROMPTS_DIR / p["input_image"]) if p.get("input_image") else None
    expected = "\n".join(f"- {t}" for t in p.get("expected_text", []))
    checks = "\n".join(f"- {c}" for c in p.get("structure_checks", []))
    info = (f"**{g['prompt_id']}** · {p.get('modality', '?')} · style: {p.get('style', '?')}\n\n"
            f"{p.get('prompt', '(prompt not found)')}\n\n**Expected text**\n{expected}\n\n**Structure checks**\n{checks}")
    a = DONE.get((g["run_id"], g["gen_id"]))
    reveal = f"Model: **{g['model']}**" if a else "Model hidden until saved."
    if a:
        return (g["_image_path"], input_img, info, reveal, a["text_exact"], a["text_errors"],
                a["structure_ok"], a["meaning_preserved"], a["notes"], "", gr.update())
    return (g["_image_path"], input_img, info, reveal, False, "", False, False, "", "", gr.update())


def save(i, text_exact, text_errors, structure_ok, meaning_preserved, notes):
    if not GENS:
        return "Nothing to save.", gr.update(), ""
    i = int(i)
    g = GENS[i]
    rec = {
        "run_id": g["run_id"], "gen_id": g["gen_id"], "prompt_id": g["prompt_id"], "model": g["model"],
        "text_exact": bool(text_exact), "text_errors": text_errors.strip(),
        "structure_ok": bool(structure_ok), "meaning_preserved": bool(meaning_preserved),
        "notes": notes.strip(), "annotated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    api.upload_file(
        path_or_fileobj=json.dumps(rec, ensure_ascii=False, indent=2).encode(),
        path_in_repo=f"annotations/{g['run_id']}/{g['gen_id']}.json",
        repo_id=RATINGS_REPO, repo_type="dataset",
        commit_message=f"Annotate {g['run_id']}/{g['gen_id']}",
    )
    DONE[(g["run_id"], g["gen_id"])] = rec
    choices = [(label(k), k) for k in range(len(GENS))]
    return f"Saved. Model: **{g['model']}**", gr.update(choices=choices, value=i), ""


def step(i, delta):
    if not GENS:
        return 0
    return (int(i) + delta) % len(GENS)


with gr.Blocks(title="Tech Graphics Benchmark: annotate") as demo:
    gr.Markdown("# Tech Graphics Benchmark: annotate\nTick what holds, list text errors verbatim, add your notes.")
    picker = gr.Dropdown(choices=[(label(k), k) for k in range(len(GENS))],
                         value=first_unrated() if GENS else None, label="Generation")
    with gr.Row():
        out_img = gr.Image(label="Generated", type="filepath", height=640)
        with gr.Column():
            in_img = gr.Image(label="Input (image-to-image only)", type="filepath", height=300)
            info = gr.Markdown()
    reveal = gr.Markdown()
    with gr.Row():
        text_exact = gr.Checkbox(label="Text exactly right (no misspelt, missing or invented text)")
        structure_ok = gr.Checkbox(label="Arrows / layout instructions followed")
        meaning_preserved = gr.Checkbox(label="Meaning of the diagram preserved")
    text_errors = gr.Textbox(label="Text errors (one per line: expected → got)", lines=3)
    notes = gr.Textbox(label="Notes: what you liked or disliked", lines=4)
    with gr.Row():
        prev_b = gr.Button("← Prev")
        save_b = gr.Button("Save", variant="primary")
        next_b = gr.Button("Next →")
    status = gr.Markdown()

    outputs = [out_img, in_img, info, reveal, text_exact, text_errors, structure_ok, meaning_preserved, notes, status, picker]
    picker.change(show, picker, outputs)
    demo.load(show, picker, outputs)
    prev_b.click(lambda i: step(i, -1), picker, picker)
    next_b.click(lambda i: step(i, 1), picker, picker)
    save_b.click(save, [picker, text_exact, text_errors, structure_ok, meaning_preserved, notes], [reveal, picker, status])

if __name__ == "__main__":
    demo.launch()
