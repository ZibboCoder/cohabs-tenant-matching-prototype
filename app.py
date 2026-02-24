import hashlib
import numpy as np
import pandas as pd
import streamlit as st
import urllib.parse

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Tenant Matching — Co-living Compatibility Engine",
    page_icon="🏡",
    layout="wide",
)

# ----------------------------
# CSS — Professional & Clean
# ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

/* ---- Base ---- */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #0f172a;
}

.main { background: #f8fafc; }
.block-container { padding: 2rem 3rem 3rem 3rem !important; max-width: 1200px; }

/* ---- Hero ---- */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #1d4ed8 100%);
    border-radius: 16px;
    padding: 3rem 3.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 40%;
    width: 300px; height: 300px;
    background: rgba(29,78,216,0.15);
    border-radius: 50%;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: #ffffff;
    margin: 0 0 0.5rem 0;
    line-height: 1.15;
}
.hero-sub {
    font-size: 1.05rem;
    color: #93c5fd;
    margin: 0 0 1.5rem 0;
    font-weight: 400;
}
.hero-badges {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}
.badge {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.15);
    color: #e0f2fe;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    backdrop-filter: blur(4px);
}

/* ---- Section titles ---- */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    color: #0f172a;
    margin: 2rem 0 0.25rem 0;
}
.section-sub {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 1.25rem;
}

/* ---- Match card ---- */
.match-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s;
}
.match-card:hover { box-shadow: 0 4px 20px rgba(15,23,42,0.08); }

.match-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0f172a;
    margin: 0 0 0.15rem 0;
}
.match-score-text {
    font-size: 0.85rem;
    color: #475569;
    margin: 0;
}
.driver-tag {
    display: inline-block;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 0.15rem 0.1rem;
}
.explanation-box {
    background: #f8fafc;
    border-left: 3px solid #1d4ed8;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #334155;
    margin-top: 0.75rem;
}

/* ---- Profile table ---- */
.profile-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
}

/* ---- Questionnaire ---- */
.questionnaire-header {
    background: linear-gradient(135deg, #ecfdf5, #d1fae5);
    border: 1px solid #6ee7b7;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}
.questionnaire-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #064e3b;
    margin: 0 0 0.3rem 0;
}
.questionnaire-sub {
    font-size: 0.9rem;
    color: #065f46;
    margin: 0;
}

/* ---- Score highlight ---- */
.score-big {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #1d4ed8;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: #f1f5f9;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1.25rem !important;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    font-weight: 500;
    font-size: 0.9rem;
}

/* ---- Divider ---- */
hr { border-color: #e2e8f0; margin: 1.5rem 0; }

/* ---- Footer ---- */
.footer {
    text-align: center;
    font-size: 0.78rem;
    color: #94a3b8;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------
# Matching engine (inline)
# importiamo le funzioni core direttamente
# per il questionario live senza dipendenze esterne
# ----------------------------
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
    "sociability_level": "complementarity",
    "guest_tolerance": "similarity",
    "privacy_need": "similarity",
    "conflict_style": "similarity",
    "shared_spaces_usage": "complementarity",
}

# Human-readable labels and descriptions for the questionnaire
FEATURE_LABELS = {
    "cleanliness_level":   ("🧹 Cleanliness standard", "1 = very relaxed · 5 = very high standards"),
    "noise_tolerance":     ("🔊 Noise tolerance",      "1 = need complete silence · 5 = totally fine with noise"),
    "sleep_schedule":      ("🌙 Sleep schedule",       "1 = very early bird · 5 = night owl"),
    "routine_structure":   ("📅 Daily routine",        "1 = very flexible · 5 = highly structured"),
    "WFH_frequency":       ("💻 Work from home",       "1 = always at the office · 5 = always at home"),
    "sociability_level":   ("🤝 Sociability at home",  "1 = very introverted · 5 = very social"),
    "guest_tolerance":     ("🚪 Guests at home",       "1 = prefer no guests · 5 = very open to guests"),
    "privacy_need":        ("🔒 Need for privacy",     "1 = very open · 5 = need a lot of personal space"),
    "conflict_style":      ("💬 Conflict approach",    "1 = very avoidant · 5 = very direct"),
    "shared_spaces_usage": ("🍳 Shared spaces usage",  "1 = mostly in my room · 5 = always in common areas"),
}


def clamp01(x):
    return float(max(0.0, min(1.0, x)))

def similarity_score(a, b):
    max_dist = float(SCALE_MAX - SCALE_MIN)
    return clamp01(1.0 - (abs(a - b) / max_dist))

def complementarity_score(a, b):
    target_sum = float(SCALE_MIN + SCALE_MAX)
    max_dev = float(SCALE_MAX - SCALE_MIN)
    return clamp01(1.0 - (abs(a + b - target_sum) / max_dev))

def feature_score(feature, a, b):
    mode = SCORING_MODE.get(feature, "similarity")
    if mode == "complementarity":
        return complementarity_score(a, b), "complementarity"
    return similarity_score(a, b), "similarity"

def prettify(f):
    return f.replace("_", " ").capitalize()

def compute_matches_for_user(user_values: dict, profiles_df: pd.DataFrame, top_n: int = 5):
    """
    Compute top_n matches for a given user_values dict against profiles_df.
    Returns a list of dicts with match info.
    """
    total_weight = sum(WEIGHTS.get(f, 1.0) for f in FEATURES)
    results = []

    for _, row in profiles_df.iterrows():
        weighted_sum = 0.0
        details = []
        for f in FEATURES:
            av = float(user_values[f])
            bv = float(row[f])
            sc, mode = feature_score(f, av, bv)
            w = float(WEIGHTS.get(f, 1.0))
            weighted_sum += w * sc
            details.append((f, sc, w, mode))

        compat = (weighted_sum / total_weight) * 100.0
        details.sort(key=lambda x: x[1] * x[2], reverse=True)
        top3 = details[:3]

        results.append({
            "label": row["tenant_label"],
            "score": round(compat, 2),
            "top3": top3,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


# ----------------------------
# Helpers
# ----------------------------
def avatar_url(label: str, size: int = 128, style: str = "personas") -> str:
    seed = urllib.parse.quote(label)
    return f"https://api.dicebear.com/9.x/{style}/png?seed={seed}&size={size}"

def donut_svg(percent_value: float, size: int = 80, stroke: int = 9) -> str:
    p = max(0.0, min(100.0, float(percent_value)))
    r = (size - stroke) / 2
    c = 2 * 3.141592653589793 * r
    offset = c * (1 - p / 100.0)
    # Color based on score
    color = "#16a34a" if p >= 80 else "#1d4ed8" if p >= 60 else "#f59e0b" if p >= 40 else "#ef4444"
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{size/2}" cy="{size/2}" r="{r}"
              fill="none" stroke="#e2e8f0" stroke-width="{stroke}" />
      <circle cx="{size/2}" cy="{size/2}" r="{r}"
              fill="none" stroke="{color}" stroke-width="{stroke}"
              stroke-linecap="round"
              stroke-dasharray="{c:.2f}"
              stroke-dashoffset="{offset:.2f}"
              transform="rotate(-90 {size/2} {size/2})" />
      <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"
            font-family="DM Sans, system-ui" font-size="{int(size*0.2)}"
            font-weight="700" fill="#0f172a">
        {p:.0f}%
      </text>
    </svg>"""

def load_data(profiles_path, matches_path):
    profiles = pd.read_csv(profiles_path)
    matches = pd.read_csv(matches_path)
    return profiles, matches

def pct(x):
    try: return float(x)
    except: return 0.0


# ----------------------------
# Hero Section
# ----------------------------
st.markdown("""
<div class="hero">
  <div class="hero-title">Co-living Compatibility Engine</div>
  <div class="hero-sub">AI-powered tenant matching · Reduce conflicts · Build better communities</div>
  <div class="hero-badges">
    <span class="badge">⚡ 300 synthetic profiles</span>
    <span class="badge">🧠 10 behavioral variables</span>
    <span class="badge">📊 Similarity + Complementarity</span>
    <span class="badge">🔍 Explainable AI</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    top_n = st.slider("Top N matches to show", min_value=3, max_value=10, value=5, step=1)

    st.divider()
    st.markdown("### 📖 How it works")
    st.markdown("""
Each tenant profile has **10 behavioral variables** scored 1–5.

The engine computes a **compatibility score (0–100%)** using:
- **Similarity** — rewards similar values (e.g. sleep schedule, cleanliness)
- **Complementarity** — rewards balanced pairs (e.g. sociability, shared spaces)

Each variable has a **weight** reflecting its importance in daily co-living friction.

The **Top Drivers** show which variables influenced the match most.
    """)

    st.divider()
    st.markdown("### 📁 Data source")
    use_upload = st.checkbox("Upload custom CSV files", value=False)


# ----------------------------
# Load data
# ----------------------------
profiles_path = "synthetic_profiles_v2.csv"
matches_path = "top_matches_explained_v2.csv"
profiles, matches = None, None

try:
    if use_upload:
        up_p = st.sidebar.file_uploader("synthetic_profiles_v2.csv", type=["csv"])
        up_m = st.sidebar.file_uploader("top_matches_explained_v2.csv", type=["csv"])
        if up_p is None or up_m is None:
            st.info("Upload both CSV files to continue, or uncheck the option above.")
            st.stop()
        profiles = pd.read_csv(up_p)
        matches = pd.read_csv(up_m)
    else:
        profiles, matches = load_data(profiles_path, matches_path)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()


# ----------------------------
# Tabs
# ----------------------------
tab1, tab2 = st.tabs(["🔍 Explore Profiles", "✏️ Try It Yourself"])


# ============================================================
# TAB 1 — Explore existing profiles
# ============================================================
with tab1:
    st.markdown('<div class="section-title">Explore Tenant Profiles</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Select a synthetic tenant and explore their top compatibility matches.</div>', unsafe_allow_html=True)

    tenant_list = sorted(profiles["tenant_label"].unique().tolist())
    selected_tenant = st.selectbox("Select a tenant", tenant_list, index=0, label_visibility="collapsed")

    sel_row = profiles[profiles["tenant_label"] == selected_tenant].head(1)
    if sel_row.empty:
        st.error("Tenant not found.")
        st.stop()

    # Profile card
    st.markdown('<div class="profile-box">', unsafe_allow_html=True)
    col_av, col_data = st.columns([1, 6], gap="medium")
    with col_av:
        st.image(avatar_url(selected_tenant, size=120), width=88)
    with col_data:
        st.markdown(f"**{selected_tenant}**")
        display_row = sel_row.drop(columns=["user_id"], errors="ignore").copy()
        st.dataframe(display_row, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Matches
    sub = matches[matches["tenant_label"] == selected_tenant].copy()
    if sub.empty:
        st.warning("No matches found for this tenant.")
        st.stop()

    sub["compatibility_score"] = sub["compatibility_score"].apply(pct)
    sub = sub.sort_values("compatibility_score", ascending=False).head(top_n)

    st.markdown('<div class="section-title">Top Matches</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Best {top_n} compatibility matches for {selected_tenant}</div>', unsafe_allow_html=True)

    for rank, (_, r) in enumerate(sub.iterrows(), start=1):
        match_label = r.get("match_tenant_label", "")
        score = float(r.get("compatibility_score", 0.0))
        short = str(r.get("explanation_short", "")).strip()
        drivers_raw = str(r.get("top_drivers", "")).strip()
        driver_vals = str(r.get("top_driver_values", "")).strip()
        long_exp = str(r.get("explanation_long", "")).strip()

        # Parse driver names for tags
        driver_names = []
        for part in drivers_raw.split(";"):
            part = part.strip()
            if "(" in part:
                driver_names.append(part.split("(")[0].strip().replace("_", " ").capitalize())

        with st.container():
            st.markdown('<div class="match-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 5, 2], gap="medium")

            with c1:
                st.image(avatar_url(match_label, size=96), width=68)

            with c2:
                st.markdown(f'<div class="match-name">#{rank} &nbsp; {match_label}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="match-score-text">Compatibility score: <strong>{score:.1f}%</strong></div>', unsafe_allow_html=True)
                if driver_names:
                    tags_html = "".join([f'<span class="driver-tag">{d}</span>' for d in driver_names])
                    st.markdown(f"<div style='margin-top:0.5rem'>Top drivers: {tags_html}</div>", unsafe_allow_html=True)
                if short:
                    st.markdown(f'<div class="explanation-box">{short}</div>', unsafe_allow_html=True)

            with c3:
                st.markdown(
                    f"<div style='display:flex;justify-content:flex-end;align-items:center;height:100%'>{donut_svg(score)}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("📋 Full explanation & variable breakdown"):
                if long_exp:
                    st.write(long_exp)
                if driver_vals:
                    st.markdown("**Top driver values:**")
                    for item in driver_vals.split("|"):
                        st.markdown(f"- {item.strip()}")


# ============================================================
# TAB 2 — Try It Yourself (live questionnaire)
# ============================================================
with tab2:
    st.markdown("""
    <div class="questionnaire-header">
      <div class="questionnaire-title">Find Your Co-living Matches</div>
      <div class="questionnaire-sub">Answer 10 quick questions about your lifestyle and see your top compatibility matches in real time.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-sub">Rate each variable from 1 to 5 using the sliders below.</div>', unsafe_allow_html=True)

    user_values = {}

    # Display sliders in 2 columns for a cleaner layout
    col_left, col_right = st.columns(2, gap="large")
    features_left = FEATURES[:5]
    features_right = FEATURES[5:]

    with col_left:
        for f in features_left:
            label, desc = FEATURE_LABELS[f]
            st.markdown(f"**{label}**")
            st.caption(desc)
            user_values[f] = st.slider(
                label, min_value=1, max_value=5, value=3,
                key=f"q_{f}", label_visibility="collapsed"
            )

    with col_right:
        for f in features_right:
            label, desc = FEATURE_LABELS[f]
            st.markdown(f"**{label}**")
            st.caption(desc)
            user_values[f] = st.slider(
                label, min_value=1, max_value=5, value=3,
                key=f"q_{f}", label_visibility="collapsed"
            )

    st.divider()

    # --- Compute and show results ---
    st.markdown('<div class="section-title">Your Top Matches</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Based on your answers, these are your most compatible co-living candidates from our database.</div>', unsafe_allow_html=True)

    live_matches = compute_matches_for_user(user_values, profiles, top_n=top_n)

    for rank, m in enumerate(live_matches, start=1):
        label = m["label"]
        score = m["score"]
        top3 = m["top3"]

        driver_tags = "".join([
            f'<span class="driver-tag">{prettify(f)}</span>'
            for f, sc, w, mode in top3
        ])

        with st.container():
            st.markdown('<div class="match-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 5, 2], gap="medium")

            with c1:
                st.image(avatar_url(label, size=96), width=68)

            with c2:
                st.markdown(f'<div class="match-name">#{rank} &nbsp; {label}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="match-score-text">Compatibility score: <strong>{score:.1f}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f"<div style='margin-top:0.5rem'>Top drivers: {driver_tags}</div>", unsafe_allow_html=True)

                # Show variable comparison for top3
                comparison_lines = []
                for f, sc, w, mode in top3:
                    your_val = user_values[f]
                    their_val = int(profiles[profiles["tenant_label"] == label][f].values[0])
                    mode_icon = "≈" if mode == "similarity" else "⇄"
                    comparison_lines.append(
                        f"**{prettify(f)}**: You {your_val} {mode_icon} Them {their_val} &nbsp; _(score: {sc:.2f})_"
                    )
                with st.expander("📋 Variable breakdown"):
                    for line in comparison_lines:
                        st.markdown(f"- {line}")
                    st.caption("≈ = similarity (closer is better) · ⇄ = complementarity (balanced is better)")

            with c3:
                st.markdown(
                    f"<div style='display:flex;justify-content:flex-end;align-items:center;height:100%'>{donut_svg(score)}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------
# Footer
# ----------------------------
st.markdown("""
<div class="footer">
    Co-living Compatibility Engine · Prototype v2 · Built on synthetic data<br>
    In production: real tenant profiles, feedback loops, and adaptive weight tuning.
</div>
""", unsafe_allow_html=True)
