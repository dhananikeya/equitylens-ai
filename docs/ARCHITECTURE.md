# EquityLens AI Architecture

## Runtime flow

EquityLens separates ingestion, provider I/O, cached runtime data, and presentation.

1. **Ingestion / refresh**
   - `scripts/update_sec_filings.py` retrieves SEC submissions on a schedule.
   - It writes lightweight `data/sec_summary.json`, per-company shards under `data/sec_companies/`, and a compressed historical archive.
   - Generated research datasets are written separately from hand-curated records.

2. **Provider services**
   - `services/http.py` owns outbound HTTP behavior and normalized provider errors.
   - `services/providers/` contains provider-specific clients for Treasury, New York Fed, BLS, Federal Reserve, Bloomberg, and swap-curve data.
   - `market_data.py`, `sec_data.py`, and `macro_data.py` transform provider responses into application data.

3. **Runtime data layer**
   - `app_runtime.py` loads repository-backed datasets and handles lazy SEC/research loading.
   - Startup loads only the lightweight company metrics, research coverage index, SEC summary, and company universe.
   - Narrative, quarterly, S-1, ownership, analyst, ETF, and price-history data are lazy-loaded.

4. **Models and configuration**
   - `models/` contains reusable typed contexts and schemas.
   - `config.py` owns app settings, performance budgets, cache TTL metadata, and provider metadata.
   - `sources.py` owns provider labels and source-authority labels.
   - `formatting.py` owns shared display formatting.

5. **Presentation**
   - `views/` contains top-level Streamlit views.
   - `views/company_sections/` contains Company Research sub-sections.
   - `views/market_sections/` contains Market Monitor sub-sections/components.
   - `ui_components.py` contains reusable Streamlit UI primitives.
   - `charts.py` contains reusable Plotly constructors/layout helpers.
   - `assets/equitylens.css` contains global styles.

## Data authority

- SEC EDGAR and official government/company disclosures are primary sources.
- Yahoo Finance, Finviz, Bloomberg headline links, and other market providers are supplemental context.
- Missing data is displayed as unavailable rather than inferred.
- Calculated values should be labeled separately from reported values.

## Performance rules

- Home warm-render target: under 2 seconds.
- Company Research warm-render target: under 3 seconds.
- Navigation/full rerun target: under 1 second.
- Full SEC archive is never part of startup.
- External calls require caching and explicit timeouts.
- Expensive section data loads only when the user opens that section or explicitly refreshes it.

## Dependency direction

`views -> domain/data modules -> services -> external providers`

Ingestion scripts write repository datasets but do not import UI modules. Views should not call raw HTTP providers directly.

## Validation

The main GitHub Action compiles the Python application and runs the primary test suite. Changes to data architecture should preserve:
- the six top-level application areas,
- source-link behavior,
- Streamlit startup,
- lazy-loading boundaries,
- existing data fallbacks.
