from crewai import Agent, LLM
from tools import search_tool
from dotenv import load_dotenv
import os
import sys
import time

load_dotenv()

# Set UTF-8 output for Windows console (avoids emoji encoding crashes)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── Fix: CrewAI injects 'cache_breakpoint' into messages which Groq rejects ──
# Monkey-patch the cache marker to be a no-op so the flag is never added.
import litellm
litellm.drop_params = True
litellm.num_retries = 3                # Auto-retry on transient errors (429, 500, 503)
litellm.request_timeout = 300          # 5 minutes — generous to avoid premature timeout
litellm.retry = True
litellm.retry_after = 30               # Wait 30s between retries

import crewai.llms.cache as _cache
_cache.mark_cache_breakpoint = lambda msg: msg  # no-op

# ── LLM Configuration ────────────────────────────────────────────────────────
# Priority chain:
#   1. OpenGateway (mimo-v2.5-pro) — primary
#   2. Groq (llama-3.3-70b-versatile) — fast fallback
#   3. Gemini (gemini-2.0-flash) — reliable fallback (generous rate limits)

def _create_primary_llm():
    """Create the OpenGateway LLM (primary)."""
    api_key = os.getenv("OPENGATEWAY_API_KEY")
    base_url = os.getenv("OPENGATEWAY_BASE_URL", "https://opengateway.gitlawb.com/v1")
    if not api_key:
        return None
    return LLM(
        model="openai/mimo-v2.5-pro",
        api_key=api_key,
        base_url=base_url,
        timeout=300,
        max_tokens=4096,
    )

def _create_groq_llm():
    """Create the Groq LLM (fast fallback)."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=api_key,
        timeout=300,
        max_tokens=4096,
    )

def _create_gemini_llm():
    """Create the Gemini LLM (reliable fallback — generous rate limits)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return LLM(
        model="gemini/gemini-2.0-flash",
        api_key=api_key,
        timeout=300,
        max_tokens=4096,
    )

# ── Select best available LLM with fallback chain ────────────────────────────
primary = _create_primary_llm()
groq_llm = _create_groq_llm()
gemini_llm = _create_gemini_llm()

# Build ordered list of (llm_instance, provider_name, model_name)
_candidates = []
if primary:
    _candidates.append((primary, "OpenGateway", "mimo-v2.5-pro"))
if groq_llm:
    _candidates.append((groq_llm, "Groq", "llama-3.3-70b-versatile"))
if gemini_llm:
    _candidates.append((gemini_llm, "Gemini", "gemini-2.0-flash"))

if not _candidates:
    raise RuntimeError(
        "No LLM available. Set at least one of OPENGATEWAY_API_KEY, "
        "GROQ_API_KEY, or GEMINI_API_KEY in .env"
    )

_all_available = _candidates
llm, LLM_PROVIDER, LLM_MODEL = _candidates[0]
print(f"[LLM] 🟢 Using {LLM_PROVIDER} as primary provider")
for _inst, _prov, _model in _candidates[1:]:
    print(f"[LLM] 🔵 {_prov} available as fallback")

def get_fallback_llm():
    """Return a fallback LLM if the primary fails at runtime.
    Returns None if no fallback is available."""
    for _inst, _prov, _model in _all_available:
        if _inst is not llm:
            return _inst, _prov, _model
    return None, None, None


# ── Research Agent ────────────────────────────────────────────────────────────
# max_iter=2: one search call + one final answer = ~3-4 LLM calls
research_agent = Agent(
    role='Senior Business Research Analyst',
    goal=(
        'Research {company} thoroughly: business model, products/services, '
        'market position, competitors, recent news, and financials'
    ),
    backstory=(
        'You are a top-tier business researcher at a leading consulting firm '
        'with 10+ years of experience in market intelligence. You specialize in '
        'gathering accurate, comprehensive company data and cross-referencing '
        'multiple sources. You always structure findings clearly with citations.'
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[search_tool],
    max_iter=2,
    max_execution_time=600,  # 10 minutes max per agent
)

# ── Analysis Agent ────────────────────────────────────────────────────────────
# max_iter=1: no tools, single-shot answer = ~1-2 LLM calls
analysis_agent = Agent(
    role='Business Intelligence Analyst',
    goal=(
        'Perform deep analysis on {company} data: SWOT analysis, competitive '
        'positioning, trend identification, risk assessment, and growth opportunities'
    ),
    backstory=(
        'You are a senior data analyst at McKinsey with expertise in business '
        'intelligence. You transform raw research data into actionable insights '
        'using proven frameworks like SWOT, Porter\'s Five Forces, and PESTEL. '
        'Your analyses are data-driven, structured, and decision-ready.'
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
    max_iter=1,
    max_execution_time=300,  # 5 minutes max
)

# ── Strategy Agent ────────────────────────────────────────────────────────────
# max_iter=1: no tools, single-shot answer = ~1-2 LLM calls
strategy_agent = Agent(
    role='Chief Strategy Consultant',
    goal=(
        'Develop 3-5 prioritized strategic recommendations for {company} '
        'with implementation roadmaps, KPIs, and risk mitigation plans'
    ),
    backstory=(
        'You are a partner at a top-tier strategy consulting firm. You have '
        'led 50+ engagements in corporate strategy, digital transformation, and '
        'growth advisory. You deliver specific, measurable, actionable '
        'recommendations with clear timelines and resource requirements.'
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
    max_iter=1,
    max_execution_time=300,  # 5 minutes max
)

# ── Report Agent ──────────────────────────────────────────────────────────────
# max_iter=1: no tools, single-shot answer = ~1-2 LLM calls
report_agent = Agent(
    role='Executive Report Writer',
    goal='Compile all findings into a professional, executive-level business intelligence report',
    backstory=(
        'You are an expert business writer who produces Fortune 500-grade reports. '
        'You excel at synthesizing complex analyses into clear, compelling narratives '
        'with proper structure, data tables, and actionable takeaways. '
        'Your reports are concise yet comprehensive, never exceeding 2000 words.'
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
    max_iter=1,
    max_execution_time=300,  # 5 minutes max
)