"""Streamlit UI components."""

import streamlit as st
import pandas as pd

from src.data.teams import Team, GroupStanding
from src.data.fallback import TEAMS, GROUPS


def render_sidebar() -> dict:
    """Render sidebar controls and return configuration."""
    st.sidebar.markdown(
        '<h2 style="text-align:center;">⚽ World Cup 2026<br/>Predictor</h2>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    method = st.sidebar.selectbox(
        "Prediction Method",
        options=["simulation", "single"],
        format_func=lambda x: {
            "simulation": "🎲 Monte Carlo (full simulation)",
            "single": "🎯 Single Bracket",
        }[x],
    )

    n_simulations = 10000
    if method == "simulation":
        n_simulations = st.sidebar.slider(
            "Simulations",
            min_value=500,
            max_value=50000,
            value=5000,
            step=500,
            help="More simulations = better accuracy but slower. Group + knockout simulated each time.",
        )

    seed = st.sidebar.number_input(
        "Random Seed (0 = random)",
        min_value=0,
        max_value=999999,
        value=0,
        help="Set a fixed seed for reproducible predictions",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Tournament Info**")
    st.sidebar.markdown("- 48 teams, 12 groups of 4")
    st.sidebar.markdown("- Top 2 + 8 best 3rd → R32")
    st.sidebar.markdown("- Real FIFA rankings (Apr 2026)")
    st.sidebar.markdown("- Official bracket structure")

    return {
        "method": method,
        "n_simulations": n_simulations,
        "seed": seed if seed != 0 else None,
    }


def render_stats_table(results: dict) -> None:
    """Render the probability statistics table."""
    if results.get("method") != "simulation":
        return

    win_probs = results.get("win_probabilities", {})
    if not win_probs:
        return

    st.markdown("### 📊 Tournament Win Probabilities")
    st.caption(f"Based on {results.get('n_simulations', 0):,} full tournament simulations")

    sorted_teams = sorted(win_probs.items(), key=lambda x: x[1], reverse=True)

    semi_counts = results.get("semi_counts", {})
    final_counts = results.get("final_counts", {})
    qf_counts = results.get("qf_counts", {})

    rows = []
    for rank, (team_name, prob) in enumerate(sorted_teams[:20], 1):
        team = TEAMS.get(team_name)
        rows.append({
            "#": rank,
            "Team": team_name,
            "Ranking": team.ranking if team else "-",
            "Win %": f"{prob * 100:.1f}%",
            "Final %": f"{final_counts.get(team_name, 0) * 100:.1f}%",
            "Semi %": f"{semi_counts.get(team_name, 0) * 100:.1f}%",
            "QF %": f"{qf_counts.get(team_name, 0) * 100:.1f}%",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)


def render_groups() -> None:
    """Render the group stage overview."""
    st.markdown("### 🏟️ Group Stage")

    cols = st.columns(4)
    for idx, (group_name, team_names) in enumerate(GROUPS.items()):
        col = cols[idx % 4]
        with col:
            teams_md = "\n".join(
                f"- **{name}** (#{TEAMS[name].ranking})"
                for name in team_names
            )
            st.markdown(f"**Group {group_name}**\n{teams_md}")
            if idx % 4 == 3 and idx < len(GROUPS) - 1:
                cols = st.columns(4)
