# EquityLens Deployment Boundaries

## Current architecture

**Research application:** Python/Streamlit repository (`app.py`, `views/`, `sec_data.py`, market data modules, and GitHub Actions). Run this application with Streamlit, not a Next.js Vercel build.

**Vercel project:** `equitylens-ai-web` is presently configured as Next.js and pointed at the Python repository. Its preview build fails with `missing_pages_app` because the expected Next.js root (`app/` or `pages/`) is not in this repository.

This is a deployment wiring issue; it does not demonstrate a failure of the Streamlit research application.

## Recommended separation

1. Preserve the Streamlit app, current data pipeline, and any functioning production endpoint.
2. Disconnect the Python repository from the Next.js Vercel project in the Vercel dashboard's Project Settings > Git **after confirming the production domain and its actual deployment source**.
3. Keep `equitylens-ai-web` as a separate optional web project if a Next.js/TypeScript site is needed. Connect it to a dedicated frontend repository, or to a proper frontend subdirectory with valid Next.js files and its own tested build.
4. Keep the research UI prototype under `frontend/` in this repository as a Streamlit Components v2 enhancement. It is not a standalone Vercel application.
5. Maintain separate deployment checks for Streamlit and the future Vercel frontend. Do not treat Vercel's Next.js failure as a failure of Python UI integration.

## Safe validation

- Confirm which public domain currently serves the real EquityLens app before changing domains or Git connections.
- Run the Streamlit app on a compatible pinned Streamlit version and test the JavaScript card component.
- Verify native fallback navigation, filings, watchlist, market data and comparison features.
- Require a passing frontend build before connecting a future Next.js repository to Vercel.
- Merge the UI draft only after runtime and responsive testing.

## Do not do

- Do not switch the existing Python repository's Vercel framework and assume that makes Streamlit runnable there.
- Do not move SEC ingestion or credentials into the browser.
- Do not delete or reassign production domains during the separation.
- Do not merge a draft solely to satisfy the Vercel build check.

## Current tracked state

- Streamlit UI draft: PR #8, `design/equitylens-dark-ui-refresh`.
- Vercel project: `equitylens-ai-web`, project ID `prj_Yn4sGWFrmYnDGm4MHwfW0TAupRfs`.
- Failed deployment: `dpl_HzbuiyLezqizdoQg4JXMBtzTMDaj` (`missing_pages_app`).
- No Vercel project settings changed as part of this separation plan.
