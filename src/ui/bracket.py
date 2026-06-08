"""HTML/CSS bracket rendering for tournament visualization."""

from src.data.teams import Match, Team


FLAG_CDN = "https://flagcdn.com/w40"


def _get_flag_url(team: Team) -> str:
    return f"{FLAG_CDN}/{team.iso_code}.png"


def _confidence_class(probability: float) -> str:
    if probability >= 0.75:
        return "conf-high"
    elif probability >= 0.6:
        return "conf-good"
    elif probability >= 0.5:
        return "conf-mid"
    return "conf-low"


def render_bracket_html(rounds: list[list[Match]]) -> str:
    """
    Render the full knockout bracket as HTML/CSS.
    Expects 5 rounds: R32(16 matches), R16(8), QF(4), SF(2), Final(1).
    Split into left half (8 R32 → 4 R16 → 2 QF → 1 SF) and right half same,
    meeting in the center final.
    """
    if not rounds or len(rounds) < 5:
        return "<p>No bracket data available.</p>"

    r32, r16, qf, sf, final = rounds

    # Left half: first 8 of R32, first 4 of R16, first 2 of QF, first SF
    left_rounds = [r32[:8], r16[:4], qf[:2], [sf[0]]]
    # Right half: last 8 of R32, last 4 of R16, last 2 of QF, second SF
    right_rounds = [r32[8:], r16[4:], qf[2:], [sf[1]]]

    round_labels = ["Round of 32", "Round of 16", "Quarter-finals", "Semi-finals"]

    left_html = _render_half(left_rounds, round_labels, "left")
    right_html = _render_half(right_rounds, round_labels, "right")
    final_html = _render_final(final[0])

    return f"""<!DOCTYPE html>
<html>
<head>{_get_styles()}</head>
<body>
    <div class="bracket-title">FIFA WORLD CUP 2026 — AI BRACKET PREDICTION</div>
    <div class="bracket-container">
        <div class="bracket-half bracket-left">{left_html}</div>
        <div class="bracket-final">{final_html}</div>
        <div class="bracket-half bracket-right">{right_html}</div>
    </div>
</body>
</html>"""


def _render_half(rounds: list[list[Match]], labels: list[str], side: str) -> str:
    html_parts = []
    for round_idx, matches in enumerate(rounds):
        label = labels[round_idx] if round_idx < len(labels) else ""
        matches_html = "".join(_render_match(m) for m in matches)
        html_parts.append(f"""
            <div class="round round-{round_idx}">
                <div class="round-label">{label}</div>
                <div class="round-matches">{matches_html}</div>
            </div>
        """)
    return "\n".join(html_parts)


def _render_match(match: Match) -> str:
    winner = match.winner
    prob = match.win_probability
    conf_class = _confidence_class(prob)

    a_cls = "team winner" if winner == match.team_a else "team loser"
    b_cls = "team winner" if winner == match.team_b else "team loser"

    return f"""
    <div class="match {conf_class}">
        <div class="{a_cls}">
            <img class="flag" src="{_get_flag_url(match.team_a)}" alt="" loading="lazy"/>
            <span class="team-name">{match.team_a.name}</span>
        </div>
        <div class="{b_cls}">
            <img class="flag" src="{_get_flag_url(match.team_b)}" alt="" loading="lazy"/>
            <span class="team-name">{match.team_b.name}</span>
        </div>
        <span class="prob-badge">{prob:.0%}</span>
    </div>
    """


def _render_final(match: Match) -> str:
    winner = match.winner
    prob = match.win_probability
    a_cls = "team winner" if winner == match.team_a else "team loser"
    b_cls = "team winner" if winner == match.team_b else "team loser"

    return f"""
    <div class="final-wrapper">
        <div class="trophy">🏆</div>
        <div class="final-label">FINAL</div>
        <div class="final-match">
            <div class="{a_cls}">
                <img class="flag flag-lg" src="{_get_flag_url(match.team_a)}" alt="" loading="lazy"/>
                <span class="team-name">{match.team_a.name}</span>
            </div>
            <div class="vs-divider">vs</div>
            <div class="{b_cls}">
                <img class="flag flag-lg" src="{_get_flag_url(match.team_b)}" alt="" loading="lazy"/>
                <span class="team-name">{match.team_b.name}</span>
            </div>
        </div>
        <div class="winner-banner">
            <img class="winner-flag" src="{_get_flag_url(winner)}" alt="" loading="lazy"/>
            <div class="winner-name">{winner.name}</div>
            <div class="winner-sub">PREDICTED WINNER</div>
            <div class="winner-conf">{prob:.0%} confidence</div>
        </div>
    </div>
    """


def _get_styles() -> str:
    return """<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        background: linear-gradient(160deg, #0f0326 0%, #1a0a3e 30%, #0d1b2a 70%, #0f0326 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #e2e8f0;
        padding: 16px 10px;
    }

    .bracket-title {
        text-align: center;
        font-size: 16px;
        font-weight: 800;
        letter-spacing: 3px;
        color: #f8fafc;
        margin-bottom: 16px;
        text-shadow: 0 2px 12px rgba(251,191,36,0.2);
    }

    .bracket-container {
        display: flex;
        align-items: stretch;
        justify-content: center;
        gap: 6px;
        width: 100%;
    }

    .bracket-half {
        display: flex;
        gap: 4px;
        flex: 1;
        max-width: 42%;
    }
    .bracket-left { flex-direction: row; }
    .bracket-right { flex-direction: row-reverse; }

    .round {
        display: flex;
        flex-direction: column;
        min-width: 120px;
        flex: 1;
    }

    .round-label {
        text-align: center;
        font-size: 8px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        padding: 4px 0 6px;
        white-space: nowrap;
    }

    .round-matches {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        flex: 1;
        gap: 3px;
    }

    .match {
        background: rgba(30, 41, 59, 0.9);
        border-radius: 6px;
        border-left: 3px solid #475569;
        padding: 4px 6px;
        position: relative;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .match:hover {
        transform: scale(1.04);
        box-shadow: 0 4px 16px rgba(0,0,0,0.5);
        z-index: 10;
    }
    .match.conf-high { border-left-color: #22c55e; }
    .match.conf-good { border-left-color: #84cc16; }
    .match.conf-mid { border-left-color: #eab308; }
    .match.conf-low { border-left-color: #ef4444; }

    .team {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 2px 0;
    }
    .team.winner .team-name { font-weight: 700; color: #f8fafc; }
    .team.loser { opacity: 0.4; }

    .flag {
        width: 20px;
        height: 14px;
        object-fit: cover;
        border-radius: 2px;
        flex-shrink: 0;
    }
    .flag-lg { width: 28px; height: 19px; }

    .team-name {
        font-size: 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 80px;
    }

    .prob-badge {
        position: absolute;
        top: 50%;
        right: 4px;
        transform: translateY(-50%);
        font-size: 8px;
        font-weight: 600;
        color: #94a3b8;
        background: rgba(15, 23, 42, 0.8);
        padding: 1px 4px;
        border-radius: 3px;
    }

    .bracket-final {
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 160px;
        max-width: 16%;
    }

    .final-wrapper { text-align: center; }

    .trophy {
        font-size: 40px;
        filter: drop-shadow(0 4px 12px rgba(251,191,36,0.5));
    }

    .final-label {
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 3px;
        color: #fbbf24;
        margin: 4px 0 10px;
    }

    .final-match {
        background: rgba(30, 41, 59, 0.95);
        border: 2px solid #fbbf24;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 12px;
    }
    .final-match .team { padding: 4px 0; gap: 8px; }
    .final-match .team-name { font-size: 12px; max-width: 100px; }

    .vs-divider {
        font-size: 9px;
        color: #64748b;
        text-align: center;
        padding: 2px 0;
        font-style: italic;
    }

    .winner-banner {
        background: linear-gradient(135deg, rgba(251,191,36,0.12), rgba(251,191,36,0.04));
        border: 1px solid rgba(251,191,36,0.3);
        border-radius: 10px;
        padding: 12px;
    }
    .winner-flag {
        width: 44px;
        height: 30px;
        object-fit: cover;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.5);
        margin-bottom: 6px;
    }
    .winner-name {
        font-size: 16px;
        font-weight: 800;
        color: #fbbf24;
    }
    .winner-sub {
        font-size: 8px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #94a3b8;
        margin-top: 2px;
    }
    .winner-conf {
        font-size: 10px;
        color: #64748b;
        margin-top: 4px;
    }
</style>"""
