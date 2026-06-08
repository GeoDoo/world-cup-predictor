"""World Cup 2026 Predictor - Streamlit Application."""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="World Cup 2026 Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.prediction.engine import run_prediction
from src.ui.bracket import render_animated_bracket
from src.ui.components import render_sidebar, render_stats_table, render_groups


def main():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stApp {
                background: linear-gradient(160deg, #0f0326 0%, #1a0a3e 30%, #0d1b2a 70%, #0f0326 100%);
            }
            .block-container { padding-top: 0.5rem; }
            h1, h2, h3 { color: #f8fafc !important; }
            iframe { border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    config = render_sidebar()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_button = st.button(
            "⚡ Simulate World Cup",
            type="primary",
            use_container_width=True,
        )

    if run_button or "results" not in st.session_state:
        with st.spinner("Running simulation..."):
            try:
                results = run_prediction(
                    method=config["method"],
                    n_simulations=config["n_simulations"],
                    seed=config["seed"],
                )
                st.session_state["results"] = results
            except Exception as e:
                st.error(f"Simulation failed: {e}")
                import traceback
                st.code(traceback.format_exc())
                st.stop()

    results = st.session_state.get("results")

    if results:
        bracket = results.get("bracket")
        group_standings = results.get("group_standings")

        if bracket:
            html = render_animated_bracket(bracket, group_standings)
            st.components.v1.html(html, height=950, scrolling=True)

        render_stats_table(results)

    with st.expander("📋 Groups & Teams", expanded=False):
        render_groups()


if __name__ == "__main__":
    main()
