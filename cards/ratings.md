---
license: cc-by-4.0
pretty_name: Tech Graphics Benchmark (annotations)
tags:
- diagrams
- text-rendering
- benchmark
- human-evaluation
---

# Tech Graphics Benchmark: annotations

Raw human evaluation data for [Tech-Graphics-Benchmark](https://github.com/danielrosehill/Tech-Graphics-Benchmark): one JSON file per annotated generation, written by the annotation Space. The model was hidden from the annotator until the file was saved; cost and size were shown.

- Prompts: [danielrosehill/Tech-Graphics-Benchmark](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark)
- Generations (images + manifests): [danielrosehill/Tech-Graphics-Benchmark-Runs](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark-Runs)

Layout: `annotations/<run_id>/<gen_id>.json`. `gen_id` matches a row in the runs dataset's `<run_id>/manifest.jsonl`.

| Field | Type | Meaning |
|---|---|---|
| `run_id`, `gen_id`, `prompt_id`, `model` | string | Which generation |
| `usd_per_image` | number | List price of the generation (USD) |
| `width`, `height` | int | Delivered image size in pixels |
| `text_exact` | bool | Every expected string present and spelled exactly; no invented text |
| `text_legible` | bool | All text readable at a glance |
| `structure_ok` | bool | Arrow, order and placement instructions honoured |
| `meaning_preserved` | bool | Same meaning as the brief or the original sketch |
| `rating_style`, `rating_overall`, `rating_value` | int 1–10 or null | Style, would-publish, value for money |
| `text_errors` | string | One error per line, `expected → got` |
| `notes` | string | Free-text comments |
| `process_notes` | string | Notes about the annotation process, not the image: criteria to add or change, things the form couldn't capture. Absent before 2026-10-28 |
| `annotated_at` | ISO 8601 UTC | When saved |

`process-notes/<YYYYMMDDTHHMMSS>.json` holds process notes saved without an annotation: `{note, run_id, gen_id, prompt_id, written_at}`, the generation being the one on screen when it was written.

Annotations saved before 2026-10-28's form change may lack `text_legible`, `width` and `height`. Grading and scoring: [README § Grading](https://github.com/danielrosehill/Tech-Graphics-Benchmark#grading).
