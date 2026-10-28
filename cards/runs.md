---
license: cc-by-4.0
pretty_name: Tech Graphics Benchmark (generations)
task_categories:
- text-to-image
- image-to-image
tags:
- diagrams
- text-rendering
- benchmark
---

# Tech Graphics Benchmark: generations

Every image generated for [Tech-Graphics-Benchmark](https://github.com/danielrosehill/Tech-Graphics-Benchmark), one folder per round.

- Prompts: [danielrosehill/Tech-Graphics-Benchmark](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark)
- Annotations (raw eval data): [danielrosehill/Tech-Graphics-Benchmark-Ratings](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark-Ratings)

Layout: `<run_id>/manifest.jsonl` + `<run_id>/images/<gen_id>.png`. Manifest rows are shuffled and `gen_id`s are opaque, so the annotation Space stays blind.

| Field | Meaning |
|---|---|
| `gen_id`, `run_id`, `prompt_id`, `attempt` | Identity: prompt and which try (1..N) |
| `model`, `endpoint`, `provider` | Model label, provider endpoint ID, provider (`fal`) |
| `image` | Path relative to the dataset root |
| `seed` | Seed the provider reported, or null |
| `requested_size` | Size the round asked for (`image_size`, or `aspect_ratio` + `resolution`) |
| `width`, `height` | Delivered size in pixels |
| `usd_per_image`, `price_basis` | Cost per image and where it came from (list price unless stated) |
| `created` | Local generation time |
