"""ML-based match prediction using historical World Cup data."""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from src.data.teams import Team, Match


_model = None
_scaler = None


def _get_data_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "..", "data", "historical_results.csv")


def _load_training_data() -> pd.DataFrame:
    path = _get_data_path()
    df = pd.read_csv(path)
    return df


def _prepare_features(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Build feature matrix from historical matches.
    Features: rank_diff, points_diff, points_a, points_b
    Target: 1 if team_a wins, 0 if team_b wins (draws resolved by penalties -> coin flip in training)
    """
    features = []
    labels = []

    for _, row in df.iterrows():
        rank_diff = row["team_b_rank"] - row["team_a_rank"]
        points_diff = row["team_a_points"] - row["team_b_points"]

        feat = [
            rank_diff,
            points_diff,
            row["team_a_points"],
            row["team_b_points"],
            row["team_a_rank"],
            row["team_b_rank"],
        ]
        features.append(feat)

        if row["score_a"] > row["score_b"]:
            labels.append(1)
        elif row["score_a"] < row["score_b"]:
            labels.append(0)
        else:
            # Draws in knockout resolved by penalties - use ranking as tiebreaker
            labels.append(1 if row["team_a_rank"] < row["team_b_rank"] else 0)

    return np.array(features), np.array(labels)


def train_model() -> tuple[RandomForestClassifier, StandardScaler]:
    """Train the prediction model on historical data."""
    global _model, _scaler

    df = _load_training_data()
    X, y = _prepare_features(df)

    _scaler = StandardScaler()
    X_scaled = _scaler.fit_transform(X)

    _model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        class_weight="balanced",
    )
    _model.fit(X_scaled, y)

    return _model, _scaler


def get_model() -> tuple[RandomForestClassifier, StandardScaler]:
    """Get or train the model (singleton)."""
    global _model, _scaler
    if _model is None:
        train_model()
    return _model, _scaler


def predict_match(team_a: Team, team_b: Team) -> tuple[Team, float]:
    """
    Predict the winner of a match using the ML model.
    Returns (winner, confidence).
    """
    model, scaler = get_model()

    features = np.array([[
        team_b.ranking - team_a.ranking,
        team_a.fifa_points - team_b.fifa_points,
        team_a.fifa_points,
        team_b.fifa_points,
        team_a.ranking,
        team_b.ranking,
    ]])

    features_scaled = scaler.transform(features)
    prob_a = model.predict_proba(features_scaled)[0][1]

    if prob_a >= 0.5:
        return team_a, prob_a
    else:
        return team_b, 1 - prob_a


def ml_predict_tournament(teams: list[Team]) -> list[list[Match]]:
    """Predict an entire knockout tournament using the ML model."""
    current_teams = list(teams)
    all_rounds = []

    while len(current_teams) > 1:
        matches = []
        for i in range(0, len(current_teams), 2):
            team_a = current_teams[i]
            team_b = current_teams[i + 1]
            winner, confidence = predict_match(team_a, team_b)
            match = Match(
                team_a=team_a,
                team_b=team_b,
                winner=winner,
                win_probability=confidence,
            )
            matches.append(match)
        all_rounds.append(matches)
        current_teams = [m.winner for m in matches]

    return all_rounds
