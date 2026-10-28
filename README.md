# Tech-Graphics-Benchmark

> **Status: second set of rounds generated, annotation under way (2026-10-28).** Eighteen test prompts (ten text-to-image, five image-to-image, three in a Hebrew track; five more retired), a 15-model longlist on fal, and four rounds in the private annotation Space.
>
> **Visibility:** repo public · prompts public · generations public · annotations public · annotation Space private

[![Prompts](https://img.shields.io/badge/HF%20dataset-prompts-yellow?logo=huggingface)](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark) [![Generations](https://img.shields.io/badge/HF%20dataset-generations-yellow?logo=huggingface)](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark-Runs) [![Annotations](https://img.shields.io/badge/HF%20dataset-annotations%20(raw%20eval%20data)-yellow?logo=huggingface)](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark-Ratings)

Can an image generation model make the graphics a tech repo or blog post actually uses (a photoreal banner with a sloth at a desk, a mascot in a real street scene, a neon title, a whiteboard sketch restyled as a chalkboard or comic page) **without losing the meaning**: every label spelled exactly, every arrow where it was asked for?

Diagrams-as-code (Mermaid, Graphviz, PlantUML) are accurate, well tooled and dull. Generative image models can bring colour, style and personality to explaining a concept, but text rendering has long been their Achilles heel, and for an explainer diagram one wrong label is fatal. This is a deliberately lightweight, periodic check (one or two prompts per modality) to see which models currently get it right. Models change too fast for an exhaustive comparison to stay useful.

The winners here are not necessarily the most photorealistic or "best" image models. Text fidelity and instruction following are different skills, and a smaller model, a LoRA or a fine-tune can beat a frontier model on them.

## Test prompts

[![Hugging Face](https://img.shields.io/badge/HuggingFace-Dataset-yellow?logo=huggingface)](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark)

Eighteen prompts (fifteen core: ten text-to-image, five image-to-image; three in the Hebrew track): [huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark). The source of truth is [`data/prompts.jsonl`](data/prompts.jsonl), and [`data/README.md`](data/README.md) is the dataset card. Retired prompts, with the reason, are in [`data/retired.jsonl`](data/retired.jsonl). Upload with:

```bash
hf upload danielrosehill/Tech-Graphics-Benchmark data . --repo-type dataset
```

| ID | Modality | What it tests |
|---|---|---|
| `tgb-t2i-03` | Text-to-image | Crayon banner for the Hebrish fine-tune post: Boxty (tech) and Jachnun (code-switching) with handwritten WERs, a box of example words, one arrow down to Sabich v2.2 and its WERs, a margin note. 15 exact strings |
| `tgb-t2i-05` | Text-to-image | Photoreal sloth sysadmin in a server closet: monitor progress text, a paper sign on the rack, a printed mug. 3 exact strings |
| `tgb-t2i-06` | Text-to-image | Photoreal sloth and capybara pair-programming; one terminal line on the laptop screen |
| `tgb-t2i-07` | Text-to-image | Blocky orange mascot at a Jerusalem bus stop; a two-row LED arrival board (row order, route, destination, minutes). 6 exact strings |
| `tgb-t2i-08` | Text-to-image | Neon README title banner: two lines with set colours, pixel sloth face above |
| `tgb-t2i-10` | Text-to-image | Editorial model-lineage diagram: one base, two rows of training ingredients, two coloured output badges. 11 strings |
| `tgb-t2i-11` | Text-to-image | Editorial share card: serif title, subtitle, STOCK vs FINE-TUNED rows, the stock row a deliberate mis-transcription that must not be "fixed" |
| `tgb-t2i-12` | Text-to-image | Information table: 4 columns × 3 rows of model names and WERs, header and highlighted row; every cell in its place. 18 strings |
| `tgb-t2i-13` | Text-to-image | Five-step numbered infographic, voice note → blog post: labels, captions, icons, right-pointing arrows |
| `tgb-t2i-14` | Text-to-image | Horizontal bar chart: five labelled bars in order, lengths proportional, values at bar ends, axis label |
| `tgb-i2i-01` | Image-to-image | Whiteboard photo → clean colour diagram, **keeping the handwriting** but making it legible; fix three named misspellings, nothing else |
| `tgb-i2i-03` | Image-to-image | Whiteboards #08 (Zoom-prep yes/no flowchart) → green chalkboard. 7 strings |
| `tgb-i2i-04` | Image-to-image | Whiteboards #11 (personalised-AI idea, bot interview → memory → vector DB) → sticky notes on cork. 16 strings |
| `tgb-i2i-05` | Image-to-image | Whiteboards #13 (user/bot dialogue workflow) → comic-book page with characters and speech bubbles, no sound-effect words. 11 strings |
| `tgb-i2i-06` | Image-to-image | Whiteboards #21 (whiteboard → dev spec pipeline) → neon tubes on brick. 15 strings |
| `tgb-he-00` | Text-to-image, Hebrew | Screen: one box with פירגון and a label below. Gates the rest of the Hebrew track |
| `tgb-he-01` | Text-to-image, Hebrew | Hebrew-only mirror of `tgb-t2i-02`: right-to-left pipeline, left-pointing arrows, a percentage inside Hebrew text. 8 exact strings |
| `tgb-he-02` | Text-to-image, mixed | Hebrew and English in the same strings (`יש לי meeting ב-Zoom מחר`), each run keeping its own direction, Hebrew prefixes on English words. 8 exact strings |

Each record carries `track` (`hebrew` for the Hebrew track, absent for core), `expected_text` (every string that must appear, spelled exactly; empty for descriptive prompts), `validation` (which validation ticks apply), `structure_checks` (the arrow and layout instructions to verify) and optional `notes` (sources for any figures, grading caveats).

Two families of text-to-image prompt, both modelled on graphics the author actually publishes. **Banners** (`tgb-t2i-03`, `-05` to `-08`): repo and post hero images, modelled on ones the author has actually used (sloth blog heroes in Personal-Site-Blog, the Claude plugin banners): the realistic use. The image-to-image inputs are boards from [danielrosehill/Whiteboards](https://huggingface.co/datasets/danielrosehill/Whiteboards), whose human transcriptions give the exact strings. **Informational graphics** (`tgb-t2i-10` to `-14`): the lineage diagrams, share cards, tables, step infographics and charts on [blog.danielrosehill.com](https://blog.danielrosehill.com), in its calm editorial style (cream background, teal, amber and slate). Every prompt asks for some exact text, so every one can be validated; the styles come from the [Sample-Whiteboards](https://github.com/danielrosehill/Sample-Whiteboards) prompt library, each with a no-added-text rule appended. Two prompt shapes: **exact** (every label, number and arrow specified) and **descriptive** (what the image should convey, no strings), since cover art is usually asked for the second way.

## Mechanism

Two modalities, graded separately because they fail differently:

- **Text-to-image.** The model gets a written description of a diagram with exact label strings, numbers and arrow directions. The failure to look for is garbled, misspelt or invented text and arrows that point the wrong way or connect the wrong boxes.
- **Image-to-image.** The model gets a photo of a hand-drawn whiteboard or notepad sketch and is asked to restyle it: keep the handwriting but make it legible, or swap it for a clean font, add colour, straighten the perspective. The failure to look for is **text transposition errors**: labels the model drops, invents, rewords or "corrects" wrongly while restyling.

Style is part of the ask (photoreal, crayon, neon, chalkboard, comic) because the point is a graphic with personality. A correct but plain output passes the hard checks; the notes record whether it was any fun to look at.

### Retired prompts

`tgb-t2i-01` (anime ASR explainer), `tgb-t2i-02` (manga STT pipeline) and `tgb-i2i-02` (whiteboard → anime infographic) were retired on 2026-10-28: anime and manga are not styles the author would use for a repo or post. Both annotations saved from the first round were on these prompts and scored `rating_overall` 2/10 while passing every validation tick ("looks like something you'd hang up in a kindergarten instead of put on a tech blog"), so text fidelity alone didn't make them usable. The records are in `data/retired.jsonl`; the annotations stay in the ratings dataset; the Space no longer queues the 18 unannotated generations from them. `tgb-t2i-04` (cover art) and `tgb-t2i-09` (sloth with a GPU rig) followed later the same day: descriptive prompts asking for no text, title or diagram give nothing to validate, so they don't belong here. The Hebrew prompts `tgb-he-01` and `tgb-he-02` had anime and manga style asks too and were restyled to flat colour with a cartoon robot mascot instead, since what they test is the Hebrew text.

## Hebrew track

A sub-benchmark for one capability most models still lack: Hebrew text in a diagram. The diagram asks are the same as the core prompts; the text is Hebrew, written right to left. `tgb-he-02` goes further and mixes Hebrew and English inside single strings, the way Hebrish is actually spoken and written, so each run has to keep its own direction and the sentence has to read in the right order.

Because most models fail outright ([Hebrew-Image-Generation-Eval](https://github.com/danielrosehill/Hebrew-Image-Generation-Eval), 2025-12: 2 of 12 models rendered two single words), the track is gated. Every panel model gets `tgb-he-00` (one word and one two-word label) once; only models that pass `text_exact` on it run `tgb-he-01` and `tgb-he-02`. Failing the screen is recorded as a result, not skipped.

Hebrew-specific errors to log in `text_errors`: reversed letter order, mirrored glyphs, a non-final letter at the end of a word (מ for ם), pseudo-Hebrew filler, digits flipped by bidi (`2.76%` → `6.72%`), and in mixed strings, English words reversed or the word order scrambled.

## Rounds

Informal micro-rounds every few months, not a full sweep: **3–5 cheap models × a few prompts × one or two tries**, one modality per round. Around 20 images and well under $1 per round; the point is a quick look at whether a newer, cheaper model now gets the text right.

1. **Refresh the model list.** `with-secrets uv run python scripts/fal_catalogue.py` snapshots every active fal text-to-image and image-to-image endpoint with its list price into `catalogue/fal-YYYY-MM-DD.jsonl` (577 endpoints on 2026-10-28). Diff against the previous snapshot to see what's new. Token-billed models (GPT Image, Nano Banana Lite, MAI) show a placeholder price of 1 unit or credit; the real cost is on `https://fal.ai/models/<endpoint_id>`.
2. **Longlist.** [`panels/2026-10.json`](panels/2026-10.json): 15 candidates from $0.005 to $0.08 per 1K image, each with its endpoints and where its price came from. Each round picks a few from it.
3. **Round config.** `configs/<run_id>.json`: prompts, models, model-specific `args` and a budget. Switch off prompt expansion wherever a model has it (`enable_prompt_expansion: false`), or the model rewrites the exact strings. Input schemas: `https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<id>`.
4. **Generate.** `with-secrets uv run python scripts/run_round.py configs/<run_id>.json` (`--dry-run` first for the count and cost). For image-to-image, the config's models are edit endpoints and `input_base_url` points at the prompts dataset (`https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark/resolve/main/`), so upload `data/` before running; each input goes in `image_urls` (override per model with `image_param`, e.g. `image_url` for Ideogram edit). Writes `runs/<run_id>/manifest.jsonl` and `images/` (images are not in git), with opaque, shuffled `gen_id`s so the Space stays blind.
5. **Publish for annotation.** `hf upload danielrosehill/Tech-Graphics-Benchmark-Runs runs/<run_id> <run_id> --repo-type dataset --exclude spend.json`, then restart the Space.

The Hebrew track runs as its own round: `tgb-he-00` once per model, then `tgb-he-01` and `tgb-he-02` only for models that pass.

## Grading

Human, per generation, in the private annotation Space ([`space/`](space/)); the saved annotations are public. The model name stays hidden until the annotation is saved. The per-image cost and size are shown up front, because value for money can't be rated without it; on a small panel the price can hint at the model, which is accepted.

The form has four sections, in this order.

**1. Validation** (hard, pass/fail; only the ticks in the prompt's `validation` list)

A tick is only asked where the prompt gives it something to check: diagram prompts get all four, banners with exact strings but no diagram get the two text ticks, and a prompt with no text, title or diagram would get none (none are active: such prompts are retired rather than rated). Ticks that don't apply are hidden in the Space and saved as `null` (not applicable), never as a fail.

| Field | Type | Meaning |
|---|---|---|
| `text_exact` | tick | Every `expected_text` string present and spelled exactly; no invented text. **The hard criterion** |
| `text_legible` | tick | All text readable at a glance at blog-post size: no smudged, warped or cramped lettering |
| `structure_ok` | tick | Every `structure_checks` item honoured: arrows, order, placement |
| `meaning_preserved` | tick | A reader would take the same meaning from it as from the brief or the original sketch |

**2. Comments**

| Field | Type | Meaning |
|---|---|---|
| `text_errors` | text | Each error verbatim, `expected → got` |
| `notes` | text | Subjective: what I liked or disliked about the generation |

**3. Ratings** (1–10, optional each; `null` when skipped)

| Field | Meaning |
|---|---|
| `rating_style` | Delivers the asked-for look (photoreal, crayon, neon, chalkboard, comic) and is fun to look at |
| `rating_overall` | Would I publish it as the post's banner or explainer, as is |
| `rating_value` | Value for money: the image judged against its `usd_per_image` |

**4. Notes on the annotation process** (for Claude)

A free-text box for notes about the rubric rather than the image: a criterion to add, one to change, something that couldn't be graded with the fields available. Saved with the annotation as `process_notes`, or on its own with **Save process note only** as `process-notes/<timestamp>.json` in the ratings dataset (with the `run_id`, `gen_id` and `prompt_id` on screen). They are not scored. When the rubric is next revised, read every non-empty `process_notes` and every `process-notes/*.json`, apply them to the form, this section and `cards/ratings.md`, and say which notes each change answers.

Each annotation also stores the generation's `width`, `height` and `usd_per_image` (list price from the round config, recorded per manifest row by `scripts/run_round.py`).

**Scoring**, per model and modality:

- **Pass rates:** share of generations passing `text_exact`, and share passing every applicable tick, each over the generations where the tick applies (`null` is left out of the denominator; ratings-only prompts don't count). These rank the models; ratings break ties and explain.
- **Mean ratings:** mean of each `rating_*` over the rated generations, with n.
- **Cost per usable image:** `usd_per_image ÷ share passing every applicable tick` (∞ when none pass). The objective counterpart to `rating_value`.

The notes are quoted, not scored.

## Where things live

| What | Where |
|---|---|
| Design, prompts source, Space source, model panels, fal catalogue snapshots | this repo |
| Test prompts | HF dataset [`danielrosehill/Tech-Graphics-Benchmark`](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark) (public) |
| Generations | HF dataset [`danielrosehill/Tech-Graphics-Benchmark-Runs`](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark-Runs) (public). Layout: `<run_id>/manifest.jsonl` + `<run_id>/images/<gen_id>.png` |
| Annotations (raw eval data) | HF dataset [`danielrosehill/Tech-Graphics-Benchmark-Ratings`](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark-Ratings) (public since 2026-10-28), one file per generation at `annotations/<run_id>/<gen_id>.json` |
| Dataset cards for the two HF datasets above | [`cards/runs.md`](cards/runs.md), [`cards/ratings.md`](cards/ratings.md); upload each as `README.md` to its dataset |
| Annotation app | HF Space [`danielrosehill/Tech-Graphics-Benchmark-Annotate`](https://huggingface.co/spaces/danielrosehill/Tech-Graphics-Benchmark-Annotate) (private, Gradio) |

A manifest row is `{"gen_id", "run_id", "prompt_id", "model", "endpoint", "provider", "attempt", "image", "seed", "created", "requested_size", "width", "height", "usd_per_image", "price_basis"}`, with `image` relative to the dataset root. `requested_size` is what the config asked for (`image_size`, or `aspect_ratio` + `resolution`); `width`/`height` are what came back, read from the PNG. Models given the same request deliver different sizes (2026-10-28: 1024×768, 1152×864, 1200×896), so the Space shows both. `usd_per_image` is the config's list price (backfilled, with the sizes, into `2026-10-28-informal` on 2026-10-28); runs without it show "cost not recorded" in the Space. Run IDs are `YYYY-MM-DD-<label>`.

The Space reads all three datasets at startup, so restart it after pushing a run. Saving is instant: the annotation is queued and a background thread commits everything pending in one commit (an HF commit took ~30 s on 2026-10-28, which made each save hang). The save message shows how many are still uploading; don't restart or redeploy the Space while that's non-zero, or the queued files are lost. Images are displayed from full-resolution JPEG copies (quality 92, ~7× smaller than the PNGs) made at startup. It needs the secret `HF_TOKEN` (write access to the ratings dataset); the repo IDs can be overridden with the variables `RUNS_REPO`, `PROMPTS_REPO` and `RATINGS_REPO`. Redeploy with `space/deploy.sh`.

## Results

| Run | Models | Prompts | Images | Cost | Status |
|---|---|---|---|---|---|
| `2026-10-28-informal` ([config](configs/2026-10-28-informal.json)) | FLUX.3 Klein, GPT Image 2.5 Flare (medium), Ideogram V4.5 (low), Qwen-Image 3, Nano Banana 2.1 (1K) | `tgb-t2i-01`, `tgb-t2i-02` | 20 (2 per model per prompt) | ~$0.52 (list prices) | Prompts retired 2026-10-28 after 2 annotations; the other 18 dropped from the Space queue |
| `2026-10-28-banners` ([config](configs/2026-10-28-banners.json)) | same five, 16:9 | `tgb-t2i-05` to `tgb-t2i-09` | 25 (1 per model per prompt) | ~$0.66 (list prices) | Annotation under way; `tgb-t2i-09` retired mid-round, its 4 unannotated images dropped from the queue |
| `2026-10-28-informational` ([config](configs/2026-10-28-informational.json)) | same five as banners, 16:9 | `tgb-t2i-10` to `tgb-t2i-14` | 25 (1 per model per prompt) | ~$0.66 (list prices) | Generated 2026-10-28, awaiting annotation |
| `2026-10-28-whiteboards` ([config](configs/2026-10-28-whiteboards.json)) | edit endpoints: FLUX.3 Klein, GPT Image 2.5 Flare (medium), Seedream 5 Flash, Qwen-Image 3, Nano Banana 2.1 (1K) | `tgb-i2i-01`, `tgb-i2i-03` to `tgb-i2i-06` | 25 (1 per model per prompt) | ~$0.67 (list prices; GPT edit estimated) | Generated 2026-10-28, awaiting annotation |

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
