import math
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
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
# CSS — PropTech Style
# FIX: selettori aggiornati per Streamlit recente
# ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,wght@0,400;0,700;1,400&display=swap');

/* ---- Reset & Base ---- */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1a2332;
}

/* ---- Background PropTech — FIX selettori ---- */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background-color: #f0f4f0 !important;
    background-image:
        radial-gradient(ellipse at 0% 0%, rgba(20,184,166,0.09) 0px, transparent 60%),
        radial-gradient(ellipse at 100% 100%, rgba(15,52,96,0.07) 0px, transparent 60%) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    padding: 2rem 3rem 3rem 3rem !important;
    max-width: 1200px;
}

/* ---- Hero ---- */
.hero {
    background: linear-gradient(135deg, #0f3460 0%, #0d7377 55%, #14b8a6 100%);
    border-radius: 20px;
    padding: 3rem 3.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(13,115,119,0.25);
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -80px; left: 35%;
    width: 350px; height: 350px;
    background: rgba(20,184,166,0.12);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Fraunces', serif;
    font-size: 2.8rem;
    color: #ffffff;
    margin: 0 0 0.6rem 0;
    line-height: 1.1;
    position: relative; z-index: 1;
}
.hero-sub {
    font-size: 1rem;
    color: #99f6e4;
    margin: 0 0 1.75rem 0;
    font-weight: 400;
    position: relative; z-index: 1;
}
.hero-badges {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    position: relative; z-index: 1;
}
.badge {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    color: #e0fdf4;
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    backdrop-filter: blur(8px);
}

/* ---- Section titles ---- */
.section-title {
    font-family: 'Fraunces', serif;
    font-size: 1.5rem;
    color: #0f3460;
    margin: 2rem 0 0.25rem 0;
}
.section-sub {
    font-size: 0.88rem;
    color: #64748b;
    margin-bottom: 1.25rem;
}

/* ---- Cards ---- */
.match-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(15,52,96,0.06);
    transition: box-shadow 0.2s, transform 0.2s;
}
.match-card:hover {
    box-shadow: 0 6px 24px rgba(13,115,119,0.12);
    transform: translateY(-1px);
}
.profile-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 4px rgba(15,52,96,0.06);
}

/* ---- Match name & score ---- */
.match-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f3460;
    margin: 0 0 0.15rem 0;
}
.match-score-text {
    font-size: 0.83rem;
    color: #64748b;
    margin: 0;
}

/* ---- Driver tags ---- */
.driver-tag {
    display: inline-block;
    background: #f0fdfa;
    color: #0d7377;
    border: 1px solid #99f6e4;
    padding: 0.2rem 0.65rem;
    border-radius: 6px;
    font-size: 0.73rem;
    font-weight: 600;
    margin: 0.15rem 0.1rem;
}

/* ---- Explanation box ---- */
.explanation-box {
    background: #f0fdfa;
    border-left: 3px solid #14b8a6;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    font-size: 0.83rem;
    color: #134e4a;
    margin-top: 0.75rem;
}

/* ---- Questionnaire header ---- */
.questionnaire-header {
    background: linear-gradient(135deg, #f0fdfa, #ccfbf1);
    border: 1px solid #99f6e4;
    border-radius: 14px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}
.questionnaire-title {
    font-family: 'Fraunces', serif;
    font-size: 1.4rem;
    color: #0f3460;
    margin: 0 0 0.3rem 0;
}
.questionnaire-sub {
    font-size: 0.88rem;
    color: #0d7377;
    margin: 0;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: #f8fffe !important;
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
    font-weight: 600;
    font-size: 0.88rem;
}

/* ---- Footer ---- */
.footer {
    text-align: center;
    font-size: 0.76rem;
    color: #94a3b8;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
}

hr { border-color: #e2e8f0; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# MATCHING ENGINE
# ============================================================
FEATURES = [
    "cleanliness_level", "noise_tolerance", "sleep_schedule",
    "routine_structure", "WFH_frequency", "sociability_level",
    "guest_tolerance", "privacy_need", "conflict_style", "shared_spaces_usage",
]

WEIGHTS = {
    "cleanliness_level": 1.3, "noise_tolerance": 1.3, "sleep_schedule": 1.2,
    "routine_structure": 1.0, "WFH_frequency": 0.8, "sociability_level": 1.0,
    "guest_tolerance": 1.0,   "privacy_need": 1.1,   "conflict_style": 0.9,
    "shared_spaces_usage": 0.9,
}

SCORING_MODE = {
    "cleanliness_level": "similarity",   "noise_tolerance": "similarity",
    "sleep_schedule": "similarity",      "routine_structure": "similarity",
    "WFH_frequency": "similarity",       "sociability_level": "complementarity",
    "guest_tolerance": "similarity",     "privacy_need": "similarity",
    "conflict_style": "similarity",      "shared_spaces_usage": "complementarity",
}

FEATURE_COLORS = {
    "cleanliness_level": "#14b8a6",  "noise_tolerance": "#0d7377",
    "sleep_schedule": "#6366f1",     "routine_structure": "#f59e0b",
    "WFH_frequency": "#3b82f6",      "sociability_level": "#ec4899",
    "guest_tolerance": "#8b5cf6",    "privacy_need": "#ef4444",
    "conflict_style": "#f97316",     "shared_spaces_usage": "#10b981",
}

FEATURE_LABELS = {
    "cleanliness_level":   ("🧹 Cleanliness",     "1 = relaxed · 5 = very high standards"),
    "noise_tolerance":     ("🔊 Noise tolerance",  "1 = need silence · 5 = fine with noise"),
    "sleep_schedule":      ("🌙 Sleep schedule",   "1 = early bird · 5 = night owl"),
    "routine_structure":   ("📅 Daily routine",    "1 = flexible · 5 = highly structured"),
    "WFH_frequency":       ("💻 Work from home",   "1 = always office · 5 = always home"),
    "sociability_level":   ("🤝 Sociability",      "1 = introverted · 5 = very social"),
    "guest_tolerance":     ("🚪 Guests",           "1 = no guests · 5 = very open"),
    "privacy_need":        ("🔒 Privacy need",     "1 = very open · 5 = needs space"),
    "conflict_style":      ("💬 Conflict style",   "1 = avoidant · 5 = very direct"),
    "shared_spaces_usage": ("🍳 Shared spaces",    "1 = stays in room · 5 = always common areas"),
}


def clamp01(x):
    return float(max(0.0, min(1.0, x)))

def similarity_score(a, b):
    return clamp01(1.0 - abs(a - b) / 4.0)

def complementarity_score(a, b):
    return clamp01(1.0 - abs(a + b - 6) / 4.0)

def feature_score(feature, a, b):
    if SCORING_MODE.get(feature) == "complementarity":
        return complementarity_score(a, b), "complementarity"
    return similarity_score(a, b), "similarity"

def prettify(f):
    return f.replace("_", " ").capitalize()

def _run_matching(user_values, profiles_df, exclude_id=None, top_n=5):
    total_w = sum(WEIGHTS.get(f, 1.0) for f in FEATURES)
    results = []
    for _, row in profiles_df.iterrows():
        if exclude_id is not None and row["user_id"] == exclude_id:
            continue
        ws = 0.0
        details = []
        for f in FEATURES:
            sc, mode = feature_score(f, float(user_values[f]), float(row[f]))
            w = float(WEIGHTS.get(f, 1.0))
            ws += w * sc
            details.append((f, sc, w, mode))
        compat = (ws / total_w) * 100.0
        details.sort(key=lambda x: x[1] * x[2], reverse=True)
        results.append({
            "label": row["tenant_label"],
            "score": round(compat, 2),
            "top3": details[:3],
            "all_details": details,
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]

def compute_matches_for_user(user_values, profiles_df, top_n=5):
    return _run_matching(user_values, profiles_df, exclude_id=None, top_n=top_n)

def compute_matches_from_profile(profile_row, profiles_df, top_n=5):
    user_values = {f: float(profile_row[f]) for f in FEATURES}
    return _run_matching(user_values, profiles_df, exclude_id=profile_row["user_id"], top_n=top_n)


# ============================================================
# HELPERS VISIVI
# ============================================================
def avatar_url(label: str, size: int = 128) -> str:
    seed = urllib.parse.quote(label)
    return f"https://api.dicebear.com/9.x/notionists/png?seed={seed}&size={size}&backgroundColor=f0fdfa"

def donut_svg(p: float, size: int = 80, stroke: int = 9) -> str:
    p = max(0.0, min(100.0, float(p)))
    r = (size - stroke) / 2
    c = 2 * math.pi * r
    offset = c * (1 - p / 100.0)
    color = "#14b8a6" if p >= 80 else "#0d7377" if p >= 60 else "#f59e0b" if p >= 40 else "#ef4444"
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="#e2e8f0" stroke-width="{stroke}"/>
      <circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke}"
              stroke-linecap="round" stroke-dasharray="{c:.2f}" stroke-dashoffset="{offset:.2f}"
              transform="rotate(-90 {size/2} {size/2})"/>
      <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"
            font-family="Plus Jakarta Sans,system-ui" font-size="{int(size*0.2)}"
            font-weight="700" fill="#0f3460">{p:.0f}%</text>
    </svg>"""

def render_segments(val_a: int, color: str, label: str, val_b: int = None):
    """
    FIX: Render barre a segmenti direttamente con st.markdown chiamato UNA VOLTA.
    Costruisce HTML completo e lo renderizza subito.
    """
    # Riga A (tenant / user)
    segs_a = ""
    for i in range(1, 6):
        bg = color if i <= val_a else "#e2e8f0"
        segs_a += f'<div style="flex:1;height:9px;background:{bg};border-radius:3px;margin:0 2px;"></div>'

    # Riga B (match) — opzionale
    row_b = ""
    if val_b is not None:
        segs_b = ""
        for i in range(1, 6):
            bg = "#94a3b8" if i <= val_b else "#f1f5f9"
            segs_b += f'<div style="flex:1;height:6px;background:{bg};border-radius:2px;margin:0 2px;"></div>'
        row_b = f"""
        <div style="display:flex;align-items:center;gap:4px;margin-top:3px;">
          <span style="font-size:0.63rem;color:#94a3b8;width:30px;flex-shrink:0;">them</span>
          <div style="display:flex;flex:1;">{segs_b}</div>
          <span style="font-size:0.68rem;font-weight:600;color:#94a3b8;width:22px;text-align:right;">{val_b}/5</span>
        </div>"""

    you_label = f'<span style="font-size:0.63rem;color:#64748b;width:30px;flex-shrink:0;">{"you" if val_b is not None else ""}</span>'

    html = f"""
    <div style="margin-bottom:0.6rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <span style="font-size:0.76rem;color:#334155;font-weight:500;">{label}</span>
        <span style="font-size:0.72rem;font-weight:700;color:#0f3460;">{val_a}/5</span>
      </div>
      <div style="display:flex;align-items:center;gap:4px;">
        {you_label}
        <div style="display:flex;flex:1;">{segs_a}</div>
      </div>
      {row_b}
    </div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_radar(vals_a, vals_b, labels, title_a="Selected", title_b="Best match", size=280):
    """
    FIX: Usa st.components.v1.html() per renderizzare SVG complessi.
    Questo bypassa i limiti di st.markdown con SVG.
    """
    n = len(vals_a)
    cx, cy = size / 2, size / 2
    r_max = size * 0.36
    r_lbl = size * 0.47

    angles = [math.pi / 2 - 2 * math.pi * i / n for i in range(n)]

    def pt(val, angle):
        ratio = val / 5.0
        return cx + r_max * ratio * math.cos(angle), cy - r_max * ratio * math.sin(angle)

    # Griglia
    grid = ""
    for level in range(1, 6):
        pts = [pt(level, a) for a in angles]
        path = " ".join([f"{'M' if i==0 else 'L'}{x:.1f},{y:.1f}" for i,(x,y) in enumerate(pts)]) + " Z"
        grid += f'<path d="{path}" fill="none" stroke="#e2e8f0" stroke-width="1"/>'

    # Assi
    axes = ""
    for angle in angles:
        x2, y2 = pt(5, angle)
        axes += f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#e2e8f0" stroke-width="1"/>'

    # Poligoni
    poly_a = " ".join([f"{x:.1f},{y:.1f}" for x,y in [pt(v,a) for v,a in zip(vals_a,angles)]])
    poly_b = " ".join([f"{x:.1f},{y:.1f}" for x,y in [pt(v,a) for v,a in zip(vals_b,angles)]])

    # Labels
    lbls = ""
    for i, (angle, lbl) in enumerate(zip(angles, labels)):
        lx = cx + r_lbl * math.cos(angle)
        ly = cy - r_lbl * math.sin(angle)
        anchor = "middle"
        if lx < cx - 8: anchor = "end"
        elif lx > cx + 8: anchor = "start"
        short = lbl[:11]
        lbls += f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" dominant-baseline="middle" font-family="Plus Jakarta Sans,system-ui" font-size="9" fill="#475569" font-weight="500">{short}</text>'

    # Legenda
    legend = f"""
    <rect x="8" y="{size-26}" width="10" height="10" rx="2" fill="#14b8a6" opacity="0.7"/>
    <text x="22" y="{size-18}" font-family="Plus Jakarta Sans,system-ui" font-size="9" fill="#475569">{title_a}</text>
    <rect x="{int(size*0.5)+8}" y="{size-26}" width="10" height="10" rx="2" fill="#0f3460" opacity="0.5"/>
    <text x="{int(size*0.5)+22}" y="{size-18}" font-family="Plus Jakarta Sans,system-ui" font-size="9" fill="#475569">{title_b}</text>"""

    svg = f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
      {grid}{axes}
      <polygon points="{poly_a}" fill="#14b8a6" fill-opacity="0.25" stroke="#14b8a6" stroke-width="2"/>
      <polygon points="{poly_b}" fill="#0f3460" fill-opacity="0.15" stroke="#0f3460" stroke-width="1.5" stroke-dasharray="4,2"/>
      {lbls}{legend}
    </svg>"""

    # FIX: usa components.html per SVG complessi
    components.html(
        f'<div style="display:flex;justify-content:center;align-items:center;">{svg}</div>',
        height=size + 10
    )

def load_data(p, m):
    return pd.read_csv(p), pd.read_csv(m)

def pct(x):
    try: return float(x)
    except: return 0.0


# ============================================================
# HERO
# ============================================================
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


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    top_n = st.slider("Top N matches to show", min_value=1, max_value=15, value=5, step=1)
    st.divider()
    st.markdown("### 📖 How it works")
    st.markdown("""
Each tenant has **10 behavioral variables** (1–5).

Compatibility score uses:
- **Similarity** — closer = better (cleanliness, sleep…)
- **Complementarity** — balanced = better (sociability…)

Variables have different **weights** based on friction impact.
    """)
    st.divider()
    st.markdown("### 📁 Data source")
    use_upload = st.checkbox("Upload custom CSV files", value=False)


# ============================================================
# LOAD DATA
# ============================================================
try:
    if use_upload:
        up_p = st.sidebar.file_uploader("synthetic_profiles_v2.csv", type=["csv"])
        up_m = st.sidebar.file_uploader("top_matches_explained_v2.csv", type=["csv"])
        if up_p is None or up_m is None:
            st.info("Upload both CSV files, or uncheck the option above.")
            st.stop()
        profiles = pd.read_csv(up_p)
        matches  = pd.read_csv(up_m)
    else:
        profiles, matches = load_data("synthetic_profiles_v2.csv", "top_matches_explained_v2.csv")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()


# ============================================================
# TABS
# ============================================================
tab1, tab2 = st.tabs(["🔍 Explore Profiles", "✏️ Try It Yourself"])


# ============================================================
# TAB 1 — Explore Profiles
# ============================================================
with tab1:
    st.markdown('<div class="section-title">Explore Tenant Profiles</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Select a tenant and explore their top matches — computed live.</div>', unsafe_allow_html=True)

    tenant_list = sorted(profiles["tenant_label"].unique().tolist())
    selected_tenant = st.selectbox("Select a tenant", tenant_list, index=0, label_visibility="collapsed")

    sel_row = profiles[profiles["tenant_label"] == selected_tenant].head(1)
    if sel_row.empty:
        st.error("Tenant not found.")
        st.stop()

    # Profile card
    st.markdown('<div class="profile-box">', unsafe_allow_html=True)
    col_av, col_data = st.columns([1, 5], gap="large")
    with col_av:
        st.image(avatar_url(selected_tenant, size=120), width=104)
        st.markdown(
            f"<div style='text-align:center;font-weight:700;font-size:0.9rem;margin-top:0.5rem;color:#0f3460'>"
            f"{selected_tenant}</div>",
            unsafe_allow_html=True
        )
    with col_data:
        for f in FEATURES:
            val = int(sel_row[f].values[0])
            lbl, _ = FEATURE_LABELS[f]
            render_segments(val, FEATURE_COLORS[f], label=lbl)
    st.markdown('</div>', unsafe_allow_html=True)

    # Calcolo match LIVE
    live_results = compute_matches_from_profile(sel_row.iloc[0], profiles, top_n=top_n)

    st.markdown('<div class="section-title">Top Matches</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-sub">Best {top_n} matches for {selected_tenant} — computed live</div>',
        unsafe_allow_html=True
    )

    # Radar best match
    if live_results:
        best = live_results[0]
        best_row = profiles[profiles["tenant_label"] == best["label"]].iloc[0]
        vals_a = [int(sel_row[f].values[0]) for f in FEATURES]
        vals_b = [int(best_row[f]) for f in FEATURES]
        short_labels = [FEATURE_LABELS[f][0].split(" ", 1)[1] for f in FEATURES]

        with st.expander("📡 Radar — profile comparison with best match", expanded=True):
            rc1, rc2 = st.columns([1, 1], gap="large")
            with rc1:
                render_radar(vals_a, vals_b, short_labels,
                             title_a=selected_tenant[:12], title_b=best["label"][:12])
            with rc2:
                st.markdown(f"**{selected_tenant}** vs **{best['label']}**")
                st.markdown(f"Compatibility: **{best['score']:.1f}%**")
                st.divider()
                for f in FEATURES:
                    va = int(sel_row[f].values[0])
                    vb = int(best_row[f])
                    lbl, _ = FEATURE_LABELS[f]
                    render_segments(va, FEATURE_COLORS[f], label=lbl, val_b=vb)

    # Lista match
    for rank, m in enumerate(live_results, start=1):
        label = m["label"]
        score = m["score"]
        top3  = m["top3"]
        driver_tags = "".join([
            f'<span class="driver-tag">{prettify(f)}</span>'
            for f, sc, w, mode in top3
        ])
        driver_text = ", ".join([prettify(f) for f, sc, w, mode in top3])
        match_row = profiles[profiles["tenant_label"] == label].iloc[0]

        with st.container():
            st.markdown('<div class="match-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 5, 2], gap="medium")
            with c1:
                st.image(avatar_url(label, size=96), width=72)
            with c2:
                st.markdown(f'<div class="match-name">#{rank} &nbsp; {label}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="match-score-text">Compatibility: <strong>{score:.1f}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f"<div style='margin-top:0.4rem'>Top drivers: {driver_tags}</div>", unsafe_allow_html=True)
                st.markdown(
                    f'<div class="explanation-box">High compatibility driven by {driver_text}.</div>',
                    unsafe_allow_html=True
                )
            with c3:
                st.markdown(
                    f"<div style='display:flex;justify-content:flex-end;align-items:center;height:100%'>"
                    f"{donut_svg(score)}</div>",
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("📋 Variable breakdown"):
                for f, sc, w, mode in m["all_details"]:
                    va = int(sel_row[f].values[0])
                    vb = int(match_row[f])
                    lbl, _ = FEATURE_LABELS[f]
                    mode_icon = "≈" if mode == "similarity" else "⇄"
                    render_segments(va, FEATURE_COLORS[f], label=f"{lbl} {mode_icon}", val_b=vb)
                st.caption("≈ similarity (closer = better) · ⇄ complementarity (balanced = better) · grey = their value")


# ============================================================
# TAB 2 — Try It Yourself
# ============================================================
with tab2:
    st.markdown("""
    <div class="questionnaire-header">
      <div class="questionnaire-title">Find Your Co-living Matches</div>
      <div class="questionnaire-sub">Answer 10 quick questions · See your matches in real time</div>
    </div>
    """, unsafe_allow_html=True)

    user_values = {}
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        for f in FEATURES[:5]:
            lbl, desc = FEATURE_LABELS[f]
            st.markdown(f"**{lbl}**")
            st.caption(desc)
            user_values[f] = st.slider(lbl, 1, 5, 3, key=f"q_{f}", label_visibility="collapsed")

    with col_right:
        for f in FEATURES[5:]:
            lbl, desc = FEATURE_LABELS[f]
            st.markdown(f"**{lbl}**")
            st.caption(desc)
            user_values[f] = st.slider(lbl, 1, 5, 3, key=f"q_{f}", label_visibility="collapsed")

    st.divider()
    st.markdown('<div class="section-title">Your Top Matches</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Computed live against all 300 profiles in the database.</div>',
        unsafe_allow_html=True
    )

    live_matches = compute_matches_for_user(user_values, profiles, top_n=top_n)

    # Radar Tab2
    if live_matches:
        best2 = live_matches[0]
        best2_row = profiles[profiles["tenant_label"] == best2["label"]].iloc[0]
        vals_u  = [user_values[f] for f in FEATURES]
        vals_b2 = [int(best2_row[f]) for f in FEATURES]
        short_labels2 = [FEATURE_LABELS[f][0].split(" ", 1)[1] for f in FEATURES]

        with st.expander("📡 Radar — your profile vs best match", expanded=True):
            rc1, rc2 = st.columns([1, 1], gap="large")
            with rc1:
                render_radar(vals_u, vals_b2, short_labels2,
                             title_a="You", title_b=best2["label"][:12])
            with rc2:
                st.markdown(f"**You** vs **{best2['label']}**")
                st.markdown(f"Compatibility: **{best2['score']:.1f}%**")
                st.divider()
                for f in FEATURES:
                    vu = user_values[f]
                    vb = int(best2_row[f])
                    lbl, _ = FEATURE_LABELS[f]
                    render_segments(vu, FEATURE_COLORS[f], label=lbl, val_b=vb)

    # Lista match Tab2
    for rank, m in enumerate(live_matches, start=1):
        label = m["label"]
        score = m["score"]
        top3  = m["top3"]
        driver_tags = "".join([
            f'<span class="driver-tag">{prettify(f)}</span>'
            for f, sc, w, mode in top3
        ])
        match_row = profiles[profiles["tenant_label"] == label].iloc[0]

        with st.container():
            st.markdown('<div class="match-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 5, 2], gap="medium")
            with c1:
                st.image(avatar_url(label, size=96), width=72)
            with c2:
                st.markdown(f'<div class="match-name">#{rank} &nbsp; {label}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="match-score-text">Compatibility: <strong>{score:.1f}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f"<div style='margin-top:0.4rem'>Top drivers: {driver_tags}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(
                    f"<div style='display:flex;justify-content:flex-end;align-items:center;height:100%'>"
                    f"{donut_svg(score)}</div>",
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("📋 Variable breakdown"):
                for f, sc, w, mode in m["all_details"]:
                    vu = user_values[f]
                    vb = int(match_row[f])
                    lbl, _ = FEATURE_LABELS[f]
                    mode_icon = "≈" if mode == "similarity" else "⇄"
                    render_segments(vu, FEATURE_COLORS[f], label=f"{lbl} {mode_icon}", val_b=vb)
                st.caption("≈ similarity · ⇄ complementarity · grey = their value")


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    Co-living Compatibility Engine · Prototype v3 · Built on synthetic data<br>
    In production: real tenant profiles, feedback loops, adaptive weight tuning.
</div>
""", unsafe_allow_html=True)
