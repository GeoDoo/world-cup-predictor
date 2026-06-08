import os
import requests
from src.data.teams import Team


API_BASE_URL = "https://footballdata.io/api/v1"


def fetch_fifa_rankings(limit: int = 50) -> list[Team]:
    """Fetch current FIFA men's rankings from the Footballdata.io API."""
    api_key = os.environ.get("FIFA_API_KEY", "")
    if not api_key:
        return []

    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"ranking_type": "men", "limit": limit}

    try:
        response = requests.get(
            f"{API_BASE_URL}/fifa-rankings/current",
            headers=headers,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return _parse_rankings(data)
    except (requests.RequestException, KeyError, ValueError):
        return []


def _parse_rankings(data: dict) -> list[Team]:
    teams = []
    rankings = data.get("data", data.get("rankings", []))

    for entry in rankings:
        country = entry.get("country", {})
        points_data = entry.get("points", {})

        team = Team(
            name=country.get("name", "Unknown"),
            iso_code=country.get("iso2", "XX").upper(),
            fifa_points=float(points_data.get("total", 0)),
            confederation=entry.get("confederation", {}).get("code", ""),
            ranking=int(entry.get("rank", 0)),
        )
        teams.append(team)

    return teams
