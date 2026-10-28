# Tech-Graphics-Benchmark

> **Status: first informal round generated, awaiting annotation (2026-10-28).** Nine test prompts (six core, three in a Hebrew track), a 15-model longlist on fal, and one text-to-image round of 20 images in the private annotation Space.
>
> **Visibility:** repo public · prompts public · runs none · ratings private

Can an image generation model turn a technical explanation into a colourful, stylised diagram (anime, manga, bold flat colour) **without losing the meaning**: every label spelled exactly, every arrow where it was asked for?

Diagrams-as-code (Mermaid, Graphviz, PlantUML) are accurate, well tooled and dull. Generative image models can bring colour, style and personality to explaining a concept, but text rendering has long been their Achilles heel, and for an explainer diagram one wrong label is fatal. This is a deliberately lightweight, periodic check (one or two prompts per modality) to see which models currently get it right. Models change too fast for an exhaustive comparison to stay useful.

The winners here are not necessarily the most photorealistic or "best" image models. Text fidelity and instruction following are different skills, and a smaller model, a LoRA or a fine-tune can beat a frontier model on them.

## Test prompts

[![Hugging Face](https://img.shields.io/badge/HuggingFace-Dataset-yellow?logo=huggingface)](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark)

Nine prompts (six core: four text-to-image, two image-to-image; three in the Hebrew track): [huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark). The source of truth is [`data/prompts.jsonl`](data/prompts.jsonl), and [`data/README.md`](data/README.md) is the dataset card. Upload with:

```bash
hf upload danielrosehill/Tech-Graphics-Benchmark data . --repo-type dataset
```

| ID | Modality | What it tests |
|---|---|---|
| `tgb-t2i-01` | Text-to-image | Anime-style blog explainer of ASR fine-tuning for domain vocabulary across two models: 11 exact strings including WER figures, two panels, arrows |
| `tgb-t2i-02` | Text-to-image | Manga-style speech-to-text pipeline: box order, arrow directions, one arrow from a box below the row, a speech bubble with a deliberate tricky string |
| `tgb-t2i-03` | Text-to-image | Crayon banner for the Hebrish fine-tune post: Boxty (tech) and Jachnun (code-switching) with handwritten WERs, a box of example words, one arrow down to Sabich v2.2 and its WERs, a margin note. 15 exact strings |
| `tgb-t2i-04` | Text-to-image | Cover art for the same post from a descriptive prompt with **no exact strings**: passes text only if nothing garbled or invented appears |
| `tgb-i2i-01` | Image-to-image | Whiteboard photo → clean colour diagram, **keeping the handwriting** but making it legible; fix three named misspellings, nothing else |
| `tgb-i2i-02` | Image-to-image | Same whiteboard → anime infographic with handwriting **replaced by sans-serif type**; layout and arrows unchanged |
| `tgb-he-00` | Text-to-image, Hebrew | Screen: one box with פירגון and a label below. Gates the rest of the Hebrew track |
| `tgb-he-01` | Text-to-image, Hebrew | Hebrew-only mirror of `tgb-t2i-02`: right-to-left pipeline, left-pointing arrows, a percentage inside Hebrew text. 8 exact strings |
| `tgb-he-02` | Text-to-image, mixed | Hebrew and English in the same strings (`יש לי meeting ב-Zoom מחר`), each run keeping its own direction, Hebrew prefixes on English words. 8 exact strings |

Each record carries `track` (`hebrew` for the Hebrew track, absent for core), `expected_text` (every string that must appear, spelled exactly; empty for descriptive prompts), `structure_checks` (the arrow and layout instructions to verify) and optional `notes` (sources for any figures, grading caveats).

Most prompts are banner or hero images for blog posts: the realistic use. Two prompt shapes: **exact** (every label, number and arrow specified) and **descriptive** (what the image should convey, no strings), since cover art is usually asked for the second way.

## Mechanism

Two modalities, graded separately because they fail differently:

- **Text-to-image.** The model gets a written description of a diagram with exact label strings, numbers and arrow directions. The failure to look for is garbled, misspelt or invented text and arrows that point the wrong way or connect the wrong boxes.
- **Image-to-image.** The model gets a photo of a hand-drawn whiteboard or notepad sketch and is asked to restyle it: keep the handwriting but make it legible, or swap it for a clean font, add colour, straighten the perspective. The failure to look for is **text transposition errors**: labels the model drops, invents, rewords or "corrects" wrongly while restyling.

Style is part of the ask (anime, manga, flat colour) because the point is a diagram with personality. A correct but plain output passes the hard checks; the notes record whether it was any fun to look at.

## Hebrew track

A sub-benchmark for one capability most models still lack: Hebrew text in a diagram. The diagram asks are the same as the core prompts; the text is Hebrew, written right to left. `tgb-he-02` goes further and mixes Hebrew and English inside single strings, the way Hebrish is actually spoken and written, so each run has to keep its own direction and the sentence has to read in the right order.

Because most models fail outright ([Hebrew-Image-Generation-Eval](https://github.com/danielrosehill/Hebrew-Image-Generation-Eval), 2025-12: 2 of 12 models rendered two single words), the track is gated. Every panel model gets `tgb-he-00` (one word and one two-word label) once; only models that pass `text_exact` on it run `tgb-he-01` and `tgb-he-02`. Failing the screen is recorded as a result, not skipped.

Hebrew-specific errors to log in `text_errors`: reversed letter order, mirrored glyphs, a non-final letter at the end of a word (מ for ם), pseudo-Hebrew filler, digits flipped by bidi (`2.76%` → `6.72%`), and in mixed strings, English words reversed or the word order scrambled.

## Rounds

Informal micro-rounds every few months, not a full sweep: **3–5 cheap models × one or two prompts × two tries**, text-to-image unless a round says otherwise. Around 20 images and well under $1 per round; the point is a quick look at whether a newer, cheaper model now gets the text right.

1. **Refresh the model list.** `with-secrets uv run python scripts/fal_catalogue.py` snapshots every active fal text-to-image and image-to-image endpoint with its list price into `catalogue/fal-YYYY-MM-DD.jsonl` (577 endpoints on 2026-10-28). Diff against the previous snapshot to see what's new. Token-billed models (GPT Image, Nano Banana Lite, MAI) show a placeholder price of 1 unit or credit; the real cost is on `https://fal.ai/models/<endpoint_id>`.
2. **Longlist.** [`panels/2026-10.json`](panels/2026-10.json): 15 candidates from $0.005 to $0.08 per 1K image, each with its endpoints and where its price came from. Each round picks a few from it.
3. **Round config.** `configs/<run_id>.json`: prompts, models, model-specific `args` and a budget. Switch off prompt expansion wherever a model has it (`enable_prompt_expansion: false`), or the model rewrites the exact strings. Input schemas: `https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<id>`.
4. **Generate.** `with-secrets uv run python scripts/run_t2i.py configs/<run_id>.json` (`--dry-run` first for the count and cost). Writes `runs/<run_id>/manifest.jsonl` and `images/` (images are not in git), with opaque, shuffled `gen_id`s so the Space stays blind.
5. **Publish for annotation.** `hf upload danielrosehill/Tech-Graphics-Benchmark-Runs runs/<run_id> <run_id> --repo-type dataset --exclude spend.json`, then restart the Space.

The Hebrew track runs as its own round: `tgb-he-00` once per model, then `tgb-he-01` and `tgb-he-02` only for models that pass.

## Grading

Human, per generation, in the private annotation Space ([`space/`](space/)). The model name stays hidden until the annotation is saved.

| Field | Type | Meaning |
|---|---|---|
| `text_exact` | tick | Every `expected_text` string present and spelled exactly; no invented text. **The hard criterion** |
| `structure_ok` | tick | Every `structure_checks` item honoured: arrows, order, placement |
| `meaning_preserved` | tick | A reader would take the same meaning from it as from the brief or the original sketch |
| `text_errors` | text | Each error verbatim, `expected → got` |
| `notes` | text | Subjective: what I liked or disliked about the generation |

Per model and modality, report the share of generations passing `text_exact`, and the share passing all three ticks. The notes are quoted, not scored.

## Where things live

| What | Where |
|---|---|
| Design, prompts source, Space source, model panels, fal catalogue snapshots | this repo |
| Test prompts | HF dataset [`danielrosehill/Tech-Graphics-Benchmark`](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark) (public) |
| Generations | HF dataset `danielrosehill/Tech-Graphics-Benchmark-Runs` (public). Layout: `<run_id>/manifest.jsonl` + `<run_id>/images/<gen_id>.png` |
| Annotations | HF dataset `danielrosehill/Tech-Graphics-Benchmark-Ratings` (private), one file per generation at `annotations/<run_id>/<gen_id>.json` |
| Annotation app | HF Space `danielrosehill/Tech-Graphics-Benchmark-Annotate` (private, Gradio) |

A manifest row is `{"gen_id", "run_id", "prompt_id", "model", "endpoint", "provider", "attempt", "image", "seed", "created"}`, with `image` relative to the dataset root. Run IDs are `YYYY-MM-DD-<label>`.

The Space reads all three datasets at startup, so restart it after pushing a run. It needs the secret `HF_TOKEN` (write access to the ratings dataset); the repo IDs can be overridden with the variables `RUNS_REPO`, `PROMPTS_REPO` and `RATINGS_REPO`. Redeploy with `space/deploy.sh`.

## Results

| Run | Models | Prompts | Images | Cost | Status |
|---|---|---|---|---|---|
| `2026-10-28-informal` ([config](configs/2026-10-28-informal.json)) | FLUX.3 Klein, GPT Image 2.5 Flare (medium), Ideogram V4.5 (low), Qwen-Image 3, Nano Banana 2.1 (1K) | `tgb-t2i-01`, `tgb-t2i-02` | 20 (2 per model per prompt) | ~$0.52 (list prices) | Generated 2026-10-28, awaiting annotation |

## Open questions

- Whether to add a notepad sketch (pen on paper) as a second image-to-image input alongside the whiteboard.
- Whether to add a Hebrew image-to-image prompt (a whiteboard written in Hebrew) once some model passes the text-to-image Hebrew track.

## Origin

Daniel Rosehill, 2026-10-28, while writing a blog post explaining what an ASR fine-tune's evaluation showed about domain recognition across two models. Builds on the whiteboard-to-diagram work in [Nano-Banana-Tech-Diagram-Maker](https://github.com/danielrosehill/Nano-Banana-Tech-Diagram-Maker) and [Sample-Whiteboards](https://github.com/danielrosehill/Sample-Whiteboards).

## Related

- [Hebrew-Image-Generation-Eval](https://github.com/danielrosehill/Hebrew-Image-Generation-Eval): pass/fail Hebrew text rendering across twelve text-to-image models. Same text-fidelity question, for Hebrew rather than diagrams.
- [Tech-Diagram-Image-Gen-Prompts](https://github.com/danielrosehill/Tech-Diagram-Image-Gen-Prompts): the prompt library (28 styles, 33 diagram types) for actually making these diagrams.
- [Nano-Tech-Diagrams-MCP](https://github.com/danielrosehill/Nano-Tech-Diagrams-MCP): MCP server that generates them with Nano Banana 2.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
