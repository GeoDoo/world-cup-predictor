"""Monte Carlo tournament simulator using ELO-style probability."""

import random
from collections import defaultdict

from src.data.teams import Team, Match


def win_probability(team_a: Team, team_b: Team) -> float:
    """Calculate probability of team_a beating team_b based on FIFA points."""
    return 1.0 / (1.0 + 10 ** ((team_b.fifa_points - team_a.fifa_points) / 600.0))


def simulate_match(team_a: Team, team_b: Team) -> Team:
    """Simulate a single match, returning the winner."""
    prob_a = win_probability(team_a, team_b)
    return team_a if random.random() < prob_a else team_b


def simulate_knockout_round(teams: list[Team]) -> list[Match]:
    """Simulate one round of knockout matches from a seeded list of teams."""
    matches = []
    for i in range(0, len(teams), 2):
        team_a = teams[i]
        team_b = teams[i + 1]
        winner = simulate_match(team_a, team_b)
        prob = win_probability(team_a, team_b)
        match = Match(
            team_a=team_a,
            team_b=team_b,
            winner=winner,
            win_probability=prob if winner == team_a else 1 - prob,
        )
        matches.append(match)
    return matches


def simulate_tournament(teams: list[Team]) -> list[list[Match]]:
    """
    Simulate an entire knockout tournament.
    Returns list of rounds, each containing matches.
    Teams should be seeded (ordered for bracket pairing).
    """
    current_teams = list(teams)
    all_rounds = []

    while len(current_teams) > 1:
        matches = simulate_knockout_round(current_teams)
        all_rounds.append(matches)
        current_teams = [m.winner for m in matches]

    return all_rounds


def monte_carlo_simulation(
    teams: list[Team], n_simulations: int = 10000, seed: int | None = None
) -> dict:
    """
    Run N tournament simulations and aggregate results.

    Returns:
        dict with:
            - "win_counts": {team: count}
            - "round_counts": {team: {round_idx: count}}
            - "best_bracket": the most representative single bracket
            - "win_probabilities": {team: probability}
    """
    if seed is not None:
        random.seed(seed)

    win_counts: dict[str, int] = defaultdict(int)
    round_counts: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    best_bracket = None
    best_bracket_score = -1

    for _ in range(n_simulations):
        rounds = simulate_tournament(teams)
        bracket_score = 0

        for round_idx, matches in enumerate(rounds):
            for match in matches:
                round_counts[match.winner.name][round_idx] += 1
                prob = win_probability(match.winner, match.team_a if match.winner == match.team_b else match.team_b)
                bracket_score += prob

        champion = rounds[-1][0].winner
        win_counts[champion.name] += 1

        if bracket_score > best_bracket_score:
            best_bracket_score = bracket_score
            best_bracket = rounds

    win_probabilities = {
        team: count / n_simulations for team, count in win_counts.items()
    }

    return {
        "win_counts": dict(win_counts),
        "round_counts": {k: dict(v) for k, v in round_counts.items()},
        "best_bracket": best_bracket,
        "win_probabilities": win_probabilities,
        "n_simulations": n_simulations,
    }
