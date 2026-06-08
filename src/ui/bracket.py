"""Animated HTML/JS bracket that reveals results progressively."""

import json
from src.data.teams import Match, Team, GroupStanding


FLAG_CDN = "https://flagcdn.com/w40"


def _get_flag_url(team: Team) -> str:
    return f"{FLAG_CDN}/{team.iso_code}.png"


def render_animated_bracket(
    rounds: list[list[Match]],
    group_standings: dict[str, list[GroupStanding]] | None = None,
) -> str:
    """
    Render the full tournament as an animated HTML page.
    Groups reveal first, then knockout rounds one match at a time.
    """
    # Serialize match data for JS
    groups_data = _serialize_groups(group_standings) if group_standings else []
    knockout_data = _serialize_knockout(rounds)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
{_get_styles()}
</head>
<body>
<div id="app">
    <div class="header">
        <div class="title">FIFA WORLD CUP 2026</div>
        <div class="subtitle">AI SIMULATION</div>
    </div>

    <div id="phase-indicator" class="phase-indicator"></div>

    <!-- Group Stage -->
    <div id="groups-section" class="groups-section hidden">
        <div id="groups-grid" class="groups-grid"></div>
    </div>

    <!-- Knockout Bracket -->
    <div id="knockout-section" class="knockout-section hidden">
        <div class="bracket-container">
            <div class="bracket-half bracket-left" id="bracket-left"></div>
            <div class="bracket-final" id="bracket-final"></div>
            <div class="bracket-half bracket-right" id="bracket-right"></div>
        </div>
    </div>

    <!-- Winner Reveal -->
    <div id="winner-section" class="winner-section hidden"></div>
</div>

<script>
const GROUPS_DATA = {json.dumps(groups_data)};
const KNOCKOUT_DATA = {json.dumps(knockout_data)};
const FLAG_CDN = "{FLAG_CDN}";

let speed = 1.0; // multiplier (lower = faster)

// ─── Group Stage Animation ───────────────────────────────
function renderGroupsStructure() {{
    const grid = document.getElementById('groups-grid');
    grid.innerHTML = '';
    GROUPS_DATA.forEach(group => {{
        const div = document.createElement('div');
        div.className = 'group-card';
        div.id = `group-${{group.name}}`;
        div.innerHTML = `
            <div class="group-header">Group ${{group.name}}</div>
            <table class="group-table">
                <thead><tr><th></th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead>
                <tbody id="group-body-${{group.name}}">
                    ${{group.teams.map(t => `
                        <tr id="row-${{group.name}}-${{t.iso}}" class="team-row pending">
                            <td><img class="flag-sm" src="${{FLAG_CDN}}/${{t.iso}}.png"/></td>
                            <td class="team-cell">${{t.name}}</td>
                            <td class="stat">0</td><td class="stat">0</td>
                            <td class="stat">0</td><td class="stat">0</td>
                            <td class="stat">0</td><td class="stat bold">0</td>
                        </tr>
                    `).join('')}}
                </tbody>
            </table>
        `;
        grid.appendChild(div);
    }});
}}

function animateGroupResult(group, teamIso, stats, position) {{
    return new Promise(resolve => {{
        const row = document.getElementById(`row-${{group}}-${{teamIso}}`);
        if (!row) {{ resolve(); return; }}
        const cells = row.querySelectorAll('.stat');
        cells[0].textContent = stats.played;
        cells[1].textContent = stats.won;
        cells[2].textContent = stats.drawn;
        cells[3].textContent = stats.lost;
        cells[4].textContent = stats.gd > 0 ? `+${{stats.gd}}` : stats.gd;
        cells[5].textContent = stats.pts;

        row.classList.remove('pending');
        if (position <= 1) row.classList.add('qualified');
        else if (position === 2) row.classList.add('third-qualified');
        else row.classList.add('eliminated');

        row.style.animation = 'fadeInRow 0.3s ease forwards';
        setTimeout(resolve, 200 * speed);
    }});
}}

async function playGroupStage() {{
    document.getElementById('phase-indicator').textContent = '⚽ GROUP STAGE';
    document.getElementById('groups-section').classList.remove('hidden');
    renderGroupsStructure();

    await sleep(800 * speed);

    for (const group of GROUPS_DATA) {{
        for (let i = 0; i < group.standings.length; i++) {{
            const s = group.standings[i];
            await animateGroupResult(group.name, s.iso, s, i);
        }}
        await sleep(400 * speed);
    }}

    await sleep(1000 * speed);
}}

// ─── Knockout Animation ──────────────────────────────────
function buildKnockoutStructure() {{
    const leftEl = document.getElementById('bracket-left');
    const rightEl = document.getElementById('bracket-right');

    const roundNames = ['Round of 32', 'Round of 16', 'Quarter-finals', 'Semi-finals'];

    // Left: rounds 0-3 (8, 4, 2, 1 matches)
    for (let r = 0; r < 4; r++) {{
        const roundDiv = document.createElement('div');
        roundDiv.className = `round round-${{r}}`;
        roundDiv.innerHTML = `<div class="round-label">${{roundNames[r]}}</div><div class="round-matches" id="left-round-${{r}}"></div>`;
        leftEl.appendChild(roundDiv);
    }}

    // Right: rounds 0-3
    for (let r = 0; r < 4; r++) {{
        const roundDiv = document.createElement('div');
        roundDiv.className = `round round-${{r}}`;
        roundDiv.innerHTML = `<div class="round-label">${{roundNames[r]}}</div><div class="round-matches" id="right-round-${{r}}"></div>`;
        rightEl.appendChild(roundDiv);
    }}
}}

function createMatchElement(match, animate) {{
    const div = document.createElement('div');
    const confClass = match.prob >= 0.75 ? 'conf-high' : match.prob >= 0.6 ? 'conf-good' : match.prob >= 0.5 ? 'conf-mid' : 'conf-low';
    div.className = `match ${{confClass}} ${{animate ? 'match-reveal' : ''}}`;
    div.innerHTML = `
        <div class="team ${{match.winner === match.team_a.name ? 'winner' : 'loser'}}">
            <img class="flag" src="${{FLAG_CDN}}/${{match.team_a.iso}}.png" loading="lazy"/>
            <span class="team-name">${{match.team_a.name}}</span>
        </div>
        <div class="team ${{match.winner === match.team_b.name ? 'winner' : 'loser'}}">
            <img class="flag" src="${{FLAG_CDN}}/${{match.team_b.iso}}.png" loading="lazy"/>
            <span class="team-name">${{match.team_b.name}}</span>
        </div>
        <span class="prob-badge">${{Math.round(match.prob * 100)}}%</span>
    `;
    return div;
}}

async function playKnockoutStage() {{
    document.getElementById('groups-section').classList.add('hidden');
    document.getElementById('knockout-section').classList.remove('hidden');
    buildKnockoutStructure();

    const roundDelays = [600, 900, 1200, 1500, 2000]; // ms per match, slower in later rounds
    const roundNames = ['🏟️ ROUND OF 32', '⚔️ ROUND OF 16', '🔥 QUARTER-FINALS', '🌟 SEMI-FINALS', '🏆 FINAL'];

    for (let r = 0; r < KNOCKOUT_DATA.length; r++) {{
        const matches = KNOCKOUT_DATA[r];
        document.getElementById('phase-indicator').textContent = roundNames[r];
        await sleep(600 * speed);

        if (r === 4) {{
            // Final - render in center
            const finalEl = document.getElementById('bracket-final');
            const m = matches[0];
            finalEl.innerHTML = `
                <div class="final-wrapper match-reveal">
                    <div class="trophy">🏆</div>
                    <div class="final-label">FINAL</div>
                    <div class="final-match">
                        <div class="team ${{m.winner === m.team_a.name ? 'winner' : 'loser'}}">
                            <img class="flag flag-lg" src="${{FLAG_CDN}}/${{m.team_a.iso}}.png"/>
                            <span class="team-name">${{m.team_a.name}}</span>
                        </div>
                        <div class="vs-divider">vs</div>
                        <div class="team ${{m.winner === m.team_b.name ? 'winner' : 'loser'}}">
                            <img class="flag flag-lg" src="${{FLAG_CDN}}/${{m.team_b.iso}}.png"/>
                            <span class="team-name">${{m.team_b.name}}</span>
                        </div>
                    </div>
                </div>
            `;
            await sleep(2000 * speed);
            // Reveal winner
            document.getElementById('winner-section').classList.remove('hidden');
            const winnerIso = m.winner === m.team_a.name ? m.team_a.iso : m.team_b.iso;
            document.getElementById('winner-section').innerHTML = `
                <div class="winner-reveal">
                    <div class="winner-trophy">🏆</div>
                    <img class="winner-flag" src="${{FLAG_CDN}}/${{winnerIso}}.png"/>
                    <div class="winner-name">${{m.winner}}</div>
                    <div class="winner-sub">WORLD CUP CHAMPION 2026</div>
                </div>
            `;
        }} else {{
            // Split matches into left and right halves
            const half = Math.floor(matches.length / 2);
            const leftMatches = matches.slice(0, half);
            const rightMatches = matches.slice(half);

            for (let i = 0; i < Math.max(leftMatches.length, rightMatches.length); i++) {{
                if (i < leftMatches.length) {{
                    const el = document.getElementById(`left-round-${{r}}`);
                    el.appendChild(createMatchElement(leftMatches[i], true));
                }}
                if (i < rightMatches.length) {{
                    const el = document.getElementById(`right-round-${{r}}`);
                    el.appendChild(createMatchElement(rightMatches[i], true));
                }}
                await sleep(roundDelays[r] * speed);
            }}
        }}

        await sleep(800 * speed);
    }}
}}

// ─── Main ────────────────────────────────────────────────
function sleep(ms) {{ return new Promise(r => setTimeout(r, ms)); }}

async function run() {{
    await sleep(500);
    if (GROUPS_DATA.length > 0) {{
        await playGroupStage();
    }}
    await playKnockoutStage();
}}

run();
</script>
</body>
</html>"""


def _serialize_groups(standings: dict[str, list[GroupStanding]]) -> list[dict]:
    """Serialize group standings for JS."""
    result = []
    for group_name in sorted(standings.keys()):
        group_data = {
            "name": group_name,
            "teams": [],
            "standings": [],
        }
        for s in standings[group_name]:
            group_data["teams"].append({
                "name": s.team.name,
                "iso": s.team.iso_code,
            })
            group_data["standings"].append({
                "name": s.team.name,
                "iso": s.team.iso_code,
                "played": s.played,
                "won": s.won,
                "drawn": s.drawn,
                "lost": s.lost,
                "gd": s.goal_difference,
                "pts": s.points,
            })
        result.append(group_data)
    return result


def _serialize_knockout(rounds: list[list[Match]]) -> list[list[dict]]:
    """Serialize knockout matches for JS."""
    result = []
    for round_matches in rounds:
        round_data = []
        for m in round_matches:
            round_data.append({
                "team_a": {"name": m.team_a.name, "iso": m.team_a.iso_code},
                "team_b": {"name": m.team_b.name, "iso": m.team_b.iso_code},
                "winner": m.winner.name,
                "prob": round(m.win_probability, 2),
            })
        result.append(round_data)
    return result


def _get_styles() -> str:
    return """<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        background: linear-gradient(160deg, #0f0326 0%, #1a0a3e 30%, #0d1b2a 70%, #0f0326 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #e2e8f0;
        padding: 16px 12px;
        min-height: 100vh;
    }

    .hidden { display: none !important; }

    .header {
        text-align: center;
        margin-bottom: 12px;
    }
    .title {
        font-size: 18px;
        font-weight: 800;
        letter-spacing: 4px;
        color: #f8fafc;
    }
    .subtitle {
        font-size: 11px;
        letter-spacing: 3px;
        color: #fbbf24;
        margin-top: 2px;
    }

    .phase-indicator {
        text-align: center;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #fbbf24;
        margin: 10px 0;
        min-height: 20px;
    }

    /* ─── Groups ─── */
    .groups-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
    }
    .group-card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 8px;
        padding: 8px;
        border: 1px solid #334155;
    }
    .group-header {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 6px;
    }
    .group-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 9px;
    }
    .group-table th {
        color: #64748b;
        font-weight: 600;
        padding: 2px 3px;
        text-align: center;
    }
    .group-table th:nth-child(2) { text-align: left; }
    .team-row { opacity: 0; transition: opacity 0.3s; }
    .team-row.pending { opacity: 0.3; }
    .team-row.qualified { opacity: 1; }
    .team-row.qualified .team-cell { color: #22c55e; font-weight: 700; }
    .team-row.third-qualified { opacity: 1; }
    .team-row.third-qualified .team-cell { color: #eab308; }
    .team-row.eliminated { opacity: 0.5; }
    .team-row.eliminated .team-cell { color: #ef4444; }
    .flag-sm { width: 16px; height: 11px; border-radius: 1px; vertical-align: middle; }
    .team-cell { text-align: left; padding: 2px 4px; white-space: nowrap; }
    .stat { text-align: center; padding: 2px; color: #94a3b8; }
    .stat.bold { font-weight: 700; color: #e2e8f0; }

    @keyframes fadeInRow {
        from { opacity: 0; transform: translateX(-8px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* ─── Knockout ─── */
    .knockout-section { margin-top: 10px; }
    .bracket-container {
        display: flex;
        align-items: stretch;
        gap: 6px;
        width: 100%;
        min-height: 500px;
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
        min-width: 110px;
        flex: 1;
    }
    .round-label {
        text-align: center;
        font-size: 8px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        padding: 3px 0 5px;
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
    }
    .match.conf-high { border-left-color: #22c55e; }
    .match.conf-good { border-left-color: #84cc16; }
    .match.conf-mid { border-left-color: #eab308; }
    .match.conf-low { border-left-color: #ef4444; }

    .match-reveal {
        animation: matchReveal 0.4s ease forwards;
    }
    @keyframes matchReveal {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }

    .team {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 2px 0;
    }
    .team.winner .team-name { font-weight: 700; color: #f8fafc; }
    .team.loser { opacity: 0.35; }

    .flag { width: 18px; height: 12px; object-fit: cover; border-radius: 2px; flex-shrink: 0; }
    .flag-lg { width: 26px; height: 17px; }

    .team-name {
        font-size: 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 75px;
    }

    .prob-badge {
        position: absolute;
        top: 50%;
        right: 4px;
        transform: translateY(-50%);
        font-size: 8px;
        font-weight: 600;
        color: #64748b;
    }

    /* ─── Final ─── */
    .bracket-final {
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 150px;
        max-width: 16%;
    }
    .final-wrapper { text-align: center; }
    .trophy { font-size: 36px; filter: drop-shadow(0 4px 12px rgba(251,191,36,0.5)); }
    .final-label {
        font-size: 9px; font-weight: 800; letter-spacing: 3px;
        color: #fbbf24; margin: 4px 0 8px;
    }
    .final-match {
        background: rgba(30,41,59,0.95);
        border: 2px solid #fbbf24;
        border-radius: 10px;
        padding: 10px 12px;
    }
    .final-match .team { padding: 4px 0; gap: 8px; }
    .final-match .team-name { font-size: 12px; max-width: 100px; }
    .vs-divider { font-size: 9px; color: #64748b; text-align: center; padding: 2px; font-style: italic; }

    /* ─── Winner ─── */
    .winner-section {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(15, 3, 38, 0.92);
        z-index: 1000;
        animation: fadeIn 0.8s ease;
    }
    .winner-reveal { text-align: center; animation: winnerPop 0.6s ease; }
    .winner-trophy { font-size: 64px; margin-bottom: 12px; }
    .winner-flag {
        width: 80px; height: 54px; object-fit: cover;
        border-radius: 6px; box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        margin-bottom: 10px;
    }
    .winner-name { font-size: 32px; font-weight: 800; color: #fbbf24; }
    .winner-sub { font-size: 11px; letter-spacing: 3px; color: #94a3b8; margin-top: 4px; }

    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes winnerPop {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
</style>"""
