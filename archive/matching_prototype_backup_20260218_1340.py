import numpy as np
import pandas as pd

# =========================
# CONFIG
# =========================
SEED = 42
np.random.seed(SEED)

N_PROFILES = 300
SCALE_MIN = 1
SCALE_MAX = 5
TOP_N = 5

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

FEATURE_LABELS = {
    "cleanliness_level": "Cleanliness",
    "noise_tolerance": "Noise tolerance",
    "sleep_schedule": "Sleep schedule",
    "routine_structure": "Routine structure",
    "WFH_frequency": "Work-from-home frequency",
    "sociability_level": "Sociability",
    "guest_tolerance": "Guest tolerance",
    "privacy_need": "Privacy need",
    "conflict_style": "Conflict style",
    "shared_spaces_usage": "Shared spaces usage",
}

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

SCORING_MODE = {
    "cleanliness_level": "similarity",
    "noise_tolerance": "similarity",
    "sleep_schedule": "similarity",
    "routine_structure": "similarity",
    "WFH_frequency": "similarity",
    "sociability_level": "similarity",
    "guest_tolerance": "similarity",
    "privacy_need": "similarity",
    "conflict_style": "similarity",
    "shared_spaces_usage": "similarity",
}


# =========================
# DATA GENERATION
# =========================
def make_tenant_label(user_id: int) -> str:
    return f"Tenant_{user_id:03d}"


def generate_synthetic_profiles(n: int) -> pd.DataFrame:
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
    max_dist = SCALE_MAX - SCALE_MIN
    dist = abs(a - b)
    return 1.0 - (dist / max_dist)


def compute_pair_score(a_row: pd.Series, b_row: pd.Series):
    weighted_sum = 0.0
    total_weight = 0.0
    details = {}

    for f in FEATURES:
        a_val = float(a_row[f])
        b_val = float(b_row[f])
        weight = WEIGHTS[f]

        score = similarity_score(a_val, b_val)
        contribution = weight * score

        details[f] = {
            "a": int(a_val),
            "b": int(b_val),
            "feature_score": round(score, 4),
            "weight": weight,
            "contribution": round(contribution, 4),
        }

        weighted_sum += contribution
        total_weight += weight

    final_score = round((weighted_sum / total_weight) * 100, 2)
    return final_score, details


# =========================
# EXPLANATION
# =========================
def build_explanations(a_row, b_row, details, final_score):
    sorted_features = sorted(
        details.items(),
        key=lambda x: x[1]["contribution"],
        reverse=True,
    )

    top3 = sorted_features[:3]
    top_features = [FEATURE_LABELS[k] for k, _ in top3]

    explanation_short = (
        f"High compatibility driven by {top_features[0]}, "
        f"{top_features[1]} and {top_features[2]}."
    )

    explanation_long = (
        f"{a_row['tenant_label']} matches well with {b_row['tenant_label']} "
        f"(score {final_score}%). "
        f"The strongest alignment is in {top_features[0]}, "
        f"{top_features[1]} and {top_features[2]}, "
        f"where their behavioural preferences are closely aligned."
    )

    return explanation_short, explanation_long


# =========================
# MATCHING ENGINE
# =========================
def compute_top_matches(profiles: pd.DataFrame):
    results = []
    rows = [profiles.iloc[i] for i in range(len(profiles))]

    for i, a in enumerate(rows):
        scored = []

        for j, b in enumerate(rows):
            if i == j:
                continue

            final_score, details = compute_pair_score(a, b)
            explanation_short, explanation_long = build_explanations(a, b, details, final_score)

            scored.append((j, final_score, explanation_short, explanation_long))

        scored.sort(key=lambda x: x[1], reverse=True)

        for rank, (j_idx, score, short_exp, long_exp) in enumerate(scored[:TOP_N], start=1):
            results.append({
                "user_id": int(a["user_id"]),
                "tenant_label": a["tenant_label"],
                "match_rank": rank,
                "match_user_id": int(rows[j_idx]["user_id"]),
                "match_tenant_label": rows[j_idx]["tenant_label"],
                "compatibility_score": score,
                "explanation_short": short_exp,
                "explanation_long": long_exp,
            })

    return pd.DataFrame(results)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    profiles = generate_synthetic_profiles(N_PROFILES)
    profiles.to_csv("synthetic_profiles.csv", index=False)

    matches = compute_top_matches(profiles)
    matches.to_csv("top_matches_explained.csv", index=False)

    print("Done ✅")
    print("Files created: synthetic_profiles.csv and top_matches_explained.csv")
