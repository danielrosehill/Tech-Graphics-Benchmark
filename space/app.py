"""Annotation Space for Tech-Graphics-Benchmark.

Reads generations from the public runs dataset, shows each one next to its prompt
(and input image for image-to-image), and writes one JSON file per annotated
generation to the private ratings dataset. The model name stays hidden until the
annotation is saved; the per-image cost (manifest `usd_per_image`) and size are shown up front so value for
money can be rated.

Process notes are notes for Claude about the annotation process itself, not about the image: a criterion
the form lacks, something that couldn't be graded, a change to make to the rubric. They are saved in the
annotation record as `process_notes`, or on their own (no annotation needed) as
process-notes/<timestamp>.json with the generation they were written against.

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
from huggingface_hub.constants import HF_HUB_CACHE

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

    # Prompts moved to retired.jsonl leave prompts.jsonl: their unannotated generations are dropped
    # from the queue; annotated ones stay viewable, shown with their retired record.
    rf = prompts_dir / "retired.jsonl"
    if rf.exists():
        for line in rf.read_text().splitlines():
            if line.strip():
                p = json.loads(line)
                prompts.setdefault(p["id"], p)
    gens = [g for g in gens if not prompts.get(g["prompt_id"], {}).get("retired")
            or (g["run_id"], g["gen_id"]) in done]

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


RATINGS = [
    ("rating_style", "Style: the asked-for look, fun to look at"),
    ("rating_overall", "Overall: would I publish it?"),
    ("rating_value", "Value for money, given the cost"),
]
SCALE = [str(n) for n in range(1, 11)]


def cost_line(g):
    usd = g.get("usd_per_image")
    cost = (f"**Cost:** ~${usd:.3f} per image ({g.get('price_basis', 'list price')})" if usd is not None
            else "**Cost:** not recorded for this run")
    if g.get("width"):
        size = f"**Size:** {g['width']} × {g['height']} px ({g['width'] * g['height'] / 1e6:.2f} MP)"
        if g.get("requested_size"):
            size += f", requested `{g['requested_size']}`"
    else:
        size = "**Size:** not recorded for this run"
    return f"{cost} · {size}"


def show(i):
    blank_ratings = [None] * len(RATINGS)
    if not GENS:
        empty = "No generations yet. Push a run to the runs dataset, then restart the Space."
        return (None, gr.update(value=None, visible=False), empty, "", "", False, False, False, False,
                *blank_ratings, "", "", "", gr.update())
    i = int(i)
    g = GENS[i]
    p = PROMPTS.get(g["prompt_id"], {})
    input_img = str(PROMPTS_DIR / p["input_image"]) if p.get("input_image") else None
    expected = "\n".join(f"- `{t}`" for t in p.get("expected_text", [])) or "- (none: any garbled or invented text fails)"
    checks = "\n".join(f"- {c}" for c in p.get("structure_checks", []))
    info = (f"### Prompt · {g['prompt_id']} · {p.get('modality', '?')} · {p.get('style', '?')}\n\n"
            f"{p.get('prompt', '(prompt not found)')}\n\n"
            f"<details><summary><b>Expected text</b></summary>\n\n{expected}\n\n</details>\n\n"
            f"<details><summary><b>Structure checks</b></summary>\n\n{checks}\n\n</details>")
    a = DONE.get((g["run_id"], g["gen_id"]))
    reveal = f"Model: **{g['model']}**" if a else "Model hidden until saved."
    in_upd = gr.update(value=input_img, visible=bool(input_img))
    if a:
        ratings = [str(a[k]) if a.get(k) else None for k, _ in RATINGS]
        return (g["_image_path"], in_upd, info, cost_line(g), reveal, a["text_exact"], a.get("text_legible", False),
                a["structure_ok"], a["meaning_preserved"], *ratings, a["text_errors"], a["notes"],
                a.get("process_notes", ""), gr.update())
    return (g["_image_path"], in_upd, info, cost_line(g), reveal, False, False, False, False,
            *blank_ratings, "", "", "", gr.update())


def save(i, text_exact, text_legible, structure_ok, meaning_preserved, *rest):
    if not GENS:
        return "Nothing to save.", gr.update()
    *ratings, text_errors, notes, process_notes = rest
    i = int(i)
    g = GENS[i]
    rec = {
        "run_id": g["run_id"], "gen_id": g["gen_id"], "prompt_id": g["prompt_id"], "model": g["model"],
        "usd_per_image": g.get("usd_per_image"), "width": g.get("width"), "height": g.get("height"),
        "text_exact": bool(text_exact), "text_legible": bool(text_legible), "structure_ok": bool(structure_ok),
        "meaning_preserved": bool(meaning_preserved),
        **{k: int(r) if r else None for (k, _), r in zip(RATINGS, ratings)},
        "text_errors": text_errors.strip(), "notes": notes.strip(), "process_notes": process_notes.strip(),
        "annotated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    api.upload_file(
        path_or_fileobj=json.dumps(rec, ensure_ascii=False, indent=2).encode(),
        path_in_repo=f"annotations/{g['run_id']}/{g['gen_id']}.json",
        repo_id=RATINGS_REPO, repo_type="dataset",
        commit_message=f"Annotate {g['run_id']}/{g['gen_id']}",
    )
    DONE[(g["run_id"], g["gen_id"])] = rec
    nxt = next((k for k in list(range(i + 1, len(GENS))) + list(range(i))
                if (GENS[k]["run_id"], GENS[k]["gen_id"]) not in DONE), i)
    choices = [(label(k), k) for k in range(len(GENS))]
    msg = f"Saved #{i + 1}: that was **{g['model']}**." + ("" if nxt != i else " All generations annotated.")
    return msg, gr.update(choices=choices, value=nxt)


def save_process_note(i, process_notes):
    text = process_notes.strip()
    if not text:
        return "Process note is empty."
    g = GENS[int(i)] if GENS else {}
    now = datetime.now(timezone.utc)
    rec = {"note": text, "run_id": g.get("run_id"), "gen_id": g.get("gen_id"), "prompt_id": g.get("prompt_id"),
           "written_at": now.isoformat(timespec="seconds")}
    api.upload_file(
        path_or_fileobj=json.dumps(rec, ensure_ascii=False, indent=2).encode(),
        path_in_repo=f"process-notes/{now.strftime('%Y%m%dT%H%M%S')}.json",
        repo_id=RATINGS_REPO, repo_type="dataset", commit_message="Process note",
    )
    return "Process note saved (no annotation saved)."


def step(i, delta):
    if not GENS:
        return 0
    return (int(i) + delta) % len(GENS)


CSS = """
.rating .wrap { flex-wrap: wrap !important; gap: 3px !important; overflow: visible !important; }
.rating input[type=radio] { display: none !important; }
.rating label { min-width: 30px !important; padding: 5px 0 !important; justify-content: center !important; }
.rating label.selected { background: #f59e0b !important; color: white !important; font-weight: 700; }
#gen-img img { width: auto !important; height: auto !important; max-width: 100% !important;
               max-height: 100% !important; margin: auto; border: 1px solid #9ca3af !important; }
"""

with gr.Blocks(title="Tech Graphics Benchmark: annotate") as demo:
    gr.Markdown("# Tech Graphics Benchmark: annotate\n"
                "Validate, comment, rate. Saving reveals the model and moves to the next unrated generation.")
    with gr.Row():
        prev_b = gr.Button("← Prev", scale=0)
        picker = gr.Dropdown(choices=[(label(k), k) for k in range(len(GENS))],
                             value=first_unrated() if GENS else None, show_label=False, scale=4)
        next_b = gr.Button("Next →", scale=0)
    with gr.Row():
        with gr.Column(scale=3):
            out_img = gr.Image(label="Generated", type="filepath", height=620, elem_id="gen-img")
            cost = gr.Markdown()
            info = gr.Markdown()
            in_img = gr.Image(label="Input image", type="filepath", height=300, visible=False)
        with gr.Column(scale=2):
            with gr.Group():
                gr.Markdown("### 1. Validation")
                text_exact = gr.Checkbox(label="Text exactly right: no misspelt, missing or invented text")
                text_legible = gr.Checkbox(label="Text legible at a glance")
                structure_ok = gr.Checkbox(label="Arrows and layout instructions followed")
                meaning_preserved = gr.Checkbox(label="Meaning of the diagram preserved")
            with gr.Group():
                gr.Markdown("### 2. Comments")
                text_errors = gr.Textbox(label="Text errors, one per line: expected → got", lines=3)
                notes = gr.Textbox(label="Notes: what you liked or disliked", lines=3)
            with gr.Group():
                gr.Markdown("### 3. Ratings (1–10)")
                rating_inputs = [gr.Radio(SCALE, label=lbl, elem_classes="rating") for _, lbl in RATINGS]
            with gr.Group():
                gr.Markdown("### 4. Notes on the annotation process (for Claude)")
                process_notes = gr.Textbox(
                    label="Criteria to add or change, things you couldn't grade with this form", lines=3)
                note_b = gr.Button("Save process note only", size="sm")
            save_b = gr.Button("Save and next", variant="primary")
            status = gr.Markdown()
            reveal = gr.Markdown()

    outputs = [out_img, in_img, info, cost, reveal, text_exact, text_legible, structure_ok, meaning_preserved,
               *rating_inputs, text_errors, notes, process_notes, picker]
    picker.change(show, picker, outputs)
    demo.load(show, picker, outputs)
    prev_b.click(lambda i: step(i, -1), picker, picker)
    next_b.click(lambda i: step(i, 1), picker, picker)
    save_b.click(save, [picker, text_exact, text_legible, structure_ok, meaning_preserved, *rating_inputs, text_errors, notes,
                        process_notes], [status, picker])
    note_b.click(save_process_note, [picker, process_notes], status)

if __name__ == "__main__":
    # Images live in the HF hub cache (snapshot_download), which Gradio won't serve unless allowed.
    demo.launch(allowed_paths=[HF_HUB_CACHE], css=CSS)
