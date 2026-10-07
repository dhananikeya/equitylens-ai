# EquityLens AI

> **Understand companies. Not documents.**

EquityLens AI is a public-company research platform that turns SEC filings and structured financial data into clearer company research. It combines filing-linked financial analysis, quarterly and trailing-twelve-month metrics, business-model context, disclosed risk themes, peer comparisons, and an interactive research assistant in one Streamlit application.

The project is designed around a simple principle: **important research claims should stay connected to the underlying source.**

## What EquityLens Does

- **Explore public companies** through company snapshots, quarterly performance, capital structure, historical trends, and qualitative research.
- **Compare peers** using standardized revenue, growth, margin, balance-sheet, and LTM views.
- **Track SEC filings** across covered companies with direct links to the original EDGAR documents.
- **Monitor macro conditions** using official BLS inflation and labor-market data, U.S. Treasury yields, SOFR reference rates, and Federal Reserve calendars.
- **Follow market news** through Bloomberg headline metadata and outbound links without republishing article content.
- **Review IPO history** through S-1 filing context where available.
- **Learn the fundamentals** with plain-language explanations of financial metrics, SEC forms, macroeconomic reports, Treasury yields, SOFR, and interest-rate swaps.

## Public Experience

The application is organized into seven primary areas:

1. **Home** — product overview and guided paths into company research.
2. **Explore Companies** — a deeper company research view with filing-linked analysis.
3. **Industry Comparison** — side-by-side peer research and financial comparison.
4. **EquityLens** — a structured company brief covering performance, business model, risks, and source links.
5. **Market Monitor** — NYSE market tape and heat map, Treasury yield curve, SOFR reference rates, macroeconomic indicators, economic/FOMC calendars, Bloomberg headline links, and company-level market context.
6. **Filings** — a monitored SEC filing feed and registration-filing history.
7. **Learn** — explanations of financial metrics, S-1 and 8-K filings, BLS reports, Treasury yields, SOFR, and interest-rate swaps.

## Research Methodology

EquityLens separates information into clear categories:

- **Reported** — taken from a company filing or company-reported disclosure.
- **Calculated by EquityLens** — derived from reported figures, including growth rates, margins, and LTM metrics.
- **Research summary** — plain-language context based on structured company information and filing disclosures.
- **Source** — the underlying SEC filing or company disclosure used for verification.

### Source Priority

1. SEC EDGAR filings, including Forms 10-K, 10-Q, 8-K, and S-1.
2. U.S. Bureau of Labor Statistics for inflation, employment, wage, and release-calendar data.
3. U.S. Department of the Treasury for the official daily Treasury par yield curve.
4. Federal Reserve and Federal Reserve Bank of New York for FOMC information, monetary-policy releases, SOFR, and SOFR averages.
5. Company investor-relations materials and company-reported disclosures.
6. Appropriately licensed or permitted market-data and news providers where needed.

EquityLens does not fabricate unavailable market data. In particular, live OTC swap quotes are shown only when an authorized data endpoint is configured.

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

## Macro & Rates Monitor

The Market Monitor adds a macro layer around company research:

- **Treasury rate tape** with 2Y, 5Y, 10Y, and 30Y yields
- **2s10s yield-curve spread**
- **SOFR** plus published 30-day, 90-day, and 180-day SOFR averages
- **Treasury yield-curve visualization**
- **BLS macro snapshot** covering CPI, Core CPI, PPI Final Demand, unemployment, payrolls, average hourly earnings, and ECI
- **Economic calendar** sourced from the official BLS release calendar
- **FOMC meeting calendar** and Federal Reserve monetary-policy updates
- **Bloomberg market-news gateway** using headline metadata and outbound links only
- **Optional USD SOFR swap curve** when a licensed JSON endpoint is configured

### Optional Swap-Rate Feed

Live OTC swap quotes are not inferred from Treasury yields or SOFR. To display authorized swap-rate data, add the following Streamlit secret:

```toml
SWAP_RATES_JSON_URL = "https://your-authorized-provider.example/swap-rates"
```

Accepted JSON shapes include:

```json
{"1Y": 4.10, "2Y": 4.02, "5Y": 3.95, "10Y": 4.08}
```

or:

```json
[
  {"tenor": "1Y", "rate": 4.10},
  {"tenor": "2Y", "rate": 4.02}
]
```

Provider licensing, redistribution rights, and timing remain the responsibility of the configured data source.

## Learning & Filing Reference

The Learn tab now includes primary-source-linked explanations for:

- Form S-1 and S-1/A
- Form 8-K
- CPI and Core CPI
- PPI
- Employment Situation
- JOLTS
- Employment Cost Index
- 10-Year Treasury yield
- SOFR
- Interest-rate swaps

Each entry explains what the item means, why it matters, how to interpret it, what to watch for, and where to verify the definition or data at the primary source.

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
- U.S. Bureau of Labor Statistics Public Data API
- U.S. Treasury daily yield-curve feed
- Federal Reserve / New York Fed reference-rate and calendar sources
- Bloomberg headline metadata and outbound market-news links
- Finviz Elite
- Yahoo Finance via yfinance
- Structured JSON datasets
- Requests
- Optional licensed swap-rate JSON integration

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
