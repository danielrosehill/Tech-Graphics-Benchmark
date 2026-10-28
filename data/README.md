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

Test prompts for [Tech-Graphics-Benchmark](https://github.com/danielrosehill/Tech-Graphics-Benchmark): can an image model make a colourful, stylised tech diagram without getting the text or the arrows wrong?

`prompts.jsonl`, one record per prompt:

| Field | Meaning |
|---|---|
| `id` | `tgb-t2i-NN` (text-to-image) or `tgb-i2i-NN` (image-to-image) |
| `modality` | `text-to-image` or `image-to-image` |
| `style` | The visual style asked for |
| `prompt` | Exact text sent to the model |
| `input_image` | Path under `inputs/` for image-to-image, else `null` |
| `expected_text` | Every string that must appear, spelled exactly. Pass/fail ground truth. Empty for descriptive prompts, where any garbled or invented text fails |
| `structure_checks` | Arrow, layout and content instructions the grader checks |
| `notes` | Optional: sources for figures in the prompt, grading caveats |

`inputs/whiteboard-mcp-01.jpg` is from [Sample-Whiteboards](https://github.com/danielrosehill/Sample-Whiteboards) (`whiteboards/030426.jpg`, photographed 2026-04-03).
