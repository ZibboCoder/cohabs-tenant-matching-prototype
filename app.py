import hashlib
import pandas as pd
import streamlit as st
import urllib.parse


# ----------------------------
# Page
# ----------------------------
st.set_page_config(
    page_title="Cohabs — Tenant Matching Demo",
    page_icon="🏡",
    layout="wide",
)

# --- Light theme & visual polish (simple CSS overrides) ---
st.markdown(
    """
    <style>
    /* page background and container */
    .reportview-container, .main {
        background: #ffffff;
        color: #111827;
    }
    /* sidebar style */
    .css-1lcbmhc.e1fqkh3o1 { background: #f7f8fa; }
    /* cards - increase padding and soften border */
    .stContainer > .stMarkdown, .stExpander {
        border-radius: 10px;
    }
    /* make the "card" look lighter */
    .stContainer {
        padding: 12px;
    }
    /* smaller table header text */
    .stDataFrame thead th {
        font-weight: 700;
    }
    /* reduce default streamlit spacing for compactness */
    .css-12oz5g7 { padding-top: 6px; }
    /* ensure monospace code area remains subtle */
    .stCodeBlock pre { background: #f5f5f5; color: #0f172a; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏡 Cohabs — Tenant Matching Demo")
st.caption("Prototype basato su dati sintetici (demo). Matching con pesi + explainability (top drivers).")

# ----------------------------
# Helpers
# ----------------------------
def stable_color(seed_str: str) -> tuple[int, int, int]:
    h = hashlib.md5(seed_str.encode("utf-8")).hexdigest()
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r, g, b)

def avatar_url(label: str, size: int = 128, style: str = "personas") -> str:
    """
    Realistic-looking avatar (static) generated via DiceBear.
    Deterministic: same label => same face.
    """
    seed = urllib.parse.quote(label)
    return f"https://api.dicebear.com/9.x/{style}/png?seed={seed}&size={size}"

def donut(percent_value: float, size: int = 88, stroke: int = 10) -> str:
    """
    Returns an inline SVG donut chart (0..100) with percentage text inside.
    """
    p = max(0.0, min(100.0, float(percent_value)))
    r = (size - stroke) / 2
    c = 2 * 3.141592653589793 * r
    offset = c * (1 - p / 100.0)

    # SVG donut: base ring + progress ring
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{size/2}" cy="{size/2}" r="{r}"
              fill="none" stroke="#E9EEF5" stroke-width="{stroke}" />
      <circle cx="{size/2}" cy="{size/2}" r="{r}"
              fill="none" stroke="#2D6CDF" stroke-width="{stroke}"
              stroke-linecap="round"
              stroke-dasharray="{c:.2f}"
              stroke-dashoffset="{offset:.2f}"
              transform="rotate(-90 {size/2} {size/2})" />
      <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"
            font-family="system-ui, -apple-system, Segoe UI, Roboto, Arial"
            font-size="{int(size*0.22)}" font-weight="700" fill="#111827">
        {p:.0f}%
      </text>
    </svg>
    """
    return svg

def load_data(profiles_path: str, matches_path: str):
    profiles = pd.read_csv(profiles_path)
    matches = pd.read_csv(matches_path)

    # sanity: required cols
    prof_req = {"user_id", "tenant_label"}
    match_req = {"tenant_label", "match_tenant_label", "compatibility_score", "top_drivers"}

    if not prof_req.issubset(set(profiles.columns)):
        raise ValueError(f"profiles file missing columns: {prof_req - set(profiles.columns)}")
    if not match_req.issubset(set(matches.columns)):
        raise ValueError(f"matches file missing columns: {match_req - set(matches.columns)}")

    return profiles, matches

def percent(x):
    try:
        return float(x)
    except:
        return 0.0

# ----------------------------
# Sidebar: data source
# ----------------------------
st.sidebar.header("Dati")
use_upload = st.sidebar.checkbox("Carica CSV manualmente (opzionale)", value=False)

profiles_path = "synthetic_profiles_v2.csv"
matches_path = "top_matches_explained_v2.csv"

profiles = None
matches = None

try:
    if use_upload:
        up_profiles = st.sidebar.file_uploader("synthetic_profiles_v2.csv", type=["csv"])
        up_matches = st.sidebar.file_uploader("top_matches_explained_v2.csv", type=["csv"])
        if up_profiles is None or up_matches is None:
            st.info("Carica entrambi i CSV per continuare, oppure disattiva l’opzione.")
            st.stop()
        profiles = pd.read_csv(up_profiles)
        matches = pd.read_csv(up_matches)
    else:
        profiles, matches = load_data(profiles_path, matches_path)
except Exception as e:
    st.error(f"Errore caricamento dati: {e}")
    st.stop()

# ----------------------------
# Sidebar: selection
# ----------------------------
st.sidebar.header("Selezione")
tenant_list = sorted(profiles["tenant_label"].unique().tolist())
selected_tenant = st.sidebar.selectbox("Select a tenant", tenant_list, index=min(0, len(tenant_list)-1))
top_n = st.sidebar.slider("Top N matches", min_value=3, max_value=15, value=5, step=1)

with st.sidebar.expander("Come funziona (quick)"):
    st.markdown(
        """
- Ogni tenant ha 10 variabili (1–5).
- Il motore calcola un **compatibility score** in %.
- Alcune variabili usano **similarity** (premia valori vicini).
- Altre usano **complementarity** (premia coppie “bilanciate”/compatibili).
- L’output mostra anche i **top drivers** (le variabili che hanno inciso di più).
        """.strip()
    )

# ----------------------------
# Main: Selected tenant profile
# ----------------------------
sel_row = profiles[profiles["tenant_label"] == selected_tenant].head(1)
if sel_row.empty:
    st.error("Tenant non trovato nei profili.")
    st.stop()

st.subheader(f"Selected tenant: {selected_tenant}")

c1, c2 = st.columns([1, 5], vertical_alignment="center")
with c1:
    st.image(avatar_url(selected_tenant, size=128, style="personas"), width=96)
with c2:
    st.dataframe(sel_row, width="stretch")

# ----------------------------
# Main: Matches for selected tenant
# ----------------------------
sub = matches[matches["tenant_label"] == selected_tenant].copy()
if sub.empty:
    st.warning("Non ci sono match per questo tenant nel file matches.")
    st.stop()

sub["compatibility_score"] = sub["compatibility_score"].apply(percent)
sub = sub.sort_values("compatibility_score", ascending=False).head(top_n)

st.subheader("Top matches")

for _, r in sub.iterrows():
    match_label = r.get("match_tenant_label", "")
    score = float(r.get("compatibility_score", 0.0))
    short = str(r.get("explanation_short", "")).strip()
    long = str(r.get("explanation_long", "")).strip()
    drivers = str(r.get("top_drivers", "")).strip()
    driver_vals = str(r.get("top_driver_values", "")).strip()

    card = st.container(border=True)
    with card:
        left, mid, right = st.columns([1, 5, 2], vertical_alignment="center")
        with left:
            st.image(avatar_url(match_label, size=128, style="personas"), width=72)
        with mid:
            st.markdown(f"### {match_label}")
            st.markdown(f"**Compatibility:** {score:.2f}%")
            if short:
                st.markdown(f"_{short}_")
            if drivers:
                st.caption(f"Top drivers: {drivers}")
        with right:
            svg = donut(score, size=88, stroke=10)
            st.markdown(
                f"<div style='display:flex; justify-content:flex-end;'>{svg}</div>",
                unsafe_allow_html=True,
            )
        with st.expander("Details"):
            if long:
                st.write(long)
            if driver_vals:
                st.caption("Top driver values (quick view)")
                st.code(driver_vals)

# ----------------------------
# Footer
# ----------------------------
st.divider()
st.caption("Note: This is a prototype based on synthetic data. In production, real data, feedback loops, and weight tuning would be implemented.")
