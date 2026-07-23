# [SpiralBench viewer](https://snailbones.github.io/spiralbench-viewer)

A vibe-codded static web app for browsing [SpiralBench](https://eqbench.com/spiral-bench.html)
(v1.2) results: pick a scenario, compare how different models handled the same
suggestible user, and read the transcripts with the score-affecting sections
highlighted.

Everything is pre-baked into `docs/` — no server, no dependencies. Host it on
GitHub Pages (serve `docs/` from the main branch) or view it locally:

```bash
python3 -m http.server -d docs        # http://localhost:8000
```

## What it shows

- A scenario category is picked at random on load (theory development,
  mania/psychosis, conspiracies, AI consciousness, …); switch via the tabs.
  The category lives in the URL hash, so links like `/#mania_psychosis` work.
- A random scenario's opening user message, with **5 randomly sampled models**
  sorted by their per-conversation spiral score (most spiraled first).
  Buttons re-roll the scenario or resample the models.
- Each model card shows a diverging risky/protective meter, weighted totals,
  the final off-rails rating, per-metric incidence chips (hover for the rubric
  definition), the judges' flagged quotes with intensities, and a collapsible
  full transcript (fetched lazily, ~150KB each).
- Loaded transcripts highlight the score-affecting sections inline: judge
  quotes are located in the assistant turns (fuzzy matching handles the
  judges' elisions and formatting changes, ~94% located) and marked risky
  (crimson) or protective (teal); hover for metric, intensity, and judge(s).
  Flags whose quote can't be located appear as ⚑ chips on their turn.

## Scoring

Per-conversation **spiral score** = Σ (weight × incidence intensity) over
risky metrics − the same over protective metrics, summed across assistant
turns and averaged across the three judges, using the benchmark's own
`scoring_weights_v1.2.json`. Higher = the conversation went further off the
rails. This is a viewer-side per-conversation analogue of the official
model-level score, not the official normalization — but model-level averages
reproduce the leaderboard ordering. The meter is scaled to the 5th–95th
percentile of all conversations and clamps beyond that; exact numbers are
always shown.

Note: the judges' per-turn chunks skip each conversation's first assistant
turn (upstream design), so first replies never carry highlights.

## Rebuilding the data

`docs/data/` is generated from a checkout of the
[spiral-bench](https://github.com/sam-paech/spiral-bench) repository
(its `res_v1.2/` results and `data/` rubric/weights):

```bash
SPIRAL_DATA_DIR=/path/to/spiral-bench python3 build_static.py
```

If `spiral-bench` is checked out as a sibling directory of this repo, the
env var can be omitted. The build condenses ~300MB of raw judge output into
`docs/data/index.json` (~6MB: scores, metric totals, flagged quotes) plus one
transcript file per (model, scenario) pair with pre-located highlight spans.

## Layout

- `docs/index.html` — the single-page frontend (fetches `docs/data/`).
- `docs/data/` — generated; index + 750 transcript files, ~130MB.
- `build_static.py` — regenerates `docs/data/`.
- `spiral.py` — the data library: loading, scoring, quote-span location.
