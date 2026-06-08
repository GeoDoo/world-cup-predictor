from dataclasses import dataclass, field


@dataclass
class Team:
    name: str
    iso_code: str
    fifa_points: float = 0.0
    confederation: str = ""
    ranking: int = 0
    flag_emoji: str = ""

    def __post_init__(self):
        if not self.flag_emoji:
            self.flag_emoji = _iso_to_flag_emoji(self.iso_code)

    def __hash__(self):
        return hash(self.iso_code)

    def __eq__(self, other):
        if isinstance(other, Team):
            return self.iso_code == other.iso_code
        return NotImplemented


@dataclass
class Match:
    team_a: Team
    team_b: Team
    winner: Team | None = None
    win_probability: float = 0.0
    round_name: str = ""


@dataclass
class TournamentConfig:
    name: str
    num_teams: int
    format_type: str  # "32_knockout" or "48_knockout"
    teams: list[Team] = field(default_factory=list)

    @property
    def knockout_rounds(self) -> list[str]:
        if self.format_type == "48_knockout":
            return [
                "Round of 32",
                "Round of 16",
                "Quarter-finals",
                "Semi-finals",
                "Final",
            ]
        return [
            "Round of 16",
            "Quarter-finals",
            "Semi-finals",
            "Final",
        ]


_SPECIAL_FLAGS = {
    "EN": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",  # England
    "SC": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",  # Scotland
    "WL": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",  # Wales
}


def _iso_to_flag_emoji(iso_code: str) -> str:
    if iso_code.upper() in _SPECIAL_FLAGS:
        return _SPECIAL_FLAGS[iso_code.upper()]
    if len(iso_code) != 2:
        return "🏳️"
    return chr(0x1F1E6 + ord(iso_code[0].upper()) - ord("A")) + chr(
        0x1F1E6 + ord(iso_code[1].upper()) - ord("A")
    )


CONFEDERATION_MAP = {
    "UEFA": "Europe",
    "CONMEBOL": "South America",
    "CONCACAF": "North/Central America",
    "CAF": "Africa",
    "AFC": "Asia",
    "OFC": "Oceania",
}
