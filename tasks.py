from crewai import Task
from agents import research_agent, analysis_agent, strategy_agent, report_agent


def create_tasks(company_name):
    """Create the sequential task pipeline for business intelligence analysis."""

    research_task = Task(
        description=(
            f"Research {company_name} and deliver a structured briefing covering:\n"
            f"1. Company overview (founding, HQ, leadership, business model)\n"
            f"2. Core products/services and revenue streams\n"
            f"3. Market position and top 3 competitors\n"
            f"4. Key recent developments (last 6 months)\n"
            f"5. Financial highlights (revenue, growth, profitability)\n\n"
            f"Keep your response under 800 words. Use bullet points. Cite sources."
        ),
        agent=research_agent,
        expected_output=(
            "A structured research briefing with 5 clearly labeled sections, "
            "bullet points, and source citations. Max 800 words."
        ),
    )

    analysis_task = Task(
        description=(
            f"Using the research data, analyze {company_name} and provide:\n"
            f"1. SWOT Analysis (4-5 points per category in a table format)\n"
            f"2. Competitive positioning summary (2-3 sentences)\n"
            f"3. Top 3 risks and top 3 growth opportunities\n"
            f"4. Key industry trends affecting the company\n\n"
            f"Be concise and data-driven. Keep under 600 words."
        ),
        agent=analysis_agent,
        expected_output=(
            "SWOT matrix, competitive positioning, risks, opportunities, "
            "and trend analysis. Max 600 words."
        ),
        context=[research_task],
    )

    strategy_task = Task(
        description=(
            f"Based on the analysis, develop strategic recommendations for {company_name}:\n"
            f"1. 3 prioritized strategic initiatives with rationale\n"
            f"2. For each: short-term actions (0-6 months) and long-term vision (6-24 months)\n"
            f"3. Key KPIs to measure success for each initiative\n"
            f"4. Top risks and mitigation approach (1-2 sentences each)\n\n"
            f"Be specific and actionable. Keep under 600 words."
        ),
        agent=strategy_agent,
        expected_output=(
            "3 prioritized strategies with timelines, KPIs, and risk mitigation. "
            "Max 600 words."
        ),
        context=[research_task, analysis_task],
    )

    report_task = Task(
        description=(
            f"Compile all findings into a professional business intelligence report for {company_name}.\n\n"
            f"Report Structure:\n"
            f"# Business Intelligence Report: {company_name}\n"
            f"## Executive Summary (3-4 sentences)\n"
            f"## Company Overview\n"
            f"## Market & Competitive Analysis\n"
            f"## SWOT Analysis (use markdown table)\n"
            f"## Strategic Recommendations\n"
            f"## Implementation Roadmap\n"
            f"## Conclusion (2-3 sentences)\n\n"
            f"Rules:\n"
            f"- Use clean markdown with headers, bullets, and tables\n"
            f"- Professional, executive-level tone\n"
            f"- Total report: 1000-1500 words maximum\n"
            f"- Include a markdown table for SWOT"
        ),
        agent=report_agent,
        expected_output=(
            "A complete, professional markdown business report with all 7 sections, "
            "SWOT table, and actionable recommendations. 1000-1500 words."
        ),
        context=[strategy_task],  # strategy already includes research + analysis context
    )

    return [research_task, analysis_task, strategy_task, report_task]