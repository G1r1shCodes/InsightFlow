"""
Visualization module for InsightFlow.
Parses report text and generates interactive Plotly charts.
"""

import plotly.graph_objects as go
import re


def _extract_swot(report_text: str) -> dict:
    """Extract SWOT items from the report text using heuristic parsing."""
    swot = {"Strengths": [], "Weaknesses": [], "Opportunities": [], "Threats": []}

    # Try to find SWOT section
    swot_pattern = re.compile(
        r"(?:#{1,3}\s*)?SWOT\s*Analysis.*?(?=#{1,3}\s|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    match = swot_pattern.search(report_text)
    section = match.group(0) if match else report_text

    current_category = None
    for line in section.split("\n"):
        line_stripped = line.strip().strip("|").strip()
        # Detect category headers
        for cat in swot:
            if re.search(rf"\b{cat}\b", line_stripped, re.IGNORECASE):
                current_category = cat
                break

        # Count bullet points or table rows as items
        if current_category and (
            line_stripped.startswith(("-", "*", "•", "–"))
            or ("|" in line and line_stripped and not line_stripped.startswith("---"))
        ):
            # Clean the text
            clean = re.sub(r"^[-*•–|]+\s*", "", line_stripped).strip("|").strip()
            clean = re.sub(r"\*\*", "", clean).strip()
            if clean and len(clean) > 5 and not clean.startswith("---"):
                swot[current_category].append(clean)

    return swot


def _extract_strategies(report_text: str) -> list[dict]:
    """Extract strategic initiatives from the report."""
    strategies = []

    # Find strategy/recommendations section
    strat_pattern = re.compile(
        r"(?:#{1,3}\s*)?(?:Strategic\s*Recommendations|Strategy).*?(?=#{1,3}\s[A-Z]|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    match = strat_pattern.search(report_text)
    section = match.group(0) if match else ""

    # Extract numbered strategies
    items = re.findall(
        r"(?:\d+[\.\)]\s*\*\*(.+?)\*\*|\*\*(\d+[\.\)].+?)\*\*)",
        section,
    )

    for groups in items:
        name = (groups[0] or groups[1]).strip()
        if name and len(name) > 3:
            strategies.append({"name": name[:50]})

    # Fallback: just find bold items
    if not strategies:
        items = re.findall(r"\*\*(.+?)\*\*", section)
        for item in items[:5]:
            clean = item.strip()
            if len(clean) > 5 and not any(
                kw in clean.lower()
                for kw in ["kpi", "risk", "mitigation", "timeline", "resource"]
            ):
                strategies.append({"name": clean[:50]})

    return strategies[:5]


def create_swot_chart(report_text: str) -> go.Figure | None:
    """Create a SWOT quadrant visualization."""
    swot = _extract_swot(report_text)

    # Need at least some data
    total_items = sum(len(v) for v in swot.values())
    if total_items < 4:
        return None

    counts = {k: len(v) for k, v in swot.items()}

    colors = {
        "Strengths": "#10b981",
        "Weaknesses": "#ef4444",
        "Opportunities": "#3b82f6",
        "Threats": "#f59e0b",
    }

    fig = go.Figure()

    categories = list(swot.keys())
    values = [counts[c] for c in categories]
    bar_colors = [colors[c] for c in categories]

    # Truncate items for hover text
    hover_texts = []
    for cat in categories:
        items = swot[cat][:5]
        text = f"<b>{cat}</b><br>" + "<br>".join(
            f"• {item[:60]}{'...' if len(item) > 60 else ''}" for item in items
        )
        if not items:
            text = f"<b>{cat}</b><br>No items extracted"
        hover_texts.append(text)

    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            marker_color=bar_colors,
            marker_line_width=0,
            hovertext=hover_texts,
            hoverinfo="text",
            text=values,
            textposition="outside",
            textfont=dict(size=14, color="#e2e8f0"),
        )
    )

    fig.update_layout(
        title=dict(
            text="SWOT Analysis Overview",
            font=dict(size=18, color="#e2e8f0"),
            x=0.5,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=13, color="#e2e8f0"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            title="Number of factors",
            tickfont=dict(color="#a0aec0"),
            titlefont=dict(color="#a0aec0"),
        ),
        height=380,
        margin=dict(t=60, b=40, l=50, r=30),
        bargap=0.35,
    )

    return fig


def create_swot_radar(report_text: str) -> go.Figure | None:
    """Create a SWOT radar/spider chart."""
    swot = _extract_swot(report_text)
    total_items = sum(len(v) for v in swot.values())
    if total_items < 4:
        return None

    categories = list(swot.keys())
    values = [len(swot[c]) for c in categories]
    # Close the polygon
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(102, 126, 234, 0.2)",
            line=dict(color="#667eea", width=2),
            marker=dict(size=8, color="#667eea"),
            name="SWOT",
        )
    )

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                gridcolor="rgba(255,255,255,0.1)",
                tickfont=dict(color="#a0aec0"),
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color="#e2e8f0"),
                gridcolor="rgba(255,255,255,0.1)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        title=dict(
            text="SWOT Radar",
            font=dict(size=18, color="#e2e8f0"),
            x=0.5,
        ),
        height=400,
        margin=dict(t=60, b=40, l=60, r=60),
        showlegend=False,
    )

    return fig


def create_strategy_priority_chart(report_text: str) -> go.Figure | None:
    """Create a horizontal bar chart of strategic priorities."""
    strategies = _extract_strategies(report_text)

    if len(strategies) < 2:
        return None

    names = [s["name"] for s in strategies]
    # Assign decreasing priority scores
    scores = list(range(len(names), 0, -1))
    # Color gradient from high to low priority
    colors = ["#667eea", "#764ba2", "#9f7aea", "#b794f4", "#d6bcfa"]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=names,
            x=scores,
            orientation="h",
            marker_color=colors[: len(names)],
            marker_line_width=0,
            text=[f"Priority {i+1}" for i in range(len(names))],
            textposition="inside",
            textfont=dict(color="white", size=12),
        )
    )

    fig.update_layout(
        title=dict(
            text="Strategic Priorities",
            font=dict(size=18, color="#e2e8f0"),
            x=0.5,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
        ),
        yaxis=dict(
            tickfont=dict(size=11, color="#e2e8f0"),
            autorange="reversed",
        ),
        height=300,
        margin=dict(t=60, b=30, l=200, r=30),
    )

    return fig


def create_risk_opportunity_gauge(report_text: str) -> go.Figure | None:
    """Create a simple risk vs opportunity balance gauge."""
    swot = _extract_swot(report_text)

    opportunities = len(swot.get("Opportunities", []))
    threats = len(swot.get("Threats", []))
    total = opportunities + threats

    if total == 0:
        return None

    opp_pct = (opportunities / total) * 100

    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=opp_pct,
            number=dict(suffix="%", font=dict(size=36, color="#e2e8f0")),
            title=dict(
                text="Opportunity Score",
                font=dict(size=16, color="#a0aec0"),
            ),
            gauge=dict(
                axis=dict(
                    range=[0, 100],
                    tickfont=dict(color="#a0aec0"),
                    tickcolor="rgba(255,255,255,0.2)",
                ),
                bgcolor="rgba(0,0,0,0)",
                bar=dict(color="#667eea"),
                steps=[
                    dict(range=[0, 33], color="rgba(239,68,68,0.2)"),
                    dict(range=[33, 66], color="rgba(245,158,11,0.2)"),
                    dict(range=[66, 100], color="rgba(16,185,129,0.2)"),
                ],
                threshold=dict(
                    line=dict(color="#10b981", width=3),
                    thickness=0.8,
                    value=opp_pct,
                ),
            ),
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        height=280,
        margin=dict(t=40, b=20, l=30, r=30),
    )

    return fig
