---
license: cc-by-4.0
pretty_name: Tech Graphics Benchmark (test prompts)
task_categories:
- text-to-image
- image-to-image
tags:
- diagrams
- text-rendering
- benchmark
---

# Tech Graphics Benchmark: test prompts

Test prompts for [Tech-Graphics-Benchmark](https://github.com/danielrosehill/Tech-Graphics-Benchmark): can an image model make a characterful banner or a restyled diagram for a tech repo or blog post without getting the text or the arrows wrong?

`prompts.jsonl`, one record per prompt:

| Field | Meaning |
|---|---|
| `id` | `tgb-t2i-NN` (text-to-image), `tgb-i2i-NN` (image-to-image) or `tgb-he-NN` (Hebrew track) |
| `modality` | `text-to-image` or `image-to-image` |
| `track` | `hebrew` for the Hebrew track (Hebrew and mixed Hebrew/English text; `tgb-he-00` is a screen that gates the other two). Absent for core prompts |
| `style` | The visual style asked for |
| `prompt` | Exact text sent to the model |
| `input_image` | Path under `inputs/` for image-to-image, else `null` |
| `expected_text` | Every string that must appear, spelled exactly. Pass/fail ground truth. Empty for descriptive prompts, where any garbled or invented text fails |
| `validation` | Which validation ticks apply: any of `text_exact`, `text_legible`, `structure_ok`, `meaning_preserved`. Diagram prompts get all four; banners with exact strings but no diagram get the two text ticks; descriptive prompts with no text, title or diagram get none (ratings only). Added 2026-10-28 |
| `structure_checks` | Arrow, layout and content instructions the grader checks |
| `notes` | Optional: sources for figures in the prompt, grading caveats |

`inputs/whiteboards-08.jpg`, `-11`, `-13` and `-21` are samples 08, 11, 13 and 21 of [danielrosehill/Whiteboards](https://huggingface.co/datasets/danielrosehill/Whiteboards) (4096×3072 WebP, converted to 2048×1536 JPEG); their `expected_text` comes from that dataset's human transcriptions. Image-to-image rounds send them to the model by this dataset's `resolve/main/inputs/...` URL.

`retired.jsonl` holds prompts dropped on 2026-10-28, each with a `retired` field giving the reason: `tgb-t2i-01`, `tgb-t2i-02` and `tgb-i2i-02` (anime and manga style asks that didn't match real use), and `tgb-t2i-04` and `tgb-t2i-09` (descriptive prompts with nothing to validate). Annotations already made on them stay in the ratings dataset.

`inputs/whiteboard-mcp-01.jpg` is from [Sample-Whiteboards](https://github.com/danielrosehill/Sample-Whiteboards) (`whiteboards/030426.jpg`, photographed 2026-04-03).
