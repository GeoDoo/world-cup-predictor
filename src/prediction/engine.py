"""Prediction engine - orchestrates tournament simulation."""

import random

from src.data.teams import Team, Match
from src.prediction.simulator import (
    simulate_full_tournament,
    monte_carlo,
)


def run_prediction(
    method: str = "simulation",
    n_simulations: int = 10000,
    seed: int | None = None,
) -> dict:
    """
    Run tournament prediction.

    Args:
        method: "simulation" for Monte Carlo, "single" for one bracket
        n_simulations: Number of simulations for Monte Carlo
        seed: Random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)

    if method == "single":
        knockout_rounds, group_standings = simulate_full_tournament()
        champion = knockout_rounds[-1][0].winner
        return {
            "bracket": knockout_rounds,
            "group_standings": group_standings,
            "champion": champion,
            "method": "single",
        }

    # Monte Carlo: run many sims for probabilities, then one final sim for the animated bracket
    results = monte_carlo(n_simulations, seed)

    # Run one more simulation to get a representative bracket WITH group standings
    knockout_rounds, group_standings = simulate_full_tournament()

    champion = knockout_rounds[-1][0].winner

    return {
        "bracket": knockout_rounds,
        "group_standings": group_standings,
        "champion": champion,
        "win_probabilities": results["win_probabilities"],
        "final_counts": results["final_counts"],
        "semi_counts": results["semi_counts"],
        "qf_counts": results["qf_counts"],
        "r16_counts": results["r16_counts"],
        "group_advance_counts": results["group_advance_counts"],
        "n_simulations": n_simulations,
        "method": "simulation",
    }
