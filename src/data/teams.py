from dataclasses import dataclass, field


@dataclass
class Team:
    name: str
    iso_code: str
    fifa_points: float = 0.0
    confederation: str = ""
    ranking: int = 0

    @property
    def flag_url(self) -> str:
        return f"https://flagcdn.com/w40/{self.iso_code}.png"

    def __hash__(self):
        return hash(self.iso_code)

    def __eq__(self, other):
        if isinstance(other, Team):
            return self.iso_code == other.iso_code
        return NotImplemented

    def __repr__(self):
        return f"Team({self.name})"


@dataclass
class Match:
    team_a: Team
    team_b: Team
    winner: Team | None = None
    score_a: int = 0
    score_b: int = 0
    win_probability: float = 0.0
    round_name: str = ""
    is_draw: bool = False


@dataclass
class GroupStanding:
    team: Team
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def points(self) -> int:
        return self.won * 3 + self.drawn

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def sort_key(self) -> tuple:
        return (-self.points, -self.goal_difference, -self.goals_for)
