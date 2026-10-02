# EquityLens AI

> **Understand companies. Not documents.**

EquityLens AI is a public-company research platform that turns SEC filings and structured financial data into clearer company research. It combines filing-linked financial analysis, quarterly and trailing-twelve-month metrics, business-model context, disclosed risk themes, peer comparisons, and an interactive research assistant in one Streamlit application.

The project is designed around a simple principle: **important research claims should stay connected to the underlying source.**

## What EquityLens Does

- **Explore public companies** through company snapshots, quarterly performance, capital structure, historical trends, and qualitative research.
- **Compare peers** using standardized revenue, growth, margin, balance-sheet, and LTM views.
- **Track SEC filings** across covered companies with direct links to the original EDGAR documents.
- **Ask EquityLens** plain-language questions about revenue growth, profitability, cash, debt, business models, and disclosed risks.
- **Review IPO history** through S-1 filing context where available.
- **Learn the fundamentals** with plain-language explanations of common public-company metrics.

## Public Experience

The application is organized into six primary areas:

1. **Home** — company search, current snapshot, featured coverage, and product overview.
2. **Explore Companies** — a deeper company research view with filing-linked analysis.
3. **Compare** — side-by-side peer research and financial comparison.
4. **Ask EquityLens** — a grounded research interface using the structured EquityLens dataset.
5. **Filings** — a monitored SEC filing feed.
6. **Learn** — explanations of financial metrics and public-company filings.

## Research Methodology

EquityLens separates information into clear categories:

- **Reported** — taken from a company filing or company-reported disclosure.
- **Calculated by EquityLens** — derived from reported figures, including growth rates, margins, and LTM metrics.
- **Research summary** — plain-language context based on structured company information and filing disclosures.
- **Source** — the underlying SEC filing or company disclosure used for verification.

### Source Priority

1. SEC EDGAR filings, including Forms 10-K, 10-Q, 8-K, and S-1.
2. Company investor-relations materials and company-reported disclosures.
3. Appropriately licensed market-data providers where needed.

## SEC Monitoring

EquityLens includes an automated SEC filing monitor. A GitHub Actions workflow refreshes filing data and updates the structured filing feed used by the application.

The tracker captures information such as:

- Company and ticker
- Filing type
- SEC filing date
- SEC acceptance timestamp when available
- Reporting period
- Accession number
- Direct SEC filing link
- First detection timestamp inside EquityLens

## Current Coverage

The current research universe focuses on cloud infrastructure, data platforms, and cybersecurity companies, including companies such as:

- MongoDB
- Snowflake
- Datadog
- Cloudflare
- Rubrik
- Elastic
- Dynatrace
- Akamai
- Palo Alto Networks
- Zscaler
- CrowdStrike
- Okta
- Fortinet
- SentinelOne
- Tenable

Coverage is intentionally focused while the research and ingestion workflows are expanded.

## Technology

**Application**
- Python
- Streamlit
- Pandas

**Data & APIs**
- SEC EDGAR
- Structured JSON datasets
- Requests
- Optional market-data API integration

**Infrastructure**
- GitHub
- GitHub Actions
- Streamlit Community Cloud
- Supabase for optional account functionality

## Project Structure

```text
equitylens-ai/
├── app.py
├── sec_data.py
├── data/
│   ├── company_metrics.json
│   ├── company_quarterly.json
│   ├── company_analysis.json
│   ├── company_s1.json
│   └── sec_filings.json
├── scripts/
├── .github/
│   └── workflows/
│       └── refresh-sec-filings.yml
├── requirements.txt
└── COPYRIGHT.md
```

## Run Locally

Clone the repository:

```bash
git clone https://github.com/dhananikeya/equitylens-ai.git
cd equitylens-ai
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

Some optional functionality requires Streamlit secrets for external services such as Supabase or a supported market-data provider. Filing-based public research remains the core of the application.

## Design Principles

EquityLens is being built around five product principles:

- **Primary sources first**
- **Transparent calculations**
- **Clear separation of fact and interpretation**
- **Useful comparisons without unnecessary complexity**
- **Research support rather than investment instructions**

## Disclaimer

EquityLens AI is an educational and research project. It analyzes publicly available financial information and does not provide personalized investment advice, investment recommendations, rankings, or guarantees of future performance.

Financial information may be delayed, incomplete, or affected by later filings and restatements. Material information should be verified against the original SEC filing or company disclosure.

## Creator

**Keya Dhanani**

B.S. Information Systems, Virginia Commonwealth University  
Independent project focused on public-company research, financial data, automation, and AI-assisted analysis.

---

© 2026 Keya Dhanani. All rights reserved. See [COPYRIGHT.md](COPYRIGHT.md) for project-specific copyright information.
