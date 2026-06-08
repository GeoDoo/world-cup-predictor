"""World Cup Winner Predictor - Streamlit Application."""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="World Cup Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.data.api_client import fetch_fifa_rankings
from src.data.fallback import get_fallback_teams
from src.data.teams import TournamentConfig
from src.prediction.engine import run_prediction
from src.ui.bracket import render_bracket_svg
from src.ui.components import render_sidebar, render_stats_table, render_champion_banner


@st.cache_data(ttl=3600)
def load_teams(num_teams: int) -> list:
    """Load teams from API with fallback to static data."""
    teams = fetch_fifa_rankings(limit=num_teams)
    if not teams:
        teams = get_fallback_teams(num_teams)
    return teams


def main():
    teams = load_teams(48)

    if not teams:
        st.error("Failed to load team data. Please check your API key or internet connection.")
        st.stop()

    config = render_sidebar(teams)

    num_teams = config["num_teams"]
    selected_teams = teams[:num_teams]

    tournament = TournamentConfig(
        name="World Cup",
        num_teams=num_teams,
        format_type=config["format_type"],
        teams=selected_teams,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_button = st.button(
            "🎲 Generate Prediction",
            type="primary",
            use_container_width=True,
        )

    # Clear stale results if config changed
    prev_config = st.session_state.get("_prev_config")
    current_config_key = (config["format_type"], config["method"], config["n_simulations"])
    if prev_config != current_config_key:
        st.session_state.pop("results", None)
        st.session_state["_prev_config"] = current_config_key

    if run_button or "results" not in st.session_state:
        with st.spinner("Simulating tournament..."):
            try:
                results = run_prediction(
                    config=tournament,
                    method=config["method"],
                    n_simulations=config["n_simulations"],
                    seed=config["seed"],
                )
                st.session_state["results"] = results
            except Exception as e:
                st.error(f"Prediction failed: {e}")
                st.stop()

    results = st.session_state.get("results")

    if results:
        render_champion_banner(results.get("champion"))

        bracket = results.get("bracket")
        if bracket:
            round_names = tournament.knockout_rounds
            svg = render_bracket_svg(bracket, round_names)
            svg_height = max(700, len(bracket[0]) * 75 + 200)
            st.components.v1.html(svg, height=svg_height, scrolling=True)

        render_stats_table(results, num_teams)

    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #64748b; font-size: 12px;">'
        "World Cup Predictor | Powered by FIFA Rankings & Monte Carlo Simulation"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
