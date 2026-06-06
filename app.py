import streamlit as st
from crewai import Crew, Process
from agents import (
    research_agent, analysis_agent, strategy_agent, report_agent,
    LLM_PROVIDER, LLM_MODEL, get_fallback_llm,
)
from tasks import create_tasks
from visualizations import (
    create_swot_chart,
    create_swot_radar,
    create_strategy_priority_chart,
    create_risk_opportunity_gauge,
)
import os
import time
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InsightFlow — AI Business Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme-Adaptive CSS ────────────────────────────────────────────────────────
# Uses CSS custom properties that work in both light and dark Streamlit themes.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── CSS Variables (theme-adaptive) ─────────────────────────────────── */
    :root {
        --card-bg: rgba(102, 126, 234, 0.08);
        --card-border: rgba(102, 126, 234, 0.18);
        --card-hover-shadow: rgba(102, 126, 234, 0.2);
        --text-primary: inherit;
        --text-secondary: rgba(150, 150, 170, 1);
        --surface-bg: rgba(255, 255, 255, 0.03);
        --surface-border: rgba(255, 255, 255, 0.08);
        --success-bg: rgba(16, 185, 129, 0.12);
        --success-border: rgba(16, 185, 129, 0.3);
        --success-text: #10b981;
        --status-bg: rgba(245, 158, 11, 0.12);
        --status-text: #f59e0b;
    }

    /* ── Global ─────────────────────────────────────────────────────────── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Header ─────────────────────────────────────────────────────────── */
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: var(--text-secondary);
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 1.5rem;
    }

    /* ── Agent Cards (works in both themes) ─────────────────────────────── */
    .agent-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px var(--card-hover-shadow);
    }
    .agent-emoji { font-size: 1.3rem; }
    .agent-name {
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--text-primary);
    }
    .agent-desc {
        font-size: 0.78rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }

    /* ── Status Badges ──────────────────────────────────────────────────── */
    .status-running {
        display: inline-block;
        background: var(--status-bg);
        color: var(--status-text);
        padding: 4px 14px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* ── Success Banner ─────────────────────────────────────────────────── */
    .success-banner {
        background: var(--success-bg);
        border: 1px solid var(--success-border);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: var(--success-text);
        text-align: center;
        margin-bottom: 1rem;
        font-size: 1.05rem;
    }

    /* ── Report Container ───────────────────────────────────────────────── */
    .report-container {
        background: var(--surface-bg);
        border: 1px solid var(--surface-border);
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1rem;
    }

    /* ── Viz Section Header ─────────────────────────────────────────────── */
    .viz-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        padding-top: 1rem;
    }
    .viz-subtext {
        color: var(--text-secondary);
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }

    /* ── Feature Cards ──────────────────────────────────────────────────── */
    .feature-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 1.5rem;
        height: 100%;
        transition: transform 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-3px);
    }
    .feature-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.4rem;
    }
    .feature-desc {
        font-size: 0.88rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }

    /* ── Footer ─────────────────────────────────────────────────────────── */
    .footer-text {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.75rem;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🔍 InsightFlow</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Multi-Agent AI Business Intelligence Report Generator</div>',
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    company_name = st.text_input(
        "Company Name",
        placeholder="e.g., Tesla, Apple, Zomato",
        help="Enter any company name to generate a full business intelligence report.",
    )

    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")

    agents_info = [
        ("🔎", "Research Agent", "Gathers company data & market intel"),
        ("📊", "Analysis Agent", "SWOT analysis & trend identification"),
        ("🎯", "Strategy Agent", "Strategic recommendations & roadmap"),
        ("📝", "Report Agent", "Professional report compilation"),
    ]
    for emoji, name, desc in agents_info:
        st.markdown(
            f"""<div class="agent-card">
                <span class="agent-emoji">{emoji}</span>
                <span class="agent-name">{name}</span>
                <div class="agent-desc">{desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    generate_btn = st.button(
        "🚀 Generate Report", type="primary", use_container_width=True
    )

    st.markdown("---")
    st.markdown(
        f'<div class="footer-text">Powered by CrewAI + {LLM_PROVIDER}<br>{LLM_MODEL}</div>',
        unsafe_allow_html=True,
    )

# ── Main Area ─────────────────────────────────────────────────────────────────
if generate_btn and company_name:

    status_placeholder = st.empty()

    with st.spinner(""):
        status_placeholder.markdown(
            '<div class="status-running">⏳ Initializing AI agents...</div>',
            unsafe_allow_html=True,
        )

        # Create tasks & crew
        tasks = create_tasks(company_name)
        crew = Crew(
            agents=[research_agent, analysis_agent, strategy_agent, report_agent],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        # Execute with retry + automatic provider fallback
        max_attempts = 3
        result = None
        current_provider = LLM_PROVIDER
        switched_provider = False

        for attempt in range(1, max_attempts + 1):
            try:
                status_placeholder.markdown(
                    f'<div class="status-running">🤖 AI agents working via {current_provider}... '
                    f'(attempt {attempt}/{max_attempts})</div>',
                    unsafe_allow_html=True,
                )
                result = crew.kickoff(inputs={"company": company_name})
                break

            except Exception as e:
                error_msg = str(e).lower()

                # Detect retryable errors: rate limits, timeouts, connection issues
                is_rate_limit = any(kw in error_msg for kw in [
                    "429", "rate_limit", "resource_exhausted",
                    "rate limit", "too many requests",
                ])
                is_timeout = any(kw in error_msg for kw in [
                    "timeout", "timed out", "time out",
                    "deadline exceeded", "connection aborted",
                    "readtimeout", "connecttimeout",
                ])
                is_service_error = any(kw in error_msg for kw in [
                    "503", "502", "500", "service unavailable",
                    "internal server error", "bad gateway",
                    "connection error", "connection reset",
                ])
                is_retryable = is_rate_limit or is_timeout or is_service_error

                if is_retryable and attempt < max_attempts:
                    # Try switching to fallback provider if available
                    if not switched_provider:
                        fb_llm, fb_prov, fb_model = get_fallback_llm()
                        if fb_llm is not None:
                            current_provider = fb_prov
                            switched_provider = True
                            status_placeholder.markdown(
                                f'<div class="status-running">🔄 Switching to {fb_prov} '
                                f'({fb_model})...</div>',
                                unsafe_allow_html=True,
                            )
                            time.sleep(3)

                            # Rebuild agents with fallback LLM
                            from crewai import Agent
                            from tools import search_tool as _st

                            _fb_research = Agent(
                                role=research_agent.role,
                                goal=research_agent.goal,
                                backstory=research_agent.backstory,
                                verbose=True,
                                allow_delegation=False,
                                llm=fb_llm,
                                tools=[_st],
                                max_iter=2,
                                max_execution_time=600,
                            )
                            _fb_analysis = Agent(
                                role=analysis_agent.role,
                                goal=analysis_agent.goal,
                                backstory=analysis_agent.backstory,
                                verbose=True,
                                allow_delegation=False,
                                llm=fb_llm,
                                max_iter=1,
                                max_execution_time=300,
                            )
                            _fb_strategy = Agent(
                                role=strategy_agent.role,
                                goal=strategy_agent.goal,
                                backstory=strategy_agent.backstory,
                                verbose=True,
                                allow_delegation=False,
                                llm=fb_llm,
                                max_iter=1,
                                max_execution_time=300,
                            )
                            _fb_report = Agent(
                                role=report_agent.role,
                                goal=report_agent.goal,
                                backstory=report_agent.backstory,
                                verbose=True,
                                allow_delegation=False,
                                llm=fb_llm,
                                max_iter=1,
                                max_execution_time=300,
                            )

                            tasks = create_tasks(company_name)
                            crew = Crew(
                                agents=[_fb_research, _fb_analysis, _fb_strategy, _fb_report],
                                tasks=tasks,
                                process=Process.sequential,
                                verbose=True,
                            )
                            continue  # Retry immediately with new provider

                    # Same provider retry — wait before retrying
                    wait_time = 30 * attempt  # 30s, 60s
                    error_type = (
                        "Rate limited" if is_rate_limit
                        else "Timed out" if is_timeout
                        else "Service error"
                    )
                    status_placeholder.markdown(
                        f'<div class="status-running">⏱️ {error_type} — waiting '
                        f'{wait_time}s before retry {attempt + 1}...</div>',
                        unsafe_allow_html=True,
                    )
                    time.sleep(wait_time)
                    tasks = create_tasks(company_name)
                    crew = Crew(
                        agents=[research_agent, analysis_agent, strategy_agent, report_agent],
                        tasks=tasks,
                        process=Process.sequential,
                        verbose=True,
                    )
                else:
                    status_placeholder.empty()
                    if is_retryable:
                        st.error("⏱️ Service unavailable after multiple retries.")
                        st.info(
                            f"💡 Both {LLM_PROVIDER} and fallback providers hit limits. "
                            "Wait 1-2 minutes and try again."
                        )
                    else:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Check your API keys in the .env file.")
                    result = None
                    break

    # ── Display Results ───────────────────────────────────────────────────────
    if result is not None:
        report_text = str(result)
        status_placeholder.empty()

        # Success banner
        st.markdown(
            '<div class="success-banner">✅ Report Generated Successfully!</div>',
            unsafe_allow_html=True,
        )

        # Header + download
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"## 📄 Business Intelligence Report: {company_name}")
        with col2:
            st.download_button(
                label="📥 Download",
                data=report_text,
                file_name=f"{company_name.replace(' ', '_')}_BI_Report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        # ── Visualizations ────────────────────────────────────────────────
        st.markdown(
            '<div class="viz-header">📊 Visual Analytics</div>'
            '<div class="viz-subtext">Auto-generated from the report data</div>',
            unsafe_allow_html=True,
        )

        viz_col1, viz_col2 = st.columns(2)

        with viz_col1:
            swot_chart = create_swot_chart(report_text)
            if swot_chart:
                st.plotly_chart(swot_chart, use_container_width=True)

        with viz_col2:
            radar_chart = create_swot_radar(report_text)
            if radar_chart:
                st.plotly_chart(radar_chart, use_container_width=True)

        viz_col3, viz_col4 = st.columns(2)

        with viz_col3:
            strategy_chart = create_strategy_priority_chart(report_text)
            if strategy_chart:
                st.plotly_chart(strategy_chart, use_container_width=True)

        with viz_col4:
            gauge_chart = create_risk_opportunity_gauge(report_text)
            if gauge_chart:
                st.plotly_chart(gauge_chart, use_container_width=True)

        # ── Full Report Text ──────────────────────────────────────────────
        st.markdown("---")
        st.markdown(
            '<div class="viz-header">📝 Full Report</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(report_text)
        st.markdown("</div>", unsafe_allow_html=True)

elif generate_btn:
    st.warning("⚠️ Please enter a company name to get started.")

else:
    # ── Landing Page ──────────────────────────────────────────────────────
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    features = [
        ("🚀", "Fast", "Generate comprehensive reports in minutes using 4 specialized AI agents working in sequence."),
        ("🎯", "Accurate", "Web-powered research combined with SWOT analysis, competitive intelligence, and strategic frameworks."),
        ("📊", "Actionable", "Get prioritized strategies with KPIs, timelines, and risk mitigation — ready for executive review."),
    ]

    for col, (icon, title, desc) in zip([col1, col2, col3], features):
        with col:
            st.markdown(
                f"""<div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("📚 How It Works", expanded=False):
        st.markdown(f"""
        ### Multi-Agent Orchestration

        InsightFlow uses **4 specialized AI agents** powered by **{LLM_PROVIDER}'s {LLM_MODEL}** working sequentially:

        | Agent | Role | Output |
        |-------|------|--------|
        | 🔎 Research | Gathers company data from web sources | Structured research briefing |
        | 📊 Analysis | SWOT, competitive positioning, trends | Analytical framework |
        | 🎯 Strategy | Strategic initiatives & roadmap | Prioritized action plan |
        | 📝 Report | Compiles final executive report | Professional markdown report |

        ### Visualizations
        After report generation, InsightFlow automatically creates:
        - **SWOT Bar Chart** — Factor counts across all 4 quadrants
        - **SWOT Radar** — Spider chart showing balance/imbalance
        - **Strategy Priorities** — Ranked strategic initiatives
        - **Opportunity Score** — Risk vs opportunity gauge

        ### Use Cases
        - **Market Research** — Quickly understand a new company or market
        - **Competitive Intelligence** — Analyze competitors' strengths & weaknesses
        - **Due Diligence** — Pre-investment or partnership research
        - **Strategic Planning** — Data-driven strategy recommendations
        """)