import math
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

st.set_page_config(
    page_title="Tenant Matching — Co-living Compatibility Engine",
    page_icon="🏡",
    layout="wide",
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,wght@0,400;0,700;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1a2332;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background-color: #f0f4f0 !important;
    background-image:
        radial-gradient(ellipse at 0% 0%, rgba(20,184,166,0.09) 0px, transparent 60%),
        radial-gradient(ellipse at 100% 100%, rgba(15,52,96,0.07) 0px, transparent 60%) !important;
}
[data-testid="stHeader"] { background: transparent !important; }

.block-container { padding: 2rem 3rem 3rem 3rem !important; max-width: 1200px; }

.hero {
    background: linear-gradient(135deg, #0f3460 0%, #0d7377 55%, #14b8a6 100%);
    border-radius: 20px; padding: 3rem 3.5rem; margin-bottom: 2rem;
    position: relative; overflow: hidden;
    box-shadow: 0 20px 60px rgba(13,115,119,0.25);
}
.hero::before { content:''; position:absolute; top:-60px; right:-60px;
    width:280px; height:280px; background:rgba(255,255,255,0.05); border-radius:50%; }
.hero::after { content:''; position:absolute; bottom:-80px; left:35%;
    width:350px; height:350px; background:rgba(20,184,166,0.12); border-radius:50%; }
.hero-title { font-family:'Fraunces',serif; font-size:2.8rem; color:#fff;
    margin:0 0 0.6rem 0; line-height:1.1; position:relative; z-index:1; }
.hero-sub { font-size:1rem; color:#99f6e4; margin:0 0 1.75rem 0;
    font-weight:400; position:relative; z-index:1; }
.hero-badges { display:flex; gap:0.75rem; flex-wrap:wrap; position:relative; z-index:1; }
.badge { background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.2);
    color:#e0fdf4; padding:0.35rem 0.9rem; border-radius:20px;
    font-size:0.78rem; font-weight:600; backdrop-filter:blur(8px); }

.section-title { font-family:'Fraunces',serif; font-size:1.5rem; color:#0f3460;
    margin:2rem 0 0.25rem 0; }
.section-sub { font-size:0.88rem; color:#64748b; margin-bottom:1.25rem; }

.match-card { background:#fff; border:1px solid #e2e8f0; border-radius:14px;
    padding:1.25rem 1.5rem; margin-bottom:1rem;
    box-shadow:0 1px 4px rgba(15,52,96,0.06); }
.profile-box { background:#fff; border:1px solid #e2e8f0; border-radius:14px;
    padding:1.5rem 1.75rem; margin-bottom:1.5rem;
    box-shadow:0 1px 4px rgba(15,52,96,0.06); }

.match-name { font-size:1.05rem; font-weight:700; color:#0f3460; margin:0 0 0.15rem 0; }
.match-score-text { font-size:0.83rem; color:#64748b; margin:0; }

.driver-tag { display:inline-block; background:#f0fdfa; color:#0d7377;
    border:1px solid #99f6e4; padding:0.2rem 0.65rem; border-radius:6px;
    font-size:0.73rem; font-weight:600; margin:0.15rem 0.1rem; }

.explanation-box { background:#f0fdfa; border-left:3px solid #14b8a6;
    border-radius:0 8px 8px 0; padding:0.75rem 1rem;
    font-size:0.83rem; color:#134e4a; margin-top:0.75rem; }

.questionnaire-header { background:linear-gradient(135deg,#f0fdfa,#ccfbf1);
    border:1px solid #99f6e4; border-radius:14px; padding:1.5rem 2rem; margin-bottom:1.5rem; }
.questionnaire-title { font-family:'Fraunces',serif; font-size:1.4rem;
    color:#0f3460; margin:0 0 0.3rem 0; }
.questionnaire-sub { font-size:0.88rem; color:#0d7377; margin:0; }

section[data-testid="stSidebar"] { background:#f8fffe !important; border-right:1px solid #e2e8f0; }
section[data-testid="stSidebar"] .block-container { padding:1.5rem 1.25rem !important; }

.stTabs [data-baseweb="tab-list"] { gap:0.5rem; background:transparent; }
.stTabs [data-baseweb="tab"] { border-radius:8px 8px 0 0; font-weight:600; font-size:0.88rem; }

.footer { text-align:center; font-size:0.76rem; color:#94a3b8;
    margin-top:3rem; padding-top:1.5rem; border-top:1px solid #e2e8f0; }
hr { border-color:#e2e8f0; margin:1.5rem 0; }
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
    "cleanliness_level":1.3, "noise_tolerance":1.3, "sleep_schedule":1.2,
    "routine_structure":1.0, "WFH_frequency":0.8,  "sociability_level":1.0,
    "guest_tolerance":1.0,   "privacy_need":1.1,   "conflict_style":0.9,
    "shared_spaces_usage":0.9,
}
SCORING_MODE = {
    "cleanliness_level":"similarity",   "noise_tolerance":"similarity",
    "sleep_schedule":"similarity",      "routine_structure":"similarity",
    "WFH_frequency":"similarity",       "sociability_level":"complementarity",
    "guest_tolerance":"similarity",     "privacy_need":"similarity",
    "conflict_style":"similarity",      "shared_spaces_usage":"complementarity",
}
FEATURE_LABELS = {
    "cleanliness_level":   ("🧹 Cleanliness",    "1 = relaxed · 5 = high standards"),
    "noise_tolerance":     ("🔊 Noise tolerance", "1 = need silence · 5 = fine with noise"),
    "sleep_schedule":      ("🌙 Sleep schedule",  "1 = early bird · 5 = night owl"),
    "routine_structure":   ("📅 Daily routine",   "1 = flexible · 5 = structured"),
    "WFH_frequency":       ("💻 Work from home",  "1 = always office · 5 = always home"),
    "sociability_level":   ("🤝 Sociability",     "1 = introverted · 5 = very social"),
    "guest_tolerance":     ("🚪 Guests",          "1 = no guests · 5 = very open"),
    "privacy_need":        ("🔒 Privacy need",    "1 = very open · 5 = needs space"),
    "conflict_style":      ("💬 Conflict style",  "1 = avoidant · 5 = very direct"),
    "shared_spaces_usage": ("🍳 Shared spaces",   "1 = stays in room · 5 = common areas"),
}

TEAL = "#14b8a6"
TEAL_LIGHT = "#99f6e4"
GREY_SEG = "#e2e8f0"
GREY_MATCH = "#94a3b8"
GREY_MATCH_EMPTY = "#f1f5f9"


def clamp01(x): return float(max(0.0, min(1.0, x)))
def sim(a, b):  return clamp01(1.0 - abs(a-b)/4.0)
def comp(a, b): return clamp01(1.0 - abs(a+b-6)/4.0)

def feature_score(f, a, b):
    if SCORING_MODE.get(f) == "complementarity":
        return comp(a, b), "complementarity"
    return sim(a, b), "similarity"

def prettify(f): return f.replace("_"," ").capitalize()

def _run(user_vals, df, exclude_id=None, top_n=5):
    tw = sum(WEIGHTS.get(f,1.0) for f in FEATURES)
    results = []
    for _, row in df.iterrows():
        if exclude_id is not None and row["user_id"] == exclude_id:
            continue
        ws, details = 0.0, []
        for f in FEATURES:
            sc, mode = feature_score(f, float(user_vals[f]), float(row[f]))
            w = float(WEIGHTS.get(f,1.0))
            ws += w * sc
            details.append((f, sc, w, mode))
        details.sort(key=lambda x: x[1]*x[2], reverse=True)
        results.append({"label":row["tenant_label"], "score":round(ws/tw*100,2),
                        "top3":details[:3], "all_details":details})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]

def match_from_profile(row, df, top_n=5):
    return _run({f:float(row[f]) for f in FEATURES}, df, exclude_id=row["user_id"], top_n=top_n)

def match_from_user(vals, df, top_n=5):
    return _run(vals, df, top_n=top_n)


# ============================================================
# HTML HELPERS — tutto costruito come stringa, st.markdown UNA VOLTA
# ============================================================
def avatar_url(label, size=128):
    seed = urllib.parse.quote(label)
    return f"https://api.dicebear.com/9.x/notionists/png?seed={seed}&size={size}&backgroundColor=f0fdfa"

def donut_svg(p, size=80, stroke=9):
    p = max(0.0, min(100.0, float(p)))
    r = (size-stroke)/2
    c = 2*math.pi*r
    off = c*(1-p/100.0)
    color = TEAL if p>=80 else "#0d7377" if p>=60 else "#f59e0b" if p>=40 else "#ef4444"
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="{GREY_SEG}" stroke-width="{stroke}"/>'
            f'<circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke}"'
            f' stroke-linecap="round" stroke-dasharray="{c:.2f}" stroke-dashoffset="{off:.2f}"'
            f' transform="rotate(-90 {size/2} {size/2})"/>'
            f'<text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"'
            f' font-family="Plus Jakarta Sans,system-ui" font-size="{int(size*0.2)}"'
            f' font-weight="700" fill="#0f3460">{p:.0f}%</text></svg>')

def seg_row_html(val, color, empty_color, height=9):
    """Una riga di 5 segmenti."""
    segs = ""
    for i in range(1, 6):
        bg = color if i <= val else empty_color
        segs += f'<div style="flex:1;height:{height}px;background:{bg};border-radius:3px;margin:0 2px;"></div>'
    return f'<div style="display:flex;flex:1;">{segs}</div>'

def single_var_html(label_txt, val_a, val_b=None, mode_icon=""):
    """
    HTML per una singola variabile con barre a segmenti.
    val_b opzionale = valore del match a confronto.
    Restituisce stringa HTML — chiamare con st.markdown(html, unsafe_allow_html=True).
    """
    row_a = seg_row_html(val_a, TEAL, GREY_SEG, height=9)
    you_lbl = '<span style="font-size:0.62rem;color:#64748b;width:30px;flex-shrink:0;"></span>'

    row_b_html = ""
    if val_b is not None:
        row_b = seg_row_html(val_b, GREY_MATCH, GREY_MATCH_EMPTY, height=6)
        row_b_html = (
            f'<div style="display:flex;align-items:center;gap:4px;margin-top:3px;">'
            f'<span style="font-size:0.62rem;color:#94a3b8;width:30px;flex-shrink:0;">them</span>'
            f'{row_b}'
            f'<span style="font-size:0.67rem;font-weight:600;color:#94a3b8;width:22px;text-align:right;">{val_b}/5</span>'
            f'</div>'
        )
        you_lbl = '<span style="font-size:0.62rem;color:#64748b;width:30px;flex-shrink:0;">you</span>'

    return (
        f'<div style="margin-bottom:0.55rem;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
        f'<span style="font-size:0.76rem;color:#334155;font-weight:500;">{label_txt}{(" "+mode_icon) if mode_icon else ""}</span>'
        f'<span style="font-size:0.72rem;font-weight:700;color:#0f3460;">{val_a}/5</span>'
        f'</div>'
        f'<div style="display:flex;align-items:center;gap:4px;">'
        f'{you_lbl}{row_a}'
        f'</div>'
        f'{row_b_html}'
        f'</div>'
    )

def vars_grid_html(features_vals_a, features_vals_b=None, show_mode=False):
    """
    Griglia 2 colonne di variabili.
    features_vals_a: list of (feature, val_a)
    features_vals_b: dict feature->val_b opzionale
    Restituisce HTML completo da passare a st.markdown.
    """
    n = len(features_vals_a)
    mid = math.ceil(n / 2)
    left  = features_vals_a[:mid]
    right = features_vals_a[mid:]

    def col_html(items):
        h = ""
        for f, va in items:
            lbl, _ = FEATURE_LABELS[f]
            vb = features_vals_b.get(f) if features_vals_b else None
            mode_icon = ""
            if show_mode:
                mode_icon = "≈" if SCORING_MODE.get(f) == "similarity" else "⇄"
            h += single_var_html(lbl, va, val_b=vb, mode_icon=mode_icon)
        return h

    lh = col_html(left)
    rh = col_html(right)

    return (
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem 2rem;margin-top:0.5rem;">'
        f'<div>{lh}</div>'
        f'<div>{rh}</div>'
        f'</div>'
    )

def radar_html(vals_a, vals_b, labels, title_a="Tenant", title_b="Best match", size=400):
    """
    SVG radar chart — canvas expanded with horizontal/vertical padding so all
    10 labels are fully visible even for near-horizontal axes (cos≈0.95).
    The radar polygon coordinate space stays size×size; the SVG element is
    wider/taller to give room for label text that extends beyond the radar area.
    """
    n = len(vals_a)
    # Padding around the radar polygon to accommodate label text
    pad_h, pad_v = 120, 50          # extra pixels left/right and top/bottom
    svg_w = size + 2 * pad_h        # total SVG width  (e.g. 640)
    svg_h = size + 2 * pad_v        # total SVG height (e.g. 500)
    cx, cy = svg_w / 2, svg_h / 2  # radar centre in the expanded canvas
    r_max = size * 0.30             # polygon max radius (unchanged)
    r_lbl = size * 0.47             # label distance from centre (unchanged)
    angles = [math.pi/2 - 2*math.pi*i/n for i in range(n)]

    def pt(val, angle):
        ratio = val / 5.0
        return cx + r_max*ratio*math.cos(angle), cy - r_max*ratio*math.sin(angle)

    def pt_lbl(angle, extra=0):
        r = r_lbl + extra
        return cx + r*math.cos(angle), cy - r*math.sin(angle)

    # Grid polygons — levels 1-5
    grid = ""
    for level in range(1, 6):
        pts = [pt(level, a) for a in angles]
        path = " ".join([f"{'M' if i==0 else 'L'}{x:.1f},{y:.1f}" for i,(x,y) in enumerate(pts)]) + " Z"
        op = "0.5" if level == 5 else "0.18"
        sw = "1" if level == 5 else "0.7"
        grid += f'<path d="{path}" fill="none" stroke="#94a3b8" stroke-width="{sw}" stroke-opacity="{op}"/>'

    # Axes
    axes = "".join([
        f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{pt(5,a)[0]:.1f}" y2="{pt(5,a)[1]:.1f}" stroke="#cbd5e1" stroke-width="0.8"/>'
        for a in angles
    ])

    # Filled polygons
    pts_a = [pt(v, a) for v, a in zip(vals_a, angles)]
    pts_b = [pt(v, a) for v, a in zip(vals_b, angles)]
    poly_a = " ".join([f"{x:.1f},{y:.1f}" for x,y in pts_a])
    poly_b = " ".join([f"{x:.1f},{y:.1f}" for x,y in pts_b])

    # Dots on polygon A vertices (teal, larger)
    dots_a = "".join([
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{TEAL}" stroke="white" stroke-width="1.5"/>'
        for x, y in pts_a
    ])
    # Dots on polygon B vertices (navy, smaller)
    dots_b = "".join([
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="#0f3460" stroke="white" stroke-width="1" opacity="0.7"/>'
        for x, y in pts_b
    ])

    # Numeric value labels next to polygon A vertices
    val_labels = ""
    for i, (val, angle) in enumerate(zip(vals_a, angles)):
        x, y = pt(val, angle)
        offset = 18
        nx = x + offset * math.cos(angle)
        ny = y - offset * math.sin(angle)
        val_labels += (
            f'<text x="{nx:.1f}" y="{ny:.1f}" text-anchor="middle" dominant-baseline="middle" '
            f'font-family="Plus Jakarta Sans,system-ui" font-size="10" font-weight="700" fill="{TEAL}">{val}</text>'
        )

    # Variable labels — full text, smart anchor/dy
    lbls = ""
    for i, (angle, lbl) in enumerate(zip(angles, labels)):
        lx, ly = pt_lbl(angle)
        if abs(lx - cx) < 15:
            anchor = "middle"
        elif lx < cx:
            anchor = "end"
        else:
            anchor = "start"
        dy = 0
        if ly < cy - r_max * 0.7:
            dy = -6
        elif ly > cy + r_max * 0.7:
            dy = 6
        lbls += (
            f'<text x="{lx:.1f}" y="{ly+dy:.1f}" text-anchor="{anchor}" '
            f'dominant-baseline="middle" font-family="Plus Jakarta Sans,system-ui" '
            f'font-size="11" fill="#334155" font-weight="500">{lbl}</text>'
        )

    # Legend — pinned to bottom of expanded canvas
    leg_y = svg_h - 20
    legend = (
        f'<rect x="12" y="{leg_y-8}" width="12" height="12" rx="3" fill="{TEAL}" opacity="0.85"/>'
        f'<text x="28" y="{leg_y}" font-family="Plus Jakarta Sans,system-ui" font-size="10" fill="#475569" font-weight="500">{title_a}</text>'
        f'<rect x="{int(svg_w*0.42)}" y="{leg_y-8}" width="12" height="12" rx="3" fill="#0f3460" opacity="0.6"/>'
        f'<text x="{int(svg_w*0.42)+16}" y="{leg_y}" font-family="Plus Jakarta Sans,system-ui" font-size="10" fill="#475569" font-weight="500">{title_b}</text>'
    )

    svg = (
        f'<svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg">'
        f'{grid}{axes}'
        f'<polygon points="{poly_b}" fill="#0f3460" fill-opacity="0.10" stroke="#0f3460" stroke-width="1.5" stroke-dasharray="5,3"/>'
        f'<polygon points="{poly_a}" fill="{TEAL}" fill-opacity="0.22" stroke="{TEAL}" stroke-width="2.5"/>'
        f'{dots_b}{dots_a}{val_labels}{lbls}{legend}'
        f'</svg>'
    )
    return f'<div style="display:flex;justify-content:center;padding:4px 0;">{svg}</div>'


def verbal_explanation_html(name_a, name_b, score, all_details, vals_a_dict, vals_b_dict):
    """
    Genera una spiegazione verbale chiara del match in inglese.
    Restituisce HTML per st.markdown.
    """
    # Calcola affinità e differenze principali
    strong = []   # score >= 0.75
    medium = []   # score 0.50-0.75
    weak   = []   # score < 0.50

    for f, sc, w, mode in all_details:
        va = vals_a_dict[f]
        vb = vals_b_dict[f]
        lbl = FEATURE_LABELS[f][0].split(" ", 1)[1]  # senza emoji
        if sc >= 0.75:
            strong.append((lbl, va, vb, mode, sc))
        elif sc >= 0.50:
            medium.append((lbl, va, vb, mode, sc))
        else:
            weak.append((lbl, va, vb, mode, sc))

    # Paragrafo introduttivo
    if score >= 85:
        intro = f"<strong>{name_a}</strong> and <strong>{name_b}</strong> are an excellent match ({score:.1f}%). They share very similar lifestyles across most dimensions, which typically leads to low friction and a positive co-living experience."
    elif score >= 70:
        intro = f"<strong>{name_a}</strong> and <strong>{name_b}</strong> are a good match ({score:.1f}%). They align well on several key dimensions, with only a few areas where some adaptation may be needed."
    else:
        intro = f"<strong>{name_a}</strong> and <strong>{name_b}</strong> have a moderate compatibility ({score:.1f}%). There are meaningful differences to be aware of before placing them together."

    # Punti di forza
    strengths_html = ""
    if strong:
        items = "".join([
            f'<li><strong>{lbl}</strong>: both score {va}/5 and {vb}/5 — '
            f'{"very similar" if mode == "similarity" else "well balanced"}</li>'
            for lbl, va, vb, mode, sc in strong[:3]
        ])
        strengths_html = f"""
        <div style="margin-top:0.9rem;">
          <div style="font-size:0.78rem;font-weight:700;color:#0d7377;margin-bottom:0.35rem;
                      text-transform:uppercase;letter-spacing:0.05em;">Strong alignments</div>
          <ul style="margin:0;padding-left:1.2rem;font-size:0.82rem;color:#334155;line-height:1.7;">{items}</ul>
        </div>"""

    # Aree di attenzione
    tension_html = ""
    if weak:
        items = "".join([
            f'<li><strong>{lbl}</strong>: {va}/5 vs {vb}/5 — '
            f'{"different preferences, worth discussing" if mode == "similarity" else "similar energy level, may compete for shared spaces"}</li>'
            for lbl, va, vb, mode, sc in weak[:2]
        ])
        tension_html = f"""
        <div style="margin-top:0.75rem;">
          <div style="font-size:0.78rem;font-weight:700;color:#f59e0b;margin-bottom:0.35rem;
                      text-transform:uppercase;letter-spacing:0.05em;">Areas to watch</div>
          <ul style="margin:0;padding-left:1.2rem;font-size:0.82rem;color:#334155;line-height:1.7;">{items}</ul>
        </div>"""

    return f"""
    <div style="background:#f8fffe;border:1px solid #ccfbf1;border-radius:10px;
                padding:1rem 1.25rem;margin-top:0.75rem;">
      <div style="font-size:0.82rem;color:#1a2332;line-height:1.65;">{intro}</div>
      {strengths_html}
      {tension_html}
    </div>"""


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

Compatibility uses:
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
    else:
        profiles = pd.read_csv("synthetic_profiles_v2.csv")
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

    # Profile card — barre 2 colonne
    st.markdown('<div class="profile-box">', unsafe_allow_html=True)
    c_av, c_bars = st.columns([1, 5], gap="large")
    with c_av:
        st.image(avatar_url(selected_tenant, 120), width=104)
        st.markdown(
            f"<div style='text-align:center;font-weight:700;font-size:0.9rem;"
            f"margin-top:0.5rem;color:#0f3460;'>{selected_tenant}</div>",
            unsafe_allow_html=True
        )
    with c_bars:
        fva = [(f, int(sel_row[f].values[0])) for f in FEATURES]
        st.markdown(vars_grid_html(fva), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Calcola match live
    live = match_from_profile(sel_row.iloc[0], profiles, top_n=top_n)

    st.markdown('<div class="section-title">Top Matches</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-sub">Best {top_n} matches for {selected_tenant} — computed live</div>',
        unsafe_allow_html=True
    )

    # Radar best match
    if live:
        best = live[0]
        best_row = profiles[profiles["tenant_label"] == best["label"]].iloc[0]
        va_list = [int(sel_row[f].values[0]) for f in FEATURES]
        vb_list = [int(best_row[f]) for f in FEATURES]
        short_lbls = [FEATURE_LABELS[f][0].split(" ",1)[1].replace(" ","\n") if False else FEATURE_LABELS[f][0].split(" ",1)[1] for f in FEATURES]

        with st.expander(f"📡 Radar — {selected_tenant} vs {best['label']} ({best['score']:.1f}%)", expanded=True):
            radar_col, info_col = st.columns([3, 2], gap="large")
            with radar_col:
                components.html(
                    radar_html(va_list, vb_list, short_lbls,
                               title_a=selected_tenant[:14], title_b=best["label"][:14]),
                    height=520
                )
            with info_col:
                st.markdown(f"**{selected_tenant}** *(teal)* vs **{best['label']}** *(dashed)*")
                st.markdown(f"Compatibility score: **{best['score']:.1f}%**")
                st.caption("The radar shows how the two tenants compare across all 10 variables. "
                           "Overlapping areas = compatible. Diverging spikes = differences.")
                st.divider()
                fva_b = [(f, int(sel_row[f].values[0])) for f in FEATURES]
                fvb_dict = {f: int(best_row[f]) for f in FEATURES}
                st.markdown(vars_grid_html(fva_b, fvb_dict), unsafe_allow_html=True)
                st.caption("Teal = selected tenant · Grey = best match · ≈ similarity · ⇄ complementarity")
                # Verbal explanation
                va_dict = {f: int(sel_row[f].values[0]) for f in FEATURES}
                vb_dict_exp = {f: int(best_row[f]) for f in FEATURES}
                all_det = best["all_details"]
                st.markdown(
                    verbal_explanation_html(selected_tenant, best["label"], best["score"],
                                           all_det, va_dict, vb_dict_exp),
                    unsafe_allow_html=True
                )

    # Lista match
    for rank, m in enumerate(live, start=1):
        label = m["label"]
        score = m["score"]
        driver_tags = "".join([
            f'<span class="driver-tag">{prettify(f)}</span>'
            for f, sc, w, mode in m["top3"]
        ])
        driver_text = ", ".join([prettify(f) for f, sc, w, mode in m["top3"]])
        match_row = profiles[profiles["tenant_label"] == label].iloc[0]

        st.markdown('<div class="match-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 5, 2], gap="medium")
        with c1:
            st.image(avatar_url(label, 96), width=72)
        with c2:
            st.markdown(f'<div class="match-name">#{rank} &nbsp; {label}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="match-score-text">Compatibility: <strong>{score:.1f}%</strong></div>', unsafe_allow_html=True)
            st.markdown(f"<div style='margin-top:0.4rem;'>Top drivers: {driver_tags}</div>", unsafe_allow_html=True)
            st.markdown(f'<div class="explanation-box">High compatibility driven by {driver_text}.</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(
                f"<div style='display:flex;justify-content:flex-end;align-items:center;height:100%;'>"
                f"{donut_svg(score)}</div>",
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Breakdown — 2 colonne, HTML unico
        with st.expander("📋 Variable breakdown"):
            fva2 = [(f, int(sel_row[f].values[0])) for f in FEATURES]
            fvb2 = {f: int(match_row[f]) for f in FEATURES}
            st.markdown(vars_grid_html(fva2, fvb2, show_mode=True), unsafe_allow_html=True)
            st.caption("Teal = selected tenant · Grey = match · ≈ similarity · ⇄ complementarity")


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

    user_vals = {}
    ql, qr = st.columns(2, gap="large")
    with ql:
        for f in FEATURES[:5]:
            lbl, desc = FEATURE_LABELS[f]
            st.markdown(f"**{lbl}**")
            st.caption(desc)
            user_vals[f] = st.slider(lbl, 1, 5, 3, key=f"q_{f}", label_visibility="collapsed")
    with qr:
        for f in FEATURES[5:]:
            lbl, desc = FEATURE_LABELS[f]
            st.markdown(f"**{lbl}**")
            st.caption(desc)
            user_vals[f] = st.slider(lbl, 1, 5, 3, key=f"q_{f}", label_visibility="collapsed")

    st.divider()
    st.markdown('<div class="section-title">Your Top Matches</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Computed live against all 300 profiles.</div>', unsafe_allow_html=True)

    live2 = match_from_user(user_vals, profiles, top_n=top_n)

    # Radar Tab2
    if live2:
        best2 = live2[0]
        best2_row = profiles[profiles["tenant_label"] == best2["label"]].iloc[0]
        vu_list  = [user_vals[f] for f in FEATURES]
        vb2_list = [int(best2_row[f]) for f in FEATURES]
        short_lbls2 = [FEATURE_LABELS[f][0].split(" ",1)[1] for f in FEATURES]

        with st.expander(f"📡 Radar — You vs {best2['label']} ({best2['score']:.1f}%)", expanded=True):
            rc1, rc2 = st.columns([3, 2], gap="large")
            with rc1:
                components.html(
                    radar_html(vu_list, vb2_list, short_lbls2,
                               title_a="You", title_b=best2["label"][:14]),
                    height=520
                )
            with rc2:
                st.markdown(f"**You** *(teal)* vs **{best2['label']}** *(dashed)*")
                st.markdown(f"Compatibility score: **{best2['score']:.1f}%**")
                st.caption("The radar shows how you compare across all 10 variables.")
                st.divider()
                fvu = [(f, user_vals[f]) for f in FEATURES]
                fvb2_dict = {f: int(best2_row[f]) for f in FEATURES}
                st.markdown(vars_grid_html(fvu, fvb2_dict), unsafe_allow_html=True)
                st.caption("Teal = you · Grey = best match")
                # Verbal explanation
                vu_dict = {f: user_vals[f] for f in FEATURES}
                vb2_dict_exp = {f: int(best2_row[f]) for f in FEATURES}
                all_det2 = best2["all_details"]
                st.markdown(
                    verbal_explanation_html("You", best2["label"], best2["score"],
                                           all_det2, vu_dict, vb2_dict_exp),
                    unsafe_allow_html=True
                )

    # Lista match Tab2
    for rank, m in enumerate(live2, start=1):
        label = m["label"]
        score = m["score"]
        driver_tags = "".join([
            f'<span class="driver-tag">{prettify(f)}</span>'
            for f, sc, w, mode in m["top3"]
        ])
        match_row = profiles[profiles["tenant_label"] == label].iloc[0]

        st.markdown('<div class="match-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 5, 2], gap="medium")
        with c1:
            st.image(avatar_url(label, 96), width=72)
        with c2:
            st.markdown(f'<div class="match-name">#{rank} &nbsp; {label}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="match-score-text">Compatibility: <strong>{score:.1f}%</strong></div>', unsafe_allow_html=True)
            st.markdown(f"<div style='margin-top:0.4rem;'>Top drivers: {driver_tags}</div>", unsafe_allow_html=True)
        with c3:
            st.markdown(
                f"<div style='display:flex;justify-content:flex-end;align-items:center;height:100%;'>"
                f"{donut_svg(score)}</div>",
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("📋 Variable breakdown"):
            fvu2 = [(f, user_vals[f]) for f in FEATURES]
            fvb3 = {f: int(match_row[f]) for f in FEATURES}
            st.markdown(vars_grid_html(fvu2, fvb3, show_mode=True), unsafe_allow_html=True)
            st.caption("Teal = you · Grey = match · ≈ similarity · ⇄ complementarity")


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    Co-living Compatibility Engine · Prototype v3 · Built on synthetic data<br>
    In production: real tenant profiles, feedback loops, adaptive weight tuning.
</div>
""", unsafe_allow_html=True)
