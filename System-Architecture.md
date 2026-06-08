# System Architecture

## Overview

InsightFlow is an AI-powered business intelligence system that transforms a company name or business topic into a structured business report using a multi-agent architecture.

## Workflow

```mermaid
flowchart TD
    A[User Input<br/>Company / Industry / Topic]

    B[Orchestrator Agent<br/>Task Coordination]

    C[Research Agent<br/>Data Collection<br/>Source Retrieval]

    D[Analysis Agent<br/>Market Analysis<br/>Trend Detection<br/>SWOT Analysis]

    E[Strategy Agent<br/>Opportunities<br/>Risk Assessment<br/>Recommendations]

    F[Report Agent<br/>Report Formatting<br/>Executive Summary]

    G[Professional Business Report<br/>Markdown / PDF]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
```

## Agent Responsibilities

### Orchestrator Agent
Coordinates workflow execution and manages communication between agents.

### Research Agent
Collects company, market, and industry information from available sources.

### Analysis Agent
Processes research data and extracts trends, insights, and business intelligence.

### Strategy Agent
Generates recommendations, identifies opportunities, and evaluates risks.

### Report Agent
Formats all findings into a professional business report.
