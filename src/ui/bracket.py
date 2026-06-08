"""SVG/HTML bracket rendering for tournament visualization."""

from src.data.teams import Match


def _confidence_color(probability: float) -> str:
    """Map probability to a color (green=high confidence, yellow=toss-up, red=upset)."""
    if probability >= 0.75:
        return "#22c55e"
    elif probability >= 0.6:
        return "#84cc16"
    elif probability >= 0.5:
        return "#eab308"
    else:
        return "#ef4444"


def _flag_svg(iso_code: str, x: float, y: float, size: float = 18) -> str:
    """Generate an emoji flag text element positioned in SVG."""
    if len(iso_code) == 2:
        flag = chr(0x1F1E6 + ord(iso_code[0].upper()) - ord("A")) + chr(
            0x1F1E6 + ord(iso_code[1].upper()) - ord("A")
        )
    else:
        flag = "🏳️"
    return f'<text x="{x}" y="{y + size * 0.7}" font-size="{size}">{flag}</text>'


def render_bracket_svg(
    rounds: list[list[Match]],
    round_names: list[str] | None = None,
    width: int = 1200,
    height: int | None = None,
) -> str:
    """
    Render a full tournament bracket as SVG.

    Left half of bracket feeds from the left, right half feeds from the right,
    final is in the center.
    """
    if not rounds:
        return "<p>No bracket data available.</p>"

    num_rounds = len(rounds)
    first_round_matches = len(rounds[0])

    if height is None:
        height = max(600, first_round_matches * 70 + 100)

    # Split bracket into left and right halves
    half = first_round_matches // 2
    is_split = first_round_matches >= 4

    if is_split:
        left_rounds, right_rounds = _split_bracket(rounds)
        svg = _render_split_bracket(left_rounds, right_rounds, round_names, width, height)
    else:
        svg = _render_linear_bracket(rounds, round_names, width, height)

    return svg


def _split_bracket(rounds: list[list[Match]]) -> tuple[list[list[Match]], list[list[Match]]]:
    """Split rounds into left and right halves."""
    left_rounds = []
    right_rounds = []

    for round_idx, matches in enumerate(rounds):
        if round_idx == len(rounds) - 1 and len(matches) == 1:
            # Final match goes to both
            left_rounds.append(matches)
            right_rounds.append(matches)
        else:
            half = len(matches) // 2
            left_rounds.append(matches[:half])
            right_rounds.append(matches[half:])

    return left_rounds, right_rounds


def _render_split_bracket(
    left_rounds: list[list[Match]],
    right_rounds: list[list[Match]],
    round_names: list[str] | None,
    width: int,
    height: int,
) -> str:
    """Render bracket with left side flowing right and right side flowing left."""
    num_rounds = len(left_rounds)
    center_x = width // 2

    # Column widths
    col_width = (width - 80) // (num_rounds * 2 - 1) if num_rounds > 1 else width // 2

    elements = []
    connectors = []

    # Render left side (rounds flow left -> center)
    for round_idx, matches in enumerate(left_rounds):
        if round_idx == len(left_rounds) - 1 and left_rounds[-1] == right_rounds[-1]:
            break  # Final rendered separately

        x = 40 + round_idx * col_width
        num_matches = len(matches)
        spacing = height / (num_matches + 1)

        for match_idx, match in enumerate(matches):
            y = spacing * (match_idx + 1) - 25
            elements.append(_render_match_box(match, x, y, col_width - 20, "left"))

            # Draw connector to next round
            if round_idx < len(left_rounds) - 2:
                next_y = (height / (len(left_rounds[round_idx + 1]) + 1)) * (match_idx // 2 + 1) - 25
                connectors.append(_draw_connector(
                    x + col_width - 20, y + 25,
                    x + col_width + 10, next_y + 25,
                ))

    # Render right side (rounds flow right -> center)
    for round_idx, matches in enumerate(right_rounds):
        if round_idx == len(right_rounds) - 1 and left_rounds[-1] == right_rounds[-1]:
            break

        x = width - 40 - (round_idx + 1) * col_width + 20
        num_matches = len(matches)
        spacing = height / (num_matches + 1)

        for match_idx, match in enumerate(matches):
            y = spacing * (match_idx + 1) - 25
            elements.append(_render_match_box(match, x, y, col_width - 20, "right"))

            if round_idx < len(right_rounds) - 2:
                next_y = (height / (len(right_rounds[round_idx + 1]) + 1)) * (match_idx // 2 + 1) - 25
                connectors.append(_draw_connector(
                    x, y + 25,
                    x - col_width + col_width - 30, next_y + 25,
                ))

    # Render final in center
    if left_rounds[-1] == right_rounds[-1]:
        final_match = left_rounds[-1][0]
        final_x = center_x - (col_width - 20) // 2
        final_y = height // 2 - 35
        elements.append(_render_final_box(final_match, final_x, final_y, col_width - 20))

    # Round name headers
    headers = []
    if round_names:
        for i, name in enumerate(round_names):
            if i == len(round_names) - 1:
                hx = center_x
            elif i < (len(round_names) - 1) // 2 + 1:
                hx = 40 + i * col_width + (col_width - 20) // 2
            else:
                mirror_i = len(round_names) - 2 - i
                hx = width - 40 - (mirror_i + 1) * col_width + 20 + (col_width - 20) // 2
            headers.append(
                f'<text x="{hx}" y="25" text-anchor="middle" '
                f'font-size="12" font-weight="bold" fill="#94a3b8">{name}</text>'
            )

    svg_content = "\n".join(connectors + elements + headers)
    return _wrap_svg(svg_content, width, height)


def _render_linear_bracket(
    rounds: list[list[Match]],
    round_names: list[str] | None,
    width: int,
    height: int,
) -> str:
    """Render a simple linear bracket (for 2-4 team tournaments)."""
    num_rounds = len(rounds)
    col_width = (width - 80) // num_rounds

    elements = []
    for round_idx, matches in enumerate(rounds):
        x = 40 + round_idx * col_width
        spacing = height / (len(matches) + 1)

        for match_idx, match in enumerate(matches):
            y = spacing * (match_idx + 1) - 25
            elements.append(_render_match_box(match, x, y, col_width - 20, "left"))

    svg_content = "\n".join(elements)
    return _wrap_svg(svg_content, width, height)


def _render_match_box(match: Match, x: float, y: float, w: float, side: str) -> str:
    """Render a single match box with two teams."""
    winner = match.winner
    prob = match.win_probability
    color = _confidence_color(prob)

    team_a_bold = "bold" if winner == match.team_a else "normal"
    team_b_bold = "bold" if winner == match.team_b else "normal"
    team_a_opacity = "1" if winner == match.team_a else "0.5"
    team_b_opacity = "1" if winner == match.team_b else "0.5"

    box_w = min(w, 180)

    return f"""
    <g transform="translate({x},{y})">
        <rect x="0" y="0" width="{box_w}" height="50" rx="6" ry="6"
              fill="#1e293b" stroke="{color}" stroke-width="2"/>
        <line x1="0" y1="25" x2="{box_w}" y2="25" stroke="#334155" stroke-width="1"/>
        <!-- Team A -->
        <text x="28" y="17" font-size="11" fill="#f1f5f9" font-weight="{team_a_bold}"
              opacity="{team_a_opacity}">{match.team_a.name}</text>
        {_flag_svg(match.team_a.iso_code, 6, 4, 14)}
        <!-- Team B -->
        <text x="28" y="42" font-size="11" fill="#f1f5f9" font-weight="{team_b_bold}"
              opacity="{team_b_opacity}">{match.team_b.name}</text>
        {_flag_svg(match.team_b.iso_code, 6, 29, 14)}
        <!-- Probability -->
        <text x="{box_w - 6}" y="30" font-size="9" fill="{color}"
              text-anchor="end" opacity="0.9">{prob:.0%}</text>
    </g>
    """


def _render_final_box(match: Match, x: float, y: float, w: float) -> str:
    """Render the final match with trophy and winner highlight."""
    winner = match.winner
    prob = match.win_probability
    color = _confidence_color(prob)
    box_w = min(w, 200)

    team_a_bold = "bold" if winner == match.team_a else "normal"
    team_b_bold = "bold" if winner == match.team_b else "normal"
    team_a_opacity = "1" if winner == match.team_a else "0.5"
    team_b_opacity = "1" if winner == match.team_b else "0.5"

    return f"""
    <g transform="translate({x},{y})">
        <rect x="0" y="0" width="{box_w}" height="70" rx="8" ry="8"
              fill="#1e293b" stroke="#fbbf24" stroke-width="3"/>
        <text x="{box_w // 2}" y="-8" text-anchor="middle" font-size="20">🏆</text>
        <text x="{box_w // 2}" y="-22" text-anchor="middle" font-size="10"
              fill="#fbbf24" font-weight="bold">FINAL</text>
        <line x1="0" y1="35" x2="{box_w}" y2="35" stroke="#334155" stroke-width="1"/>
        <!-- Team A -->
        <text x="30" y="23" font-size="12" fill="#f1f5f9" font-weight="{team_a_bold}"
              opacity="{team_a_opacity}">{match.team_a.name}</text>
        {_flag_svg(match.team_a.iso_code, 6, 8, 16)}
        <!-- Team B -->
        <text x="30" y="57" font-size="12" fill="#f1f5f9" font-weight="{team_b_bold}"
              opacity="{team_b_opacity}">{match.team_b.name}</text>
        {_flag_svg(match.team_b.iso_code, 6, 42, 16)}
        <!-- Winner label -->
        <text x="{box_w // 2}" y="85" text-anchor="middle" font-size="11"
              fill="#fbbf24" font-weight="bold">WINNER: {winner.name} {winner.flag_emoji}</text>
        <text x="{box_w // 2}" y="100" text-anchor="middle" font-size="9"
              fill="{color}">{prob:.0%} confidence</text>
    </g>
    """


def _draw_connector(x1: float, y1: float, x2: float, y2: float) -> str:
    """Draw a bracket connector line between rounds."""
    mid_x = (x1 + x2) / 2
    return (
        f'<path d="M {x1} {y1} H {mid_x} V {y2} H {x2}" '
        f'fill="none" stroke="#475569" stroke-width="1.5" opacity="0.6"/>'
    )


def _wrap_svg(content: str, width: int, height: int) -> str:
    """Wrap SVG content in full SVG document with background."""
    return f"""
    <div style="overflow-x: auto; background: #0f172a; border-radius: 12px; padding: 20px;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height + 120}"
             width="{width}" height="{height + 120}"
             style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
            <rect width="{width}" height="{height + 120}" fill="#0f172a" rx="12"/>
            <text x="{width // 2}" y="55" text-anchor="middle" font-size="22"
                  fill="#f8fafc" font-weight="bold">WORLD CUP BRACKET PREDICTION</text>
            <g transform="translate(0, 70)">
                {content}
            </g>
        </svg>
    </div>
    """
