# World Cup Winner Predictor

A tournament bracket predictor that uses FIFA rankings data to simulate World Cup outcomes via Monte Carlo simulation and machine learning models. Features an interactive SVG bracket visualization rendered in a Streamlit web app.

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [How It Works](#how-it-works)
  - [Prediction Methods](#prediction-methods)
  - [Tournament Formats](#tournament-formats)
  - [Bracket Seeding](#bracket-seeding)
- [API Reference](#api-reference)
- [Data Sources](#data-sources)
- [Customisation](#customisation)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Interactive bracket visualisation** — Full tournament bracket rendered as SVG with team flags, winner highlighting, and colour-coded confidence indicators
- **Monte Carlo simulation** — Run up to 50,000 tournament simulations to compute per-team win probabilities
- **ML prediction model** — Random Forest classifier trained on historical World Cup data (2010–2022)
- **Live FIFA rankings** — Fetch current rankings from the Footballdata.io API
- **Configurable formats** — Support for classic 32-team and new 48-team (2026) tournament structures
- **Reproducible results** — Set a random seed for deterministic bracket predictions
- **Dark-themed UI** — Modern dark interface with gold accent colours

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit App (app.py)                   │
├─────────────────────────────────────────────────────────────┤
│  UI Layer (src/ui/)          │  Prediction Layer             │
│  ├── bracket.py (SVG)        │  (src/prediction/)            │
│  └── components.py           │  ├── simulator.py (Monte      │
│      (sidebar, stats)        │  │   Carlo)                   │
│                              │  ├── ml_model.py (Random      │
│                              │  │   Forest)                  │
│                              │  └── engine.py (orchestrator) │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (src/data/)                                      │
│  ├── api_client.py (Footballdata.io API)                     │
│  ├── fallback.py (static rankings for 48 teams)             │
│  └── teams.py (Team, Match, TournamentConfig models)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
world-cup-predictor/
├── app.py                        # Streamlit entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .gitignore
├── .streamlit/
│   └── config.toml               # Streamlit theme & server config
├── data/
│   └── historical_results.csv    # World Cup match data (2010–2022)
└── src/
    ├── __init__.py
    ├── data/
    │   ├── __init__.py
    │   ├── api_client.py         # FIFA rankings API client
    │   ├── fallback.py           # Static fallback ranking data
    │   └── teams.py              # Data models (Team, Match, TournamentConfig)
    ├── prediction/
    │   ├── __init__.py
    │   ├── engine.py             # Prediction orchestrator & bracket seeding
    │   ├── ml_model.py           # Random Forest match predictor
    │   └── simulator.py          # Monte Carlo tournament simulator
    └── ui/
        ├── __init__.py
        ├── bracket.py            # SVG bracket renderer
        └── components.py         # Streamlit sidebar & stats components
```

---

## Prerequisites

- **Python 3.10+** (tested with 3.12)
- **pip** package manager
- (Optional) A free API key from [footballdata.io](https://footballdata.io) for live rankings

---

## Installation

1. **Clone the repository:**

```bash
git clone git@github.com:GeoDoo/world-cup-predictor.git
cd world-cup-predictor
```

2. **Create and activate a virtual environment:**

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root (use `.env.example` as a template):

```bash
cp .env.example .env
```

Then edit `.env` and add your API key:

```
FIFA_API_KEY=your_api_key_here
```

### Getting an API Key

1. Sign up at [footballdata.io](https://footballdata.io)
2. Navigate to your dashboard
3. Copy your API key
4. Paste it into your `.env` file

### Running Without an API Key

If no API key is configured, the app automatically falls back to bundled static rankings data (approximate mid-2026 FIFA rankings for 48 teams). All prediction features work normally with this fallback data.

---

## Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Command-Line Options

```bash
# Run on a different port
streamlit run app.py --server.port 8080

# Run in headless mode (no browser auto-open)
streamlit run app.py --server.headless true
```

---

## How It Works

### Prediction Methods

The app offers three prediction methods, selectable from the sidebar:

#### 1. Monte Carlo Simulation (default)

Simulates the entire knockout tournament N times (configurable, default 10,000) and reports aggregate statistics.

**Probability formula:**

```
P(Team A beats Team B) = 1 / (1 + 10^((points_B - points_A) / 600))
```

This is an ELO-style formula where `points_A` and `points_B` are FIFA ranking points. The divisor of 600 is calibrated so that a ~200-point gap gives approximately 75% win probability.

**Outputs:**
- The "most likely" bracket (the single simulation with the highest cumulative probability score)
- Per-team win probability (% of simulations where each team wins the tournament)
- Probability of reaching each round

#### 2. ML Model (Random Forest)

A scikit-learn `RandomForestClassifier` trained on historical World Cup match data.

**Features used:**
| Feature | Description |
|---------|-------------|
| `rank_diff` | Difference in FIFA rankings (B - A) |
| `points_diff` | Difference in FIFA points (A - B) |
| `points_a` | Team A's FIFA points |
| `points_b` | Team B's FIFA points |
| `rank_a` | Team A's FIFA ranking |
| `rank_b` | Team B's FIFA ranking |

**Training data:** 93 matches from the 2010, 2014, 2018, and 2022 World Cups (group stage, Round of 16, quarter-finals, semi-finals, and finals).

**Model parameters:**
- 200 estimators (trees)
- Max depth: 6
- Balanced class weights
- Fixed random state for reproducibility

#### 3. Single Bracket (Random)

Generates a single simulated bracket using the probability formula. Each run with a different seed produces a different possible outcome.

---

### Tournament Formats

#### 32 Teams (Classic Format)

The traditional World Cup knockout format:
- **Round of 16** → **Quarter-finals** → **Semi-finals** → **Final**
- 16 matches in the first round, converging to 1 final match
- 31 total matches

#### 48 Teams (2026 Format)

The new expanded World Cup format:
- 12 groups of 4 in the group stage
- Top 32 teams advance to the knockout bracket
- **Round of 32** → **Round of 16** → **Quarter-finals** → **Semi-finals** → **Final**
- The predictor simulates the knockout stage using the top 32 teams by ranking

---

### Bracket Seeding

Teams are placed in the bracket using standard tournament seeding:

1. Teams are sorted by FIFA points (highest = seed #1)
2. Seeds are placed so that the top seeds are on opposite sides of the bracket
3. This ensures #1 and #2 can only meet in the final, #1–#4 can only meet from semi-finals onwards, etc.

The seeding algorithm uses a recursive position-doubling approach to generate bracket slots for any power-of-2 size.

---

## API Reference

### Footballdata.io Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/fifa-rankings/current` | Fetch current FIFA men's rankings |

**Authentication:** Bearer token via `Authorization: Bearer <API_KEY>` header.

**Rate limits:** Free tier allows sufficient requests for this app's use case. Rankings are cached for 1 hour via Streamlit's `@st.cache_data`.

---

## Data Sources

### Historical Match Data (`data/historical_results.csv`)

Contains World Cup match results used to train the ML model:

| Column | Type | Description |
|--------|------|-------------|
| `year` | int | World Cup year (2010, 2014, 2018, 2022) |
| `round` | str | Match round (Group, R16, QF, SF, Final) |
| `team_a` | str | Team A name |
| `team_b` | str | Team B name |
| `score_a` | int | Goals scored by Team A |
| `score_b` | int | Goals scored by Team B |
| `team_a_rank` | int | Team A's FIFA ranking at the time |
| `team_b_rank` | int | Team B's FIFA ranking at the time |
| `team_a_points` | float | Team A's FIFA points at the time |
| `team_b_points` | float | Team B's FIFA points at the time |

### Fallback Rankings (`src/data/fallback.py`)

Static approximation of mid-2026 FIFA rankings for 48 teams. Used when the API is unavailable. Includes:
- Team name, ISO code, FIFA points, confederation, and ranking position
- Proper flag emoji support (including England, Scotland, and Wales sub-nation flags)

---

## Customisation

### Adding More Teams

Edit `src/data/fallback.py` to add additional teams to `FALLBACK_RANKINGS`:

```python
Team("New Team", "XX", 1400.00, "CONFEDERATION", 49),
```

### Adjusting Probability Formula

The ELO divisor (default: 600) in `src/prediction/simulator.py` controls how sensitive predictions are to ranking differences:
- **Lower value** (e.g. 400): Bigger upsets less likely, favourites dominate
- **Higher value** (e.g. 800): More competitive, underdogs have better chances

### Modifying the Bracket Appearance

The SVG rendering in `src/ui/bracket.py` uses these colour schemes:
- `#22c55e` (green): High confidence (>75%)
- `#84cc16` (lime): Good confidence (60–75%)
- `#eab308` (yellow): Toss-up (50–60%)
- `#ef4444` (red): Upset (<50%)
- `#fbbf24` (gold): Final match border and winner text
- `#0f172a` (dark navy): Background

### Using Different ML Models

Replace the `RandomForestClassifier` in `src/prediction/ml_model.py` with any scikit-learn classifier. The feature pipeline and prediction interface remain the same:

```python
from sklearn.linear_model import LogisticRegression

_model = LogisticRegression(max_iter=1000)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure venv is activated: `source .venv/bin/activate` |
| API returns empty data | Check your API key in `.env`. The app falls back to static data automatically. |
| Bracket looks cramped | Try resizing your browser window; the SVG container scrolls horizontally |
| `python: command not found` | Use `python3` instead, or check your PATH |
| Port 8501 in use | Run with `--server.port 8080` or kill the existing process |
| Slow simulations | Reduce the number of simulations in the sidebar slider |

---

## License

MIT
