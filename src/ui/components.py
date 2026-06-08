"""Streamlit UI components for sidebar controls and stats display."""

import streamlit as st
import pandas as pd

from src.data.teams import Team, TournamentConfig


def render_sidebar(teams: list[Team]) -> dict:
    """Render sidebar controls and return configuration."""
    st.sidebar.title("⚽ Configuration")

    format_type = st.sidebar.selectbox(
        "Tournament Format",
        options=["32_knockout", "48_knockout"],
        format_func=lambda x: "32 Teams (Classic)" if x == "32_knockout" else "48 Teams (2026 Format)",
    )

    num_teams = 32 if format_type == "32_knockout" else 48

    method = st.sidebar.selectbox(
        "Prediction Method",
        options=["simulation", "ml", "single"],
        format_func=lambda x: {
            "simulation": "Monte Carlo Simulation",
            "ml": "ML Model (Random Forest)",
            "single": "Single Bracket (Random)",
        }[x],
    )

    n_simulations = 10000
    if method == "simulation":
        n_simulations = st.sidebar.slider(
            "Number of Simulations",
            min_value=100,
            max_value=50000,
            value=10000,
            step=100,
        )

    seed = st.sidebar.number_input(
        "Random Seed (0 = random)",
        min_value=0,
        max_value=999999,
        value=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Team Pool")
    st.sidebar.markdown(f"Using top **{num_teams}** teams by FIFA ranking")

    return {
        "format_type": format_type,
        "num_teams": num_teams,
        "method": method,
        "n_simulations": n_simulations,
        "seed": seed if seed != 0 else None,
    }


def render_stats_table(results: dict, num_teams: int) -> None:
    """Render the probability statistics table."""
    if results.get("method") != "simulation":
        return

    win_probs = results.get("win_probabilities", {})
    round_counts = results.get("round_counts", {})
    n_sims = results.get("n_simulations", 1)

    if not win_probs:
        return

    st.markdown("---")
    st.markdown("### 📈 Tournament Win Probabilities")

    sorted_teams = sorted(win_probs.items(), key=lambda x: x[1], reverse=True)

    rows = []
    for team_name, prob in sorted_teams[:20]:
        team_rounds = round_counts.get(team_name, {})
        row = {
            "Team": team_name,
            "Win %": f"{prob * 100:.1f}%",
            "Final": f"{team_rounds.get(max(team_rounds.keys()) if team_rounds else 0, 0) / n_sims * 100:.1f}%" if team_rounds else "0%",
            "Semi-final": f"{_round_pct(team_rounds, -2, n_sims)}",
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _round_pct(round_counts: dict, round_offset: int, n_sims: int) -> str:
    """Get percentage for a specific round by offset from last."""
    if not round_counts:
        return "0%"
    max_round = max(round_counts.keys())
    target = max_round + round_offset + 1
    count = round_counts.get(target, 0)
    return f"{count / n_sims * 100:.1f}%"


def render_champion_banner(champion: Team | None) -> None:
    """Render the predicted champion banner."""
    if champion is None:
        return

    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e293b, #334155);
                    border-radius: 12px; border: 2px solid #fbbf24; margin: 20px 0;">
            <div style="font-size: 48px;">🏆</div>
            <div style="font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px;">
                Predicted Winner
            </div>
            <div style="font-size: 28px; font-weight: bold; color: #fbbf24; margin-top: 8px;">
                {champion.flag_emoji} {champion.name}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
