#!/usr/bin/env bash
# Upload the annotation app to the private Space. Restart the Space after pushing a new run
# so it re-reads the runs dataset.
set -euo pipefail
cd "$(dirname "$0")"
hf upload danielrosehill/Tech-Graphics-Benchmark-Annotate . . --repo-type space \
  --include app.py requirements.txt README.md --commit-message "Deploy annotation app"
