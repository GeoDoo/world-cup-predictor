# World Cup Winner Predictor

A tournament bracket predictor that uses FIFA rankings data to simulate World Cup outcomes via Monte Carlo simulation and machine learning models.

## Features

- Interactive tournament bracket visualization (SVG)
- Monte Carlo simulation weighted by FIFA ranking points
- ML prediction model trained on historical World Cup results
- Configurable tournament formats (32 or 48 teams)
- Live FIFA rankings via API
- Team flags and probability indicators

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Set your FIFA rankings API key as an environment variable:

```bash
export FIFA_API_KEY="your_api_key_here"
```

Get a free API key at [footballdata.io](https://footballdata.io).

If no API key is set, the app falls back to bundled static ranking data.

## Run

```bash
streamlit run app.py
```

## Tournament Formats

- **32 teams**: Classic World Cup knockout bracket (Round of 16 onwards)
- **48 teams**: 2026 format with 12 groups of 4, advancing to a Round of 32 knockout stage
