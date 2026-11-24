# EquityLens Foundry integration (development)
 
This branch provides a read-only REST adapter, not a deployed Foundry instance. The existing Streamlit app remains unchanged.
 
## Proposed ontology
- Company: CIK (string primary key), ticker, name, industryId
- Industry: industryId (primary key), name
- SecFiling: accessionNumber (primary key), cik, form, filedDate, sourceUrl
- FinancialMetric: metricId (primary key), cik, metricName, periodStart, periodEnd, unit, value, accessionNumber
- Links: Company to Industry; Company to SecFiling; Company to FinancialMetric; FinancialMetric to source filing.
Preserve source accession, units and reporting periods; never overwrite restatements without provenance.
 
## Activation
1. Obtain Foundry developer enrollment and create project datasets from SEC data.
2. Configure object types and links in Ontology Manager. Names above are proposals; use actual API names.
3. Configure authorized OAuth access with api:ontologies-read. For local testing only, provide a valid short-lived token via environment variables FOUNDRY_URL, FOUNDRY_ONTOLOGY, FOUNDRY_TOKEN. Never commit credentials.
4. Run a local smoke test: python -c 'from foundry_client import FoundryClient; print(len(list(FoundryClient.from_env().list_objects("Company"))))'
5. Compare results to existing SEC research before wiring the app. For public deployment implement server-side OAuth token renewal, scoped access and caching.
 
Reference: https://www.palantir.com/docs/foundry/api/v2/ontologies-v2-resources/ontology-objects/list-objects
Community example: https://github.com/palantir/aip-community-registry
 
No live enrollment or generated OSDK has been configured. AIP workflows and data upload are future steps.
