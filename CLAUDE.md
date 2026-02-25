# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Generate/regenerate the synthetic data CSVs
python3 matching_engine.py

# Launch the Streamlit demo
streamlit run app.py
```

Dependencies are in `requirements.txt` (streamlit, pandas, pillow, requests). The virtual environment is at `.venv/`.

## Architecture

This is a two-file prototype for co-living tenant matching:

**`matching_engine.py`** — offline batch pipeline:
- Generates 300 synthetic tenant profiles (`N_PROFILES=300, SEED=1234`) and saves to `synthetic_profiles_v2.csv`
- Computes pairwise compatibility for all tenants, picks top 5 matches per tenant, generates explainability text, and saves to `top_matches_explained_v2.csv`

**`app.py`** — Streamlit UI:
- Reads only `synthetic_profiles_v2.csv` (the `top_matches_explained_v2.csv` is **not** used by the current app)
- Re-implements the matching engine inline and computes matches **live** on every interaction
- Two tabs: "Explore Profiles" (select a synthetic tenant) and "Try It Yourself" (custom sliders)
- Renders avatars via DiceBear API (external network call), donut SVGs and radar charts as inline SVG strings

**Critical duplication:** `FEATURES`, `WEIGHTS`, and `SCORING_MODE` constants are defined identically in **both** files. Any change to the scoring model must be applied in both places.

## Scoring model

Each tenant has 10 behavioral variables scored 1–5. Compatibility (0–100%) is a weighted average of per-feature scores:

- **Similarity** (8 variables): `score = 1 - |a - b| / 4` — closer values score higher
- **Complementarity** (2 variables: `sociability_level`, `shared_spaces_usage`): `score = 1 - |a + b - 6| / 4` — balanced pairs (summing to ~6) score higher

Top drivers for each match are the 3 features with highest `weight × score` contribution.
