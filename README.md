
# Tenant Matching Prototype (Co-living) — Explainable Matching Engine + Streamlit Demo

## 0) What this project is (in simple terms)
This repository contains a working prototype that:
1) creates tenant profiles (synthetic / fake data for testing),
2) computes a compatibility score between every pair of tenants,
3) ranks the best matches for each tenant,
4) explains *why* a match is high (top drivers),
5) shows everything in a simple Streamlit web interface.

**Important scope note (thesis-relevant):**
- The current prototype is a **rule-based, deterministic matching framework** (not machine learning).
- It is built to be **transparent and explainable**, and to be a strong base for later validation (interviews/surveys and, potentially, ML in future iterations).

---

## 1) Repository structure (what each file does)
### Core logic
- `matching_engine.py`
  - Generates synthetic tenant profiles (1–5 scores)
  - Computes compatibility between tenants
  - Produces explainability (top drivers)
  - Exports results to CSV files

### Demo interface
- `app.py`
  - Streamlit user interface
  - **Reads** the CSV files produced by the engine (it does not recompute matches live)
  - Lets you explore tenants, top matches, and explanations

### Data files
- `synthetic_profiles_v2.csv`  
  Input dataset (synthetic). Contains tenant profiles and their variable values.
- `top_matches_explained_v2.csv`  
  Output dataset. Contains the ranked matches for each tenant + explanations.

### UI config
- `.streamlit/config.toml`  
  Streamlit theme configuration (light theme for readability)

---

## 2) How the system works (step-by-step)
This is the end-to-end pipeline:

### Step 1 — Define the tenant profile model (variables)
Each tenant is represented by **10 variables**.  
Each variable is scored on a **1–5 scale**, where:
- 1 = very low / minimal preference
- 3 = medium / neutral
- 5 = very high / strong preference

These variables are meant to capture the main day-to-day frictions in shared living.

### Step 2 — Generate synthetic data (for prototyping)
Because real co-living tenant data may not be available during early research phases, the engine creates synthetic profiles.

In `matching_engine.py`, synthetic profiles are generated with:
- `N_PROFILES = 300`
- `SEED = 1234` (fixed seed → reproducible results)

Output:
- `synthetic_profiles_v2.csv`

### Step 3 — Compute compatibility for each tenant pair
For each tenant A, the engine compares A with every other tenant B (A ≠ B), and computes a compatibility score in percentage (0–100%).

### Step 4 — Rank top matches
For each tenant A, the engine selects the **TOP_N = 5** best matches (highest compatibility score).

### Step 5 — Generate explainability (“top drivers”)
For each match, the engine:
- computes per-variable contributions,
- sorts them by impact,
- outputs the top 3 “drivers” explaining the high score.

Output:
- `top_matches_explained_v2.csv`

### Step 6 — Streamlit app reads CSV and displays results
`app.py` loads:
- profiles (`synthetic_profiles_v2.csv`)
- matches (`top_matches_explained_v2.csv`)

Then it displays:
- tenant selector
- top matches list
- donut chart compatibility
- realistic avatars (DiceBear)
- explainability text (short + long)

---

## 3) Tenant variables (what they mean)
The model uses the following variables (1–5 scale).  
Below is a short “plain English” meaning for each variable.

1) `cleanliness_level`  
   How high the person’s cleanliness/cleaning standard is.

2) `noise_tolerance`  
   How tolerant the person is to noise at home (lower tolerance = needs quiet).

3) `sleep_schedule`  
   Sleep pattern timing (early vs late; consistency of sleep hours).

4) `routine_structure`  
   How structured and regular the person’s daily routine is.

5) `WFH_frequency`  
   How often the person works from home (more presence at home).

6) `sociability_level`  
   Preference for social interaction at home (introverted ↔ very social).

7) `guest_tolerance`  
   Comfort level with guests visiting the house.

8) `privacy_need`  
   How much privacy and personal space the person needs.

9) `conflict_style`  
   How the person tends to handle conflict (avoidant ↔ direct/structured).

10) `shared_spaces_usage`  
   Intensity/frequency of using shared spaces (kitchen/living room) vs staying in private space.

---

## 4) How we designed the variables (research rationale)
The variable set is designed as a **prototype-stage decision framework** for co-living.
The rationale is:

- Co-living friction typically comes from repeated daily interactions and norms:
  cleanliness, noise, sleep rhythm, privacy, guests, shared space behavior, etc.
- These 10 variables are a **structured way to represent** those friction drivers.
- The framework is intentionally simple (1–5 scale) so it is:
  - easy to understand (for non-technical stakeholders),
  - easy to validate with interviews/surveys,
  - easy to extend later.

In the thesis, these variables should be justified through:
- literature (tenant satisfaction, conflict drivers, co-living dynamics),
- qualitative validation (operator interviews),
- quantitative validation (surveys / future data).

---

## 5) Similarity vs Complementarity (key modeling idea)
Not all variables behave the same way.

### 5.1 Similarity variables (8)
For these, **alignment reduces friction**.
The match score increases when two tenants have similar values.

In code (`SCORING_MODE`), similarity is used for:

- `cleanliness_level`
- `noise_tolerance`
- `sleep_schedule`
- `routine_structure`
- `WFH_frequency`
- `guest_tolerance`
- `privacy_need`
- `conflict_style`

**Intuition:**  
If two people have very different cleanliness standards or sleep schedules, co-living friction increases. Similar preferences tend to work better.

### 5.2 Complementarity variables (2)
For these, a “balanced pairing” can be beneficial.
We model complementarity as a “mirror balance” logic on a 1–5 scale.

In code (`SCORING_MODE`), complementarity is used for:

- `sociability_level`
- `shared_spaces_usage`

**Intuition:**  
Some household dynamics can work well when people balance each other (e.g., not everyone is extremely social, not everyone heavily occupies shared spaces).  
This is a modeling assumption to be validated later.

---

## 6) The math: how compatibility is computed
This section describes exactly what the engine computes.

### 6.1 Notation
- Let tenant A have value `A_f` for feature `f`
- Let tenant B have value `B_f` for feature `f`
- Values are in `{1,2,3,4,5}`
- Each feature has a weight `w_f`
- Each feature produces a normalized score `s_f(A,B)` in `[0,1]`

### 6.2 Similarity score (normalized, in [0,1])
For similarity variables, the engine computes:

- Maximum distance on 1–5 scale is:  
  `max_dist = 5 - 1 = 4`

- Distance between two tenants on feature f:  
  `dist = |A_f - B_f|`

- Similarity score:  
  `s_f(A,B) = 1 - (dist / 4)`

Examples:
- A=1, B=1 → dist=0 → score=1.00 (perfect similarity)
- A=1, B=2 → dist=1 → score=0.75
- A=1, B=5 → dist=4 → score=0.00 (max difference)

### 6.3 Complementarity score (mirror balance around midpoint)
Complementarity is implemented via **target sum**.

On a 1–5 scale:
- midpoint is 3
- target sum is:
  `target_sum = 1 + 5 = 6`

The idea: best complementarity happens when `A_f + B_f ≈ 6`:
- (1,5), (2,4), (3,3), (4,2), (5,1)

Compute:
- `sum = A_f + B_f`
- `dev = |sum - 6|`
- maximum deviation is 4 (same as max_dist)

Complementarity score:
- `s_f(A,B) = 1 - (dev / 4)`

Examples:
- (1,5): sum=6, dev=0 → score=1.00
- (3,3): sum=6, dev=0 → score=1.00
- (1,1): sum=2, dev=4 → score=0.00
- (5,5): sum=10, dev=4 → score=0.00

### 6.4 Weighted aggregation (final compatibility %)
For each feature `f`, we compute:
- a normalized score `s_f(A,B)` in [0,1]
- a weight `w_f`

Then:
- weighted sum:  
  `W = Σ_f (w_f * s_f(A,B))`
- total weight:  
  `T = Σ_f w_f`

Final compatibility percentage:
- `compat(A,B) = (W / T) * 100`

This produces a score in `[0,100]`.

---

## 7) Weights (importance assumptions, prototype stage)
Weights reflect the assumed importance of each variable in the final score.
They are **design assumptions for the prototype**, not empirically calibrated yet.

Current weights (from `matching_engine.py`):

- `cleanliness_level`: 1.3  
- `noise_tolerance`: 1.3  
- `sleep_schedule`: 1.2  
- `routine_structure`: 1.0  
- `WFH_frequency`: 0.8  
- `sociability_level`: 1.0  
- `guest_tolerance`: 1.0  
- `privacy_need`: 1.1  
- `conflict_style`: 0.9  
- `shared_spaces_usage`: 0.9  

Rationale (prototype-level):
- Cleanliness and noise tolerance are treated as major friction drivers.
- Sleep schedule has a strong daily impact.
- Privacy and conflict style influence emotional comfort and conflict probability.
- WFH frequency is relevant but context-dependent (hence lower weight).
- Sociability and shared-space usage matter, but are partly handled via complementarity logic.

In the thesis, these weights should be:
- validated with operator interviews,
- stress-tested via sensitivity analysis,
- refined via survey evidence (or learned from feedback if real data becomes available).

---

## 8) Explainability: how the “top drivers” are computed
For each candidate match (A,B), the engine stores for each feature:
- feature name `f`
- normalized score `s_f(A,B)`
- weight `w_f`
- mode (similarity or complementarity)

To explain a match, the engine ranks features by **contribution**:

- contribution of feature f:
  `c_f = w_f * s_f(A,B)`

Then it sorts all features by `c_f` (descending), and outputs:
- Top 3 driver variables (names)
- A short explanation sentence
- A longer explanation with the key rule:
  similarity rewards close values; complementarity rewards balanced pairs (a+b ≈ 6)
- A “values hint” showing A vs B on the top drivers

This is written into:
- `top_drivers`
- `explanation_short`
- `explanation_long`
- `top_driver_values`

in `top_matches_explained_v2.csv`.

---

## 9) How to run locally (beginner-friendly)
### 9.1 Generate (or regenerate) the CSV files
Run the engine:

- `python3 matching_engine.py`

This creates:
- `synthetic_profiles_v2.csv`
- `top_matches_explained_v2.csv`

You should see:
- `Done ✅`
- and confirmation of created files.

### 9.2 Launch the Streamlit demo
Run:
- `streamlit run app.py`

Then open the local URL shown in the terminal (example):
- `http://localhost:8502`

---

## 10) Next steps (thesis roadmap)
1) **Validation**
   - Operator interviews: does the variable set match real matching criteria?
   - Tenant surveys: which variables matter most? are the weights plausible?

2) **Data**
   - If real tenant data becomes available, test the model on real profiles.

3) **Robustness**
   - Sensitivity analysis: do rankings change dramatically if weights shift?

4) **AI/ML roadmap (future extension)**
   - If feedback loops exist (tenant satisfaction outcomes), weights could be learned from data.
   - The current framework is a structured base that can evolve into ML later.

---

## 11) Current status (what is already implemented)
- Working matching engine (similarity + complementarity)
- Weighted score to percentage
- Explainability (top drivers)
- Synthetic data generation (reproducible seed)
- Streamlit UI reading CSV outputs
- Donut visualization for compatibility
- Realistic avatars (DiceBear)
- Light theme configuration

## License
This project is licensed under the MIT License.
