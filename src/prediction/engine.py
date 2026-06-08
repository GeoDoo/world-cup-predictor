"""Prediction engine that orchestrates simulation and ML approaches."""

import random

from src.data.teams import Team, Match, TournamentConfig
from src.prediction.simulator import (
    monte_carlo_simulation,
    simulate_tournament,
    win_probability,
)


def seed_teams(teams: list[Team], format_type: str) -> list[Team]:
    """
    Seed teams for bracket placement.
    For 48-team format, top 32 advance to knockout.
    Standard bracket seeding ensures top seeds meet latest.
    """
    sorted_teams = sorted(teams, key=lambda t: t.fifa_points, reverse=True)

    # For 48-team format, only top 32 enter the knockout bracket
    if format_type == "48_knockout" and len(sorted_teams) > 32:
        sorted_teams = sorted_teams[:32]

    n = len(sorted_teams)
    if n < 2:
        return sorted_teams

    # Pad to next power of 2 for clean bracket seeding
    bracket_size = 1
    while bracket_size < n:
        bracket_size *= 2

    seeded = _bracket_seed(sorted_teams, bracket_size)
    return seeded


def _bracket_seed(teams: list[Team], bracket_size: int) -> list[Team]:
    """Place teams in bracket order so top seeds meet latest."""
    n = len(teams)
    if n <= 2:
        return teams

    positions = _seed_positions(bracket_size)
    result = [None] * bracket_size
    for i, pos in enumerate(positions):
        if i < n:
            result[pos] = teams[i]

    return [t for t in result if t is not None]


def _seed_positions(n: int) -> list[int]:
    """Generate bracket positions for standard seeding (n must be power of 2)."""
    if n == 1:
        return [0]
    if n == 2:
        return [0, 1]

    result = [0, 1]
    while len(result) < n:
        new_result = []
        size = len(result)
        for pos in result:
            new_result.append(pos * 2)
            new_result.append(size * 2 - 1 - pos * 2)
        result = new_result

    return result[:n]


def run_prediction(
    config: TournamentConfig,
    method: str = "simulation",
    n_simulations: int = 10000,
    seed: int | None = None,
) -> dict:
    """
    Run tournament prediction.

    Args:
        config: Tournament configuration with teams
        method: "simulation" for Monte Carlo, "ml" for ML model, "single" for one bracket
        n_simulations: Number of simulations for Monte Carlo
        seed: Random seed for reproducibility

    Returns:
        dict with bracket results, probabilities, and metadata
    """
    teams = config.teams[: config.num_teams]
    seeded_teams = seed_teams(teams, config.format_type)

    if method == "single":
        if seed is not None:
            random.seed(seed)
        bracket = simulate_tournament(seeded_teams)
        round_names = config.knockout_rounds
        for round_idx, matches in enumerate(bracket):
            if round_idx < len(round_names):
                for match in matches:
                    match.round_name = round_names[round_idx]
        return {
            "bracket": bracket,
            "champion": bracket[-1][0].winner if bracket else None,
            "method": "single",
            "teams": seeded_teams,
        }

    if method == "ml":
        from src.prediction.ml_model import ml_predict_tournament

        bracket = ml_predict_tournament(seeded_teams)
        round_names = config.knockout_rounds
        for round_idx, matches in enumerate(bracket):
            if round_idx < len(round_names):
                for match in matches:
                    match.round_name = round_names[round_idx]
        return {
            "bracket": bracket,
            "champion": bracket[-1][0].winner if bracket else None,
            "method": "ml",
            "teams": seeded_teams,
        }

    results = monte_carlo_simulation(seeded_teams, n_simulations, seed)
    bracket = results["best_bracket"]
    if bracket:
        round_names = config.knockout_rounds
        for round_idx, matches in enumerate(bracket):
            if round_idx < len(round_names):
                for match in matches:
                    match.round_name = round_names[round_idx]

    return {
        "bracket": bracket,
        "champion": bracket[-1][0].winner if bracket else None,
        "win_probabilities": results["win_probabilities"],
        "round_counts": results["round_counts"],
        "n_simulations": n_simulations,
        "method": "simulation",
        "teams": seeded_teams,
    }
