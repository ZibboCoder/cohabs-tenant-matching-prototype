# matching_prototype_v2.py
# Tenant matching prototype (similarity + complementarity) with explainability
# Requirements: Python 3.8+, numpy, pandas
# Run: python3 matching_prototype_v2.py

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


# =========================
# CONFIG
# =========================
SEED = 1234  # keep this fixed for reproducible synthetic data; set to None for random each run

N_PROFILES = 300
TOP_N = 5

SCALE_MIN = 1
SCALE_MAX = 5

FEATURES = [
    "cleanliness_level",
    "noise_tolerance",
    "sleep_schedule",
    "routine_structure",
    "WFH_frequency",
    "sociability_level",
    "guest_tolerance",
    "privacy_need",
    "conflict_style",
    "shared_spaces_usage",
]

# Weights: higher = more important in final score
WEIGHTS: Dict[str, float] = {
    "cleanliness_level": 1.3,
    "noise_tolerance": 1.3,
    "sleep_schedule": 1.2,
    "routine_structure": 1.0,
    "WFH_frequency": 0.8,
    "sociability_level": 1.0,
    "guest_tolerance": 1.0,
    "privacy_need": 1.1,
    "conflict_style": 0.9,
    "shared_spaces_usage": 0.9,
}

# SCORING_MODE per feature:
# - "similarity": closer values => higher score
# - "complementarity": values that "balance" around the midpoint => higher score
#
# Complementarity here is implemented as "mirror balance":
#   on a 1..5 scale, best complementarity happens when a+b is close to 6:
#   (1,5), (2,4), (3,3), (4,2), (5,1)
SCORING_MODE: Dict[str, str] = {
    "cleanliness_level": "similarity",
    "noise_tolerance": "similarity",
    "sleep_schedule": "similarity",
    "routine_structure": "similarity",
    "WFH_frequency": "similarity",
    "sociability_level": "complementarity",
    "guest_tolerance": "similarity",
    "privacy_need": "similarity",
    "conflict_style": "similarity",
    "shared_spaces_usage": "complementarity",
}


# =========================
# HELPERS
# =========================
def make_tenant_label(user_id: int) -> str:
    return f"Tenant_{user_id:03d}"


def clamp01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


# =========================
# DATA GENERATION
# =========================
def generate_synthetic_profiles(n: int, seed: int = None) -> pd.DataFrame:
    if seed is not None:
        np.random.seed(seed)

    data = {"user_id": np.arange(1, n + 1)}
    for f in FEATURES:
        data[f] = np.random.randint(SCALE_MIN, SCALE_MAX + 1, size=n)

    df = pd.DataFrame(data)
    df["tenant_label"] = df["user_id"].apply(make_tenant_label)

    cols = ["user_id", "tenant_label"] + FEATURES
    return df[cols]


# =========================
# SCORING
# =========================
def similarity_score(a: float, b: float) -> float:
    """
    Similarity in [0..1], 1 means identical values.
    On 1..5, max distance is 4. Example:
      a=1 b=5 => dist=4 => score=0
      a=1 b=2 => dist=1 => score=0.75
    """
    max_dist = float(SCALE_MAX - SCALE_MIN)
    if max_dist <= 0:
        return 1.0
    dist = abs(a - b)
    return clamp01(1.0 - (dist / max_dist))


def complementarity_score(a: float, b: float) -> float:
    """
    Complementarity in [0..1] as "balance/mirror around midpoint".
    On a 1..5 scale, midpoint is 3 and the target sum is 6.
    Perfect complementarity when (a+b) == 6:
      (1,5), (2,4), (3,3), (4,2), (5,1) => score=1
    Worst when far from 6:
      (1,1) => sum=2 => score=0
      (5,5) => sum=10 => score=0
    """
    target_sum = float(SCALE_MIN + SCALE_MAX)  # e.g., 6 on 1..5
    max_dev = float(SCALE_MAX - SCALE_MIN)     # e.g., 4 on 1..5
    if max_dev <= 0:
        return 1.0

    s = float(a + b)
    dev = abs(s - target_sum)  # 0..max_dev
    return clamp01(1.0 - (dev / max_dev))


def feature_score(feature: str, a: float, b: float) -> Tuple[float, str]:
    """
    Returns:
      - score in [0..1]
      - mode used ("similarity" or "complementarity")
    """
    mode = SCORING_MODE.get(feature, "similarity")
    if mode == "complementarity":
        return complementarity_score(a, b), "complementarity"
    return similarity_score(a, b), "similarity"


# =========================
# MATCHING + EXPLAINABILITY
# =========================
def prettify_feature_name(f: str) -> str:
    return f.replace("_", " ").capitalize()


def compute_top_matches(profiles: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Computes top_n matches for each tenant.
    Output includes:
      - compatibility_score (0..100)
      - top drivers with weights + per-feature scores
      - short + long explanation
    """
    features = FEATURES
    weights = WEIGHTS
    total_weight = sum(weights.get(f, 1.0) for f in features)

    records = profiles.to_dict(orient="records")
    out_rows: List[Dict] = []

    for i, a in enumerate(records):
        candidates: List[Tuple[int, float, List[Tuple[str, float, float, str]]]] = []

        for j, b in enumerate(records):
            if a["user_id"] == b["user_id"]:
                continue

            per_feature_details: List[Tuple[str, float, float, str]] = []
            weighted_sum = 0.0

            for f in features:
                av = float(a[f])
                bv = float(b[f])
                sc, mode = feature_score(f, av, bv)  # 0..1
                w = float(weights.get(f, 1.0))
                weighted_sum += w * sc
                per_feature_details.append((f, sc, w, mode))

            compat = (weighted_sum / total_weight) * 100.0

            # drivers: sort by contribution = w*score
            per_feature_details.sort(key=lambda x: x[1] * x[2], reverse=True)
            candidates.append((j, compat, per_feature_details))

        candidates.sort(key=lambda x: x[1], reverse=True)
        top = candidates[:top_n]

        for rank, (j_idx, compat_score, details) in enumerate(top, start=1):
            b = records[j_idx]

            # top 3 drivers
            top3 = details[:3]
            driver_parts = []
            driver_pretty = []
            for f, sc, w, mode in top3:
                driver_parts.append(f"{f}(mode={mode}, score={sc:.2f}, w={w:.2f})")
                driver_pretty.append(prettify_feature_name(f))

            explanation_short = f"High compatibility driven by {', '.join(driver_pretty)}."
            explanation_long = (
                f"{a['tenant_label']} matches well with {b['tenant_label']} "
                f"(score {compat_score:.2f}%). Top drivers: {', '.join(driver_pretty)}. "
                "Note: similarity rewards close values, while complementarity rewards balanced pairs "
                "(on a 1..5 scale, best when a+b is about 6)."
            )
            # extra: show values for top drivers for clarity
            values_hint = []
            for f, sc, w, mode in top3:
                values_hint.append(f"{f}: {a[f]} vs {b[f]} ({mode}, {sc:.2f})")
            values_hint_txt = " | ".join(values_hint)

            out_rows.append({
                "user_id": a["user_id"],
                "tenant_label": a["tenant_label"],
                "match_rank": rank,
                "match_user_id": b["user_id"],
                "match_tenant_label": b["tenant_label"],
                "compatibility_score": round(float(compat_score), 2),
                "top_drivers": "; ".join(driver_parts),
                "explanation_short": explanation_short,
                "explanation_long": explanation_long,
                "top_driver_values": values_hint_txt,
            })

    return pd.DataFrame(out_rows)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    profiles = generate_synthetic_profiles(N_PROFILES, seed=SEED)
    profiles.to_csv("synthetic_profiles_v2.csv", index=False)

    matches = compute_top_matches(profiles, top_n=TOP_N)
    matches.to_csv("top_matches_explained_v2.csv", index=False)

    print("Done ✅")
    print("Files created: synthetic_profiles_v2.csv and top_matches_explained_v2.csv")
