```text
██╗███╗   ██╗███████╗██╗ ██████╗ ██╗  ██╗████████╗███████╗██╗      ██████╗ ██╗    ██╗
██║████╗  ██║██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝██╔════╝██║     ██╔═══██╗██║    ██║
██║██╔██╗ ██║███████╗██║██║  ███╗███████║   ██║   █████╗  ██║     ██║   ██║██║ █╗ ██║
██║██║╚██╗██║╚════██║██║██║   ██║██╔══██║   ██║   ██╔══╝  ██║     ██║   ██║██║███╗██║
██║██║ ╚████║███████║██║╚██████╔╝██║  ██║   ██║   ██║     ███████╗╚██████╔╝╚███╔███╔╝
╚═╝╚═╝  ╚═══╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝
```

<p align="center">
  <img src="https://img.shields.io/badge/AI-Multi--Agent%20System-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/CrewAI-Orchestration-purple?style=for-the-badge">
  <img src="https://img.shields.io/badge/Groq-LLM-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Gemini-Fallback-4285F4?style=for-the-badge">
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
  <img src="https://img.shields.io/badge/Plotly-Visualization-3F4F75?style=for-the-badge&logo=plotly&logoColor=white">
  <img src="https://img.shields.io/badge/Serper-Web%20Search-green?style=for-the-badge">
</p>

<p align="center">
  <strong>AI-Powered Multi-Agent Business Intelligence System</strong>
</p>

<p align="center">
  Automating research, analysis, and strategic decision-making using specialized AI agents.
</p>

---

## Architecture
- **Research Agent**: Web scraping and data collection
- **Analysis Agent**: SWOT analysis and trend identification  
- **Strategy Agent**: Strategic recommendations and roadmap
- **Report Agent**: Professional report generation

The system uses a robust LLM fallback architecture, intelligently switching between `OpenGateway`, `Groq`, and `Gemini` automatically to ensure maximum uptime, even during rate limits or service timeouts.

## Business Impact
- Reduces research time from 8 hours → 15 minutes (97% reduction)
- Provides structured, consistent analysis framework
- Enables analysts to focus on high-value decision-making
- Scalable across industries and company sizes

## Tech Stack
- **CrewAI**: Multi-agent orchestration
- **LLMs**: Groq (primary) and Google Gemini (fallback) natively integrated
- **Streamlit**: Modern, adaptive UI
- **Plotly**: Dynamic, auto-generated interactive visualizations
- **SerperDev**: Real-time web search capabilities

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/InsightFlow.git
   cd InsightFlow
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   # Required for Web Search
   SERPER_API_KEY=your_serper_key_here

   # LLM Providers (Provide at least one)
   GROQ_API_KEY=your_groq_key_here
   GEMINI_API_KEY=your_gemini_key_here
   OPENGATEWAY_API_KEY=your_opengateway_key_here
   OPENGATEWAY_BASE_URL=https://opengateway.gitlawb.com/v1
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   Navigate to `http://localhost:8501` to view the dashboard!

## Future Enhancements
- Financial data integration (Yahoo Finance API)
- PDF export with charts/graphs
- Multi-company comparison mode
- Custom analysis frameworks beyond SWOT
