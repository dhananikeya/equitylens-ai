# EquityLens AI

**EquityLens AI** is a public-markets research platform that transforms SEC filings and structured financial data into standardized company research.

The project is designed to make it easier to compare companies across an industry, understand how financial performance is changing over time, review capital structure and risk factors, and trace key figures back to original SEC filings.

> **EquityLens informs. You decide.**

## Live Demo

[Launch EquityLens AI](https://equitylens-ai-2h7rd8qluv3bc8sdqf5cu3.streamlit.app/)

## Why I Built It

Public-company research often requires jumping between SEC filings, earnings reports, spreadsheets, and financial websites before two companies can be compared consistently.

I built EquityLens AI to explore how that workflow could be made more structured.

The platform standardizes company-reported information into a common research framework so users can examine financial performance, business models, capital structure, and disclosed risks without generating buy/sell recommendations or ranking companies as investments.

## What the Platform Does

### Peer Comparison

Users can select an industry, narrow the peer set by subgroup, and compare companies across:

- Annual revenue and revenue growth
- Gross, operating, and net margins
- Quarterly performance
- Trailing-twelve-month (LTM) results
- Cash, investments, debt, and share counts
- Multi-year revenue trends
- Business models and revenue sources
- Platform dependencies
- Competitive and operational risks
- Direct SEC filing sources

### Company Research

Each company has a dedicated research view that includes:

- Company and business-model overview
- Latest-quarter and LTM financial metrics
- "What Changed This Quarter?" factual change analysis
- Historical revenue and operating-margin trends
- Capital-structure snapshot
- 10-K vs. latest 10-Q filing snapshot
- Recent filing timeline
- Key risk themes
- Grounded research questions answered from structured filing data

## Current Coverage

EquityLens currently covers **15 public companies across 2 industries**.

### Cloud & Data Infrastructure Software

- Rubrik (RBRK)
- Snowflake (SNOW)
- MongoDB (MDB)
- Datadog (DDOG)
- Cloudflare (NET)
- Elastic (ESTC)
- Dynatrace (DT)
- Akamai (AKAM)

Current peer subgroups include Data Platforms, Cloud / Network Infrastructure, and Cybersecurity-related infrastructure.

### Cybersecurity

- Palo Alto Networks (PANW)
- Zscaler (ZS)
- CrowdStrike (CRWD)
- Okta (OKTA)
- Fortinet (FTNT)
- SentinelOne (S)
- Tenable (TENB)

Current peer subgroups include Endpoint / XDR, Identity Security, Network Security, and Exposure Management.

## Research Methodology

EquityLens uses publicly available company disclosures and SEC filings as the primary research foundation.

The current workflow standardizes selected reported figures into structured datasets, then calculates comparable metrics such as:

- Year-over-year revenue growth
- Quarter-over-quarter revenue growth
- Gross margin
- Operating margin
- Net margin
- Trailing-twelve-month revenue and profitability
- Sequential operating-margin changes

Qualitative research is also structured into consistent fields such as:

- Business model
- Primary revenue source
- Customer type
- Platform dependencies
- Competitive risks
- Operational risks
- Key disclosed risk themes

Source links are displayed throughout the application so users can review the original filings.

## Architecture

```text
SEC EDGAR / Company Filings
           |
           v
 Structured JSON Datasets
           |
           v
 Financial Calculation Layer
           |
           +----------------------+
           |                      |
           v                      v
   Peer Comparison        Company Research
           |                      |
           +----------+-----------+
                      |
                      v
               Streamlit UI
```

The current public version intentionally keeps the data layer simple and transparent. A future version can move ingestion and storage into a database-backed pipeline without redesigning the research interface.

## Tech Stack

- **Python** for application logic and calculations
- **Streamlit** for the interactive research interface
- **Pandas** for tabular data transformation
- **SEC EDGAR** for public-company filings
- **Requests** for API integrations
- **GitHub** for source control and project development
- **JSON** for the current structured research datasets
- Optional private market-data API integration for development environments

## Design Principles

### Neutral Research

EquityLens does not identify a "best" stock, generate buy/sell recommendations, or rank companies as investments.

Instead, it presents factual comparisons such as revenue growth, profitability, capital structure, and disclosed risk factors so users can form their own conclusions.

### Source Transparency

Material financial data is tied back to SEC filings whenever possible.

EquityLens distinguishes between **reported figures**, **metrics calculated by the application**, and **educational explanations**. Primary sources are preferred in this order: SEC filings first, then company investor-relations disclosures, followed by appropriately licensed market-data sources where needed.

### Beginner-Friendly Financial Education

The interface is designed so users do not need prior market expertise to understand the research. Financial terms such as revenue growth, gross margin, operating margin, net income, LTM, 10-K, and 10-Q are explained in plain language without converting those explanations into investment recommendations.

### Comparable Research

Companies are analyzed using a consistent structure so differences in growth, profitability, business model, and risk are easier to examine.

### Expandable Coverage

The application is designed so new companies, subgroups, and industries can be added without rebuilding the interface.

## Project Roadmap

Planned areas of exploration include:

- Automated SEC filing ingestion
- Database-backed financial history
- Additional industries and peer groups
- Filing-to-filing change detection
- Earnings change analysis
- Standardized valuation multiples
- Peer medians and ranges
- User-controlled valuation scenarios
- Grounded AI research over structured data and filing excerpts
- Additional source validation and data-quality controls

These are roadmap items, not promises about investment outcomes or future product functionality.

## Repository Structure

```text
equitylens-ai/
├── app.py
├── requirements.txt
└── data/
    ├── company_metrics.json
    ├── company_quarterly.json
    └── company_analysis.json
```

## What I Learned

Building EquityLens has required combining financial research with software design.

The project has involved:

- Interpreting SEC financial statements
- Standardizing financial data across companies with different fiscal calendars
- Calculating quarterly, annual, and LTM metrics
- Designing peer groups and research taxonomies
- Structuring qualitative filing analysis
- Building an interactive Streamlit application
- Managing data-quality and source-linking considerations
- Thinking through how AI can support research without replacing user judgment

## Data Use and Disclaimer

EquityLens AI is an independent educational and research project. It is not affiliated with, sponsored by, or endorsed by any similarly named company, product, service, financial institution, broker, exchange, or data provider.

The platform does not provide personalized investment advice, investment recommendations, rankings, or guarantees of future performance.

The public demo is built primarily around publicly available SEC filings and company-reported disclosures. Market-data integrations may be used in private development environments only when permitted by the relevant provider's licensing terms and exchange entitlements.

Financial information may be delayed, incomplete, or affected by later filings or restatements. Users should verify material information against original SEC filings and company disclosures before making financial decisions.

---

Built as a personal project exploring financial research, data standardization, and applied AI workflows.
