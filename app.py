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
from src.ui.bracket import render_bracket_html
from src.ui.components import render_sidebar, render_stats_table, render_groups


def main():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stApp {
                background: linear-gradient(160deg, #0f0326 0%, #1a0a3e 30%, #0d1b2a 70%, #0f0326 100%);
            }
            .block-container { padding-top: 1rem; }
            h1, h2, h3 { color: #f8fafc !important; }
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

    # Clear results on config change
    prev_config = st.session_state.get("_prev_config")
    current_key = (config["method"], config["n_simulations"])
    if prev_config != current_key:
        st.session_state.pop("results", None)
        st.session_state["_prev_config"] = current_key

    if run_button or "results" not in st.session_state:
        with st.spinner("Simulating full tournament (group stage + knockout)..."):
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
        champion = results.get("champion")
        if champion:
            st.markdown(
                f"""
                <div style="text-align:center; padding:16px; margin:10px 0;
                     background: linear-gradient(135deg, rgba(251,191,36,0.1), rgba(251,191,36,0.03));
                     border: 1px solid rgba(251,191,36,0.3); border-radius:12px;">
                    <span style="font-size:36px;">🏆</span>
                    <div style="font-size:11px; color:#94a3b8; letter-spacing:2px; margin-top:4px;">
                        PREDICTED WINNER
                    </div>
                    <div style="font-size:24px; font-weight:800; color:#fbbf24;">
                        <img src="{champion.flag_url}" style="height:20px; border-radius:2px; vertical-align:middle; margin-right:8px;"/>
                        {champion.name}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        bracket = results.get("bracket")
        if bracket:
            html = render_bracket_html(bracket)
            st.html(html)

        render_stats_table(results)

    with st.expander("📋 Groups & Teams", expanded=False):
        render_groups()


if __name__ == "__main__":
    main()
