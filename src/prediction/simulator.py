"""
Full tournament simulation: group stage + knockout bracket.
Uses ELO-style probability from real FIFA ranking points.
"""

import random
from collections import defaultdict

from src.data.teams import Team, Match, GroupStanding
from src.data.fallback import (
    GROUPS, TEAMS, get_group_teams,
    R32_BRACKET_LEFT, R32_BRACKET_RIGHT,
    R16_MATCHES, QF_MATCHES, SF_MATCHES, FINAL_MATCH,
)


def win_probability(team_a: Team, team_b: Team) -> float:
    """P(team_a wins) using FIFA's own ELO formula with c=600."""
    return 1.0 / (1.0 + 10.0 ** ((team_b.fifa_points - team_a.fifa_points) / 600.0))


def simulate_group_match(team_a: Team, team_b: Team) -> tuple[int, int]:
    """
    Simulate a group stage match, returning (score_a, score_b).
    Draws are possible in the group stage.
    """
    prob_a = win_probability(team_a, team_b)
    draw_prob = 0.25  # ~25% of World Cup group matches are draws

    roll = random.random()
    if roll < prob_a * (1 - draw_prob):
        # Team A wins
        goals_a = random.choices([1, 2, 3, 4], weights=[35, 35, 20, 10])[0]
        goals_b = random.randint(0, goals_a - 1)
        return goals_a, goals_b
    elif roll < prob_a * (1 - draw_prob) + draw_prob:
        # Draw
        goals = random.choices([0, 1, 2], weights=[30, 45, 25])[0]
        return goals, goals
    else:
        # Team B wins
        goals_b = random.choices([1, 2, 3, 4], weights=[35, 35, 20, 10])[0]
        goals_a = random.randint(0, goals_b - 1)
        return goals_a, goals_b


def simulate_knockout_match(team_a: Team, team_b: Team) -> tuple[Team, float]:
    """Simulate a knockout match (must have a winner). Returns (winner, prob)."""
    prob_a = win_probability(team_a, team_b)
    if random.random() < prob_a:
        return team_a, prob_a
    return team_b, 1 - prob_a


def simulate_group_stage() -> dict[str, list[GroupStanding]]:
    """Simulate all 12 group stages. Returns standings per group."""
    all_standings = {}

    for group_name in GROUPS:
        teams = get_group_teams(group_name)
        standings = {t.name: GroupStanding(team=t) for t in teams}

        # Each team plays every other team once (3 matches each)
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                ta, tb = teams[i], teams[j]
                sa, sb = simulate_group_match(ta, tb)

                standings[ta.name].played += 1
                standings[tb.name].played += 1
                standings[ta.name].goals_for += sa
                standings[ta.name].goals_against += sb
                standings[tb.name].goals_for += sb
                standings[tb.name].goals_against += sa

                if sa > sb:
                    standings[ta.name].won += 1
                    standings[tb.name].lost += 1
                elif sa == sb:
                    standings[ta.name].drawn += 1
                    standings[tb.name].drawn += 1
                else:
                    standings[tb.name].won += 1
                    standings[ta.name].lost += 1

        sorted_standings = sorted(standings.values(), key=lambda s: s.sort_key)
        all_standings[group_name] = sorted_standings

    return all_standings


def determine_advancing_teams(
    standings: dict[str, list[GroupStanding]]
) -> tuple[dict[str, Team], dict[str, Team], list[tuple[str, Team]]]:
    """
    Determine which 32 teams advance.
    Returns:
        - group_winners: {"A": team, "B": team, ...}
        - group_runners: {"A": team, "B": team, ...}
        - third_place_qualifiers: [(group_letter, team), ...] sorted best to worst
    """
    group_winners = {}
    group_runners = {}
    third_place_teams = []

    for group_name, group_standings in standings.items():
        group_winners[group_name] = group_standings[0].team
        group_runners[group_name] = group_standings[1].team
        third_place_teams.append((group_name, group_standings[2]))

    # Sort 3rd-place teams: best 8 advance
    third_place_teams.sort(key=lambda x: x[1].sort_key)
    third_place_qualifiers = [(g, s.team) for g, s in third_place_teams[:8]]

    return group_winners, group_runners, third_place_qualifiers


def assign_third_place_to_bracket(
    third_place_qualifiers: list[tuple[str, Team]],
    bracket_slots: list[tuple[str, str, str]],
) -> dict[str, Team]:
    """
    Assign 3rd-place teams to their R32 bracket slots.
    Each slot has a list of possible source groups (e.g. "3CEFHI").
    We assign based on which groups actually qualified.
    """
    qualifying_groups = {g for g, _ in third_place_qualifiers}
    team_by_group = {g: t for g, t in third_place_qualifiers}

    assignments = {}
    used_groups = set()

    for match_id, slot_a, slot_b in bracket_slots:
        slot = slot_b if slot_b.startswith("3") else slot_a
        if not slot.startswith("3"):
            continue

        possible_groups = slot[1:]  # e.g. "CEFHI"
        for g in possible_groups:
            if g in qualifying_groups and g not in used_groups:
                assignments[match_id] = team_by_group[g]
                used_groups.add(g)
                break

    return assignments


def simulate_knockout_stage(
    group_winners: dict[str, Team],
    group_runners: dict[str, Team],
    third_place_qualifiers: list[tuple[str, Team]],
) -> list[list[Match]]:
    """
    Simulate the full knockout bracket following FIFA's predetermined structure.
    Returns rounds: [R32_matches, R16_matches, QF_matches, SF_matches, Final].
    """
    # Assign teams to R32 slots
    all_bracket = R32_BRACKET_LEFT + R32_BRACKET_RIGHT
    third_assignments = assign_third_place_to_bracket(third_place_qualifiers, all_bracket)

    def resolve_team(slot: str, match_id: str) -> Team:
        if slot.startswith("1"):
            return group_winners[slot[1]]
        elif slot.startswith("2"):
            return group_runners[slot[1]]
        elif slot.startswith("3"):
            return third_assignments.get(match_id, third_place_qualifiers[0][1])
        return None

    # Simulate R32
    r32_matches = []
    r32_winners = {}

    for match_id, slot_a, slot_b in all_bracket:
        team_a = resolve_team(slot_a, match_id)
        team_b = resolve_team(slot_b, match_id)
        winner, prob = simulate_knockout_match(team_a, team_b)
        match = Match(
            team_a=team_a, team_b=team_b, winner=winner,
            win_probability=prob, round_name="Round of 32",
        )
        r32_matches.append(match)
        r32_winners[match_id] = winner

    # Simulate R16
    r16_matches = []
    r16_winners = {}
    for match_id, src_a, src_b in R16_MATCHES:
        team_a = r32_winners[src_a]
        team_b = r32_winners[src_b]
        winner, prob = simulate_knockout_match(team_a, team_b)
        match = Match(
            team_a=team_a, team_b=team_b, winner=winner,
            win_probability=prob, round_name="Round of 16",
        )
        r16_matches.append(match)
        r16_winners[match_id] = winner

    # Simulate QF
    qf_matches = []
    qf_winners = {}
    for match_id, src_a, src_b in QF_MATCHES:
        team_a = r16_winners[src_a]
        team_b = r16_winners[src_b]
        winner, prob = simulate_knockout_match(team_a, team_b)
        match = Match(
            team_a=team_a, team_b=team_b, winner=winner,
            win_probability=prob, round_name="Quarter-finals",
        )
        qf_matches.append(match)
        qf_winners[match_id] = winner

    # Simulate SF
    sf_matches = []
    sf_winners = {}
    for match_id, src_a, src_b in SF_MATCHES:
        team_a = qf_winners[src_a]
        team_b = qf_winners[src_b]
        winner, prob = simulate_knockout_match(team_a, team_b)
        match = Match(
            team_a=team_a, team_b=team_b, winner=winner,
            win_probability=prob, round_name="Semi-finals",
        )
        sf_matches.append(match)
        sf_winners[match_id] = winner

    # Simulate Final
    final_id, src_a, src_b = FINAL_MATCH
    team_a = sf_winners[src_a]
    team_b = sf_winners[src_b]
    winner, prob = simulate_knockout_match(team_a, team_b)
    final_match = Match(
        team_a=team_a, team_b=team_b, winner=winner,
        win_probability=prob, round_name="Final",
    )

    return [r32_matches, r16_matches, qf_matches, sf_matches, [final_match]]


def simulate_full_tournament() -> tuple[list[list[Match]], dict[str, list[GroupStanding]]]:
    """Simulate the entire 2026 World Cup. Returns (knockout_rounds, group_standings)."""
    standings = simulate_group_stage()
    winners, runners, third_place = determine_advancing_teams(standings)
    knockout_rounds = simulate_knockout_stage(winners, runners, third_place)
    return knockout_rounds, standings


def monte_carlo(n_simulations: int = 10000, seed: int | None = None) -> dict:
    """
    Run N full tournament simulations and aggregate results.
    Returns probabilities and the best representative bracket.
    """
    if seed is not None:
        random.seed(seed)

    win_counts: dict[str, int] = defaultdict(int)
    final_counts: dict[str, int] = defaultdict(int)
    semi_counts: dict[str, int] = defaultdict(int)
    qf_counts: dict[str, int] = defaultdict(int)
    r16_counts: dict[str, int] = defaultdict(int)
    group_advance_counts: dict[str, int] = defaultdict(int)

    best_bracket = None
    best_bracket_score = -1

    for _ in range(n_simulations):
        knockout_rounds, _ = simulate_full_tournament()
        bracket_score = 0

        # R32 - count all teams that made knockout
        for match in knockout_rounds[0]:
            group_advance_counts[match.team_a.name] += 1
            group_advance_counts[match.team_b.name] += 1
            bracket_score += match.win_probability

        # R16
        for match in knockout_rounds[1]:
            r16_counts[match.winner.name] += 1
            bracket_score += match.win_probability

        # QF
        for match in knockout_rounds[2]:
            qf_counts[match.winner.name] += 1
            bracket_score += match.win_probability

        # SF
        for match in knockout_rounds[3]:
            semi_counts[match.winner.name] += 1
            bracket_score += match.win_probability

        # Final
        final_match = knockout_rounds[4][0]
        final_counts[final_match.team_a.name] += 1
        final_counts[final_match.team_b.name] += 1
        win_counts[final_match.winner.name] += 1
        bracket_score += final_match.win_probability

        if bracket_score > best_bracket_score:
            best_bracket_score = bracket_score
            best_bracket = knockout_rounds

    win_probabilities = {
        team: count / n_simulations for team, count in win_counts.items()
    }

    return {
        "win_probabilities": win_probabilities,
        "final_counts": {t: c / n_simulations for t, c in final_counts.items()},
        "semi_counts": {t: c / n_simulations for t, c in semi_counts.items()},
        "qf_counts": {t: c / n_simulations for t, c in qf_counts.items()},
        "r16_counts": {t: c / n_simulations for t, c in r16_counts.items()},
        "group_advance_counts": {t: c / n_simulations for t, c in group_advance_counts.items()},
        "best_bracket": best_bracket,
        "n_simulations": n_simulations,
    }
