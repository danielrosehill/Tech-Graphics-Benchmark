# Tech-Graphics-Benchmark

> **Status: draft prompts, not yet run (2026-10-28).** Design, four test prompts and a private annotation Space. No generations or results yet.
>
> **Visibility:** repo public · prompts public · runs none · ratings private

Can an image generation model turn a technical explanation into a colourful, stylised diagram (anime, manga, bold flat colour) **without losing the meaning**: every label spelled exactly, every arrow where it was asked for?

Diagrams-as-code (Mermaid, Graphviz, PlantUML) are accurate, well tooled and dull. Generative image models can bring colour, style and personality to explaining a concept, but text rendering has long been their Achilles heel, and for an explainer diagram one wrong label is fatal. This is a deliberately lightweight, periodic check (one or two prompts per modality) to see which models currently get it right. Models change too fast for an exhaustive comparison to stay useful.

The winners here are not necessarily the most photorealistic or "best" image models. Text fidelity and instruction following are different skills, and a smaller model, a LoRA or a fine-tune can beat a frontier model on them.

## Test prompts

[![Hugging Face](https://img.shields.io/badge/HuggingFace-Dataset-yellow?logo=huggingface)](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark)

Four prompts, two per modality: [huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark). The source of truth is [`data/prompts.jsonl`](data/prompts.jsonl), and [`data/README.md`](data/README.md) is the dataset card. Upload with:

```bash
hf upload danielrosehill/Tech-Graphics-Benchmark data . --repo-type dataset
```

| ID | Modality | What it tests |
|---|---|---|
| `tgb-t2i-01` | Text-to-image | Anime-style blog explainer of ASR fine-tuning for domain vocabulary across two models: 11 exact strings including WER figures, two panels, arrows |
| `tgb-t2i-02` | Text-to-image | Manga-style speech-to-text pipeline: box order, arrow directions, one arrow from a box below the row, a speech bubble with a deliberate tricky string |
| `tgb-i2i-01` | Image-to-image | Whiteboard photo → clean colour diagram, **keeping the handwriting** but making it legible; fix three named misspellings, nothing else |
| `tgb-i2i-02` | Image-to-image | Same whiteboard → anime infographic with handwriting **replaced by sans-serif type**; layout and arrows unchanged |

Each record carries `expected_text` (every string that must appear, spelled exactly) and `structure_checks` (the arrow and layout instructions to verify).

## Mechanism

Two modalities, graded separately because they fail differently:

- **Text-to-image.** The model gets a written description of a diagram with exact label strings, numbers and arrow directions. The failure to look for is garbled, misspelt or invented text and arrows that point the wrong way or connect the wrong boxes.
- **Image-to-image.** The model gets a photo of a hand-drawn whiteboard or notepad sketch and is asked to restyle it: keep the handwriting but make it legible, or swap it for a clean font, add colour, straighten the perspective. The failure to look for is **text transposition errors**: labels the model drops, invents, rewords or "corrects" wrongly while restyling.

Style is part of the ask (anime, manga, flat colour) because the point is a diagram with personality. A correct but plain output passes the hard checks; the notes record whether it was any fun to look at.

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
| Design, prompts source, Space source | this repo |
| Test prompts | HF dataset [`danielrosehill/Tech-Graphics-Benchmark`](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark) (public) |
| Generations | HF dataset `danielrosehill/Tech-Graphics-Benchmark-Runs` (public, empty until the first run). Layout: `<run_id>/manifest.jsonl` + `<run_id>/images/<gen_id>.png` |
| Annotations | HF dataset `danielrosehill/Tech-Graphics-Benchmark-Ratings` (private), one file per generation at `annotations/<run_id>/<gen_id>.json` |
| Annotation app | HF Space `danielrosehill/Tech-Graphics-Benchmark-Annotate` (private, Gradio) |

A manifest row is `{"gen_id", "run_id", "prompt_id", "model", "provider", "image", "created"}`, with `image` relative to the dataset root. Run IDs are `YYYY-MM-DD-<label>`.

The Space reads all three datasets at startup, so restart it after pushing a run. It needs the secret `HF_TOKEN` (write access to the ratings dataset); the repo IDs can be overridden with the variables `RUNS_REPO`, `PROMPTS_REPO` and `RATINGS_REPO`. Redeploy with `space/deploy.sh`.

## Results

Not yet run.

## Open questions

- Model panel for the first run. A previous informal round (whiteboard restyling, spring 2026, see [Sample-Whiteboards](https://github.com/danielrosehill/Sample-Whiteboards)) had Nano Banana ahead on text fidelity. Candidates: Nano Banana 2, GPT Image, Ideogram, Recraft, Seedream, Qwen-Image, FLUX (incl. a text-focused LoRA).
- One generation per model per prompt, or a few seeds to see how much it varies?
- Whether to add a notepad sketch (pen on paper) as a second image-to-image input alongside the whiteboard.

## Origin

Daniel Rosehill, 2026-10-28, while writing a blog post explaining what an ASR fine-tune's evaluation showed about domain recognition across two models. Builds on the whiteboard-to-diagram work in [Nano-Banana-Tech-Diagram-Maker](https://github.com/danielrosehill/Nano-Banana-Tech-Diagram-Maker) and [Sample-Whiteboards](https://github.com/danielrosehill/Sample-Whiteboards).

## Related

- [Hebrew-Image-Generation-Eval](https://github.com/danielrosehill/Hebrew-Image-Generation-Eval): pass/fail Hebrew text rendering across twelve text-to-image models. Same text-fidelity question, for Hebrew rather than diagrams.
- [Tech-Diagram-Image-Gen-Prompts](https://github.com/danielrosehill/Tech-Diagram-Image-Gen-Prompts): the prompt library (28 styles, 33 diagram types) for actually making these diagrams.
- [Nano-Tech-Diagrams-MCP](https://github.com/danielrosehill/Nano-Tech-Diagrams-MCP): MCP server that generates them with Nano Banana 2.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
