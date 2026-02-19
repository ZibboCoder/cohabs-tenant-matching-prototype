import numpy as np
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
N_PROFILES = 300
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

# Weights: higher = more important in the final score
WEIGHTS = {
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

# For each feature choose how "compatibility" is computed:
# - "similarity": closer values => better
# - "complementarity": mid-range / balanced pairs => better (example: high + low can work, but extremes may be less stable)
SCORING_MODE = {
    "cleanliness_level": "similarity",
    "noise_tolerance": "similarity",
    "sleep_schedule": "similarity",
    "routine_structure": "similarity",
    "WFH_frequency": "similarity",
    "sociability_level": "complementarity",
    "guest_tolerance": "similarity",
    "privacy_need": "complementarity",
    "conflict_style": "similarity",
    "shared_spaces_usage": "complementarity",
}

TOP_N = 5


# -----------------------------
# HELPERS
# -----------------------------
def generate_synthetic_profiles(n: int) -> pd.DataFrame:
    """
    Creates synthetic tenant profiles with values in [1..5] for each feature.
    """
    data = {"user_id": np.arange(1, n + 1)}
    for f in FEATURES:
        data[f] = np.random.randint(SCALE_MIN, SCALE_MAX + 1, size=n)
    return pd.DataFrame(data)


def similarity_score(a: float, b: float, scale_min: int = 1, scale_max: int = 5) -> float:
    """
    Normalized similarity in [0..1].
    1.0 means identical, 0.0 means max distance.
    """
    max_dist = scale_max - scale_min
    dist = abs(a - b)
    return 1.0 - (dist / max_dist)


def complementarity_score(a: float, b: float, scale_min: int = 1, scale_max: int = 5) -> float:
    """
    A simple complementarity idea:
    - reward pairs whose average is close to the middle of the scale
    - small penalty for being too extreme as a pair

    Output in [0..1].
    """
    mid = (scale_min + scale_max) / 2.0  # e.g., 3.0
    avg = (a + b) / 2.0
    # closeness of average to the middle
    max_dev = (scale_max - scale_min) / 2.0  # e.g., 2.0
    avg_closeness = 1.0 - (abs(avg - mid) / max_dev)  # 1 at mid, 0 at extremes

    # penalty if the pair is "too extreme" (both low or both high)
    # extremes_index: 1 means at edge, 0 means at mid
    a_ext = abs(a - mid) / max_dev
    b_ext = abs(b - mid) / max_dev
    extremes_penalty = (a_ext + b_ext) / 2.0  # 0..1

    score = avg_closeness * (1.0 - 0.25 * extremes_penalty)

    # keep in [0..1]
    return float(max(0.0, min(1.0, score)))


def feature_score(feature: str, a: float, b: float) -> float:
    mode = SCORING_MODE.get(feature, "similarity")
    if mode == "complementarity":
        return complementarity_score(a, b, SCALE_MIN, SCALE_MAX)
    return similarity_score(a, b, SCALE_MIN, SCALE_MAX)


def compute_pair_score_with_explainability(profile_a: pd.Series, profile_b: pd.Series):
    """
    Returns:
    - total_score in [0..100]
    - per_feature contributions for explainability
    """
    weighted_sum = 0.0
    weight_total = 0.0
    contributions = {}

    for f in FEATURES:
        w = float(WEIGHTS.get(f, 1.0))
        s = feature_score(f, float(profile_a[f]), float(profile_b[f]))  # 0..1
        contrib = w * s

        contributions[f] = {
            "a": float(profile_a[f]),
            "b": float(profile_b[f]),
            "mode": SCORING_MODE.get(f, "similarity"),
            "feature_score_0_1": round(s, 4),
            "weight": w,
            "weighted_contribution": round(contrib, 4),
        }

        weighted_sum += contrib
        weight_total += w

    total_0_1 = weighted_sum / weight_total if weight_total > 0 else 0.0
    total_0_100 = round(total_0_1 * 100.0, 2)

    return total_0_100, contributions


def compute_top_matches(profiles: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    For each user, find top_n matches among all other users.
    Output includes explainability: top drivers (3 features that contributed most).
    """
    results = []
    n = len(profiles)

    # Pre-store rows to speed up
    rows = [profiles.iloc[i] for i in range(n)]

    for i in range(n):
        a = rows[i]
        scores = []

        for j in range(n):
            if i == j:
                continue
            b = rows[j]
            total, contribs = compute_pair_score_with_explainability(a, b)
            scores.append((j, total, contribs))

        # sort desc by total score
        scores.sort(key=lambda x: x[1], reverse=True)

        for rank, (j_idx, total, contribs) in enumerate(scores[:top_n], start=1):
            # top drivers: top 3 by weighted contribution
            sorted_feats = sorted(
                contribs.items(),
                key=lambda kv: kv[1]["weighted_contribution"],
                reverse=True,
            )
            top_drivers = [f"{k}({v['weighted_contribution']})" for k, v in sorted_feats[:3]]

            results.append(
                {
                    "user_id": int(a["user_id"]),
                    "match_rank": rank,
                    "match_user_id": int(rows[j_idx]["user_id"]),
                    "compatibility_score": total,
                    "top_drivers": "; ".join(top_drivers),
                }
            )

    return pd.DataFrame(results)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    profiles = generate_synthetic_profiles(N_PROFILES)
    profiles.to_csv("synthetic_profiles.csv", index=False)

    matches = compute_top_matches(profiles, top_n=TOP_N)
    matches.to_csv("top_matches_explained.csv", index=False)

    print("Done ✅")
    print("Files created: synthetic_profiles.csv and top_matches_explained.csv")
