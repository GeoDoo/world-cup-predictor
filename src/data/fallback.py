"""
Real 2026 FIFA World Cup data.
48 qualified teams with actual FIFA ranking points (April 2026).
Official group draw and tournament structure.
"""

from src.data.teams import Team

# All 48 qualified teams with real FIFA rankings (April 1, 2026)
TEAMS: dict[str, Team] = {
    "France": Team("France", "fr", 1877.32, "UEFA", 1),
    "Spain": Team("Spain", "es", 1876.40, "UEFA", 2),
    "Argentina": Team("Argentina", "ar", 1874.81, "CONMEBOL", 3),
    "England": Team("England", "gb-eng", 1825.97, "UEFA", 4),
    "Portugal": Team("Portugal", "pt", 1763.83, "UEFA", 5),
    "Brazil": Team("Brazil", "br", 1761.16, "CONMEBOL", 6),
    "Netherlands": Team("Netherlands", "nl", 1757.87, "UEFA", 7),
    "Morocco": Team("Morocco", "ma", 1755.87, "CAF", 8),
    "Belgium": Team("Belgium", "be", 1734.71, "UEFA", 9),
    "Germany": Team("Germany", "de", 1730.37, "UEFA", 10),
    "Croatia": Team("Croatia", "hr", 1717.07, "UEFA", 11),
    "Colombia": Team("Colombia", "co", 1693.09, "CONMEBOL", 13),
    "Senegal": Team("Senegal", "sn", 1688.99, "CAF", 14),
    "Mexico": Team("Mexico", "mx", 1681.03, "CONCACAF", 15),
    "USA": Team("USA", "us", 1673.13, "CONCACAF", 16),
    "Uruguay": Team("Uruguay", "uy", 1673.07, "CONMEBOL", 17),
    "Japan": Team("Japan", "jp", 1660.43, "AFC", 18),
    "Switzerland": Team("Switzerland", "ch", 1649.40, "UEFA", 19),
    "Iran": Team("Iran", "ir", 1615.30, "AFC", 21),
    "Turkey": Team("Turkey", "tr", 1599.04, "UEFA", 22),
    "Ecuador": Team("Ecuador", "ec", 1594.78, "CONMEBOL", 23),
    "Austria": Team("Austria", "at", 1593.45, "UEFA", 24),
    "South Korea": Team("South Korea", "kr", 1588.66, "AFC", 25),
    "Australia": Team("Australia", "au", 1580.67, "AFC", 27),
    "Algeria": Team("Algeria", "dz", 1564.26, "CAF", 28),
    "Egypt": Team("Egypt", "eg", 1563.24, "CAF", 29),
    "Canada": Team("Canada", "ca", 1556.48, "CONCACAF", 30),
    "Norway": Team("Norway", "no", 1550.94, "UEFA", 31),
    "Panama": Team("Panama", "pa", 1540.64, "CONCACAF", 33),
    "Ivory Coast": Team("Ivory Coast", "ci", 1532.98, "CAF", 34),
    "Sweden": Team("Sweden", "se", 1514.77, "UEFA", 38),
    "Paraguay": Team("Paraguay", "py", 1503.50, "CONMEBOL", 40),
    "Czechia": Team("Czechia", "cz", 1501.38, "UEFA", 41),
    "Scotland": Team("Scotland", "gb-sct", 1498.35, "UEFA", 43),
    "Tunisia": Team("Tunisia", "tn", 1479.04, "CAF", 44),
    "DR Congo": Team("DR Congo", "cd", 1478.35, "CAF", 46),
    "Uzbekistan": Team("Uzbekistan", "uz", 1465.34, "AFC", 50),
    "Qatar": Team("Qatar", "qa", 1454.96, "AFC", 55),
    "Iraq": Team("Iraq", "iq", 1447.14, "AFC", 57),
    "South Africa": Team("South Africa", "za", 1429.73, "CAF", 60),
    "Saudi Arabia": Team("Saudi Arabia", "sa", 1421.43, "AFC", 61),
    "Jordan": Team("Jordan", "jo", 1391.45, "AFC", 63),
    "Bosnia": Team("Bosnia", "ba", 1385.84, "UEFA", 65),
    "Cape Verde": Team("Cape Verde", "cv", 1366.13, "CAF", 69),
    "Ghana": Team("Ghana", "gh", 1346.31, "CAF", 74),
    "Curacao": Team("Curacao", "cw", 1294.65, "CONCACAF", 82),
    "Haiti": Team("Haiti", "ht", 1291.71, "CONCACAF", 83),
    "New Zealand": Team("New Zealand", "nz", 1281.57, "OFC", 85),
}

# Official 2026 World Cup Group Draw
GROUPS: dict[str, list[str]] = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Bosnia", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["USA", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# Predetermined Round of 32 bracket structure (FIFA official).
# Format: (slot_label, team_source)
# team_source is either "1X" (winner of group X), "2X" (runner-up of group X),
# or "3XXXXX" (3rd place from one of groups X depending on which 8 qualify).
# The bracket is split into two halves that meet in the final.
R32_BRACKET_LEFT = [
    ("M73", "2A", "2B"),
    ("M74", "1E", "3ABCDF"),
    ("M75", "1F", "2C"),
    ("M76", "1C", "2F"),
    ("M77", "1I", "3CDFGH"),
    ("M78", "2E", "2I"),
    ("M79", "1A", "3CEFHI"),
    ("M80", "1D", "3EHIJK"),
]

R32_BRACKET_RIGHT = [
    ("M81", "2D", "2L"),
    ("M82", "1G", "3ABEFJ"),
    ("M83", "1H", "2J"),
    ("M84", "1J", "2H"),
    ("M85", "1K", "3BEFIJ"),
    ("M86", "2G", "2K"),
    ("M87", "1L", "3DGHKL"),
    ("M88", "1B", "3DGHKL"),
]

# Round of 16 matchups (winners of R32 matches)
R16_MATCHES = [
    ("M89", "M74", "M77"),
    ("M90", "M73", "M75"),
    ("M91", "M76", "M78"),
    ("M92", "M79", "M80"),
    ("M93", "M82", "M83"),
    ("M94", "M81", "M84"),
    ("M95", "M85", "M86"),
    ("M96", "M87", "M88"),
]

# Quarter-final matchups
QF_MATCHES = [
    ("M97", "M89", "M90"),
    ("M98", "M91", "M92"),
    ("M99", "M93", "M94"),
    ("M100", "M95", "M96"),
]

# Semi-final matchups
SF_MATCHES = [
    ("M101", "M97", "M98"),
    ("M102", "M99", "M100"),
]

# Final
FINAL_MATCH = ("M103", "M101", "M102")


def get_group_teams(group_name: str) -> list[Team]:
    """Get Team objects for a group."""
    return [TEAMS[name] for name in GROUPS[group_name]]


def get_all_teams() -> list[Team]:
    """Get all 48 qualified teams."""
    return list(TEAMS.values())
