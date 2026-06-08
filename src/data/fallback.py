"""Static fallback FIFA rankings data (approximate as of mid-2026)."""

from src.data.teams import Team

FALLBACK_RANKINGS: list[Team] = [
    Team("Argentina", "AR", 1885.36, "CONMEBOL", 1),
    Team("France", "FR", 1860.00, "UEFA", 2),
    Team("Spain", "ES", 1836.18, "UEFA", 3),
    Team("England", "EN", 1814.27, "UEFA", 4),
    Team("Brazil", "BR", 1784.44, "CONMEBOL", 5),
    Team("Belgium", "BE", 1772.44, "UEFA", 6),
    Team("Netherlands", "NL", 1762.82, "UEFA", 7),
    Team("Portugal", "PT", 1752.35, "UEFA", 8),
    Team("Germany", "DE", 1743.68, "UEFA", 9),
    Team("Italy", "IT", 1732.55, "UEFA", 10),
    Team("Croatia", "HR", 1721.08, "UEFA", 11),
    Team("Colombia", "CO", 1710.15, "CONMEBOL", 12),
    Team("Uruguay", "UY", 1698.44, "CONMEBOL", 13),
    Team("Morocco", "MA", 1688.92, "CAF", 14),
    Team("Japan", "JP", 1678.38, "AFC", 15),
    Team("USA", "US", 1668.12, "CONCACAF", 16),
    Team("Mexico", "MX", 1658.45, "CONCACAF", 17),
    Team("Senegal", "SN", 1645.28, "CAF", 18),
    Team("Denmark", "DK", 1638.92, "UEFA", 19),
    Team("Switzerland", "CH", 1632.55, "UEFA", 20),
    Team("Iran", "IR", 1622.18, "AFC", 21),
    Team("Australia", "AU", 1612.44, "AFC", 22),
    Team("South Korea", "KR", 1605.82, "AFC", 23),
    Team("Poland", "PL", 1598.15, "UEFA", 24),
    Team("Ecuador", "EC", 1590.28, "CONMEBOL", 25),
    Team("Nigeria", "NG", 1582.44, "CAF", 26),
    Team("Serbia", "RS", 1575.18, "UEFA", 27),
    Team("Turkey", "TR", 1568.92, "UEFA", 28),
    Team("Austria", "AT", 1560.55, "UEFA", 29),
    Team("Ukraine", "UA", 1552.82, "UEFA", 30),
    Team("Scotland", "SC", 1545.15, "UEFA", 31),
    Team("Hungary", "HU", 1538.28, "UEFA", 32),
    Team("Canada", "CA", 1530.44, "CONCACAF", 33),
    Team("Wales", "WL", 1522.18, "UEFA", 34),
    Team("Algeria", "DZ", 1515.92, "CAF", 35),
    Team("Tunisia", "TN", 1508.55, "CAF", 36),
    Team("Cameroon", "CM", 1500.82, "CAF", 37),
    Team("Ghana", "GH", 1492.15, "CAF", 38),
    Team("Saudi Arabia", "SA", 1485.28, "AFC", 39),
    Team("Qatar", "QA", 1478.44, "AFC", 40),
    Team("Costa Rica", "CR", 1470.18, "CONCACAF", 41),
    Team("Peru", "PE", 1462.92, "CONMEBOL", 42),
    Team("Chile", "CL", 1455.55, "CONMEBOL", 43),
    Team("Paraguay", "PY", 1448.82, "CONMEBOL", 44),
    Team("Czech Republic", "CZ", 1440.15, "UEFA", 45),
    Team("Norway", "NO", 1432.28, "UEFA", 46),
    Team("Sweden", "SE", 1425.44, "UEFA", 47),
    Team("Jamaica", "JM", 1418.18, "CONCACAF", 48),
]


def get_fallback_teams(num_teams: int = 32) -> list[Team]:
    """Return top N teams from fallback rankings."""
    return FALLBACK_RANKINGS[:num_teams]
