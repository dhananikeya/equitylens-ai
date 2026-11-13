#!/usr/bin/env bash
set -euo pipefail

# Run one local-LLM research batch, then rebuild the deterministic coverage index.
#
# Examples:
#   bash scripts/run_local_research.sh
#   RESEARCH_BATCH_SIZE=20 bash scripts/run_local_research.sh
#   LOCAL_LLM_PROVIDER=ollama LOCAL_LLM_MODEL=llama3.1:8b bash scripts/run_local_research.sh
#   LOCAL_LLM_PROVIDER=openai_compatible LOCAL_LLM_URL=http://127.0.0.1:1234/v1 bash scripts/run_local_research.sh

export LOCAL_LLM_PROVIDER="${LOCAL_LLM_PROVIDER:-ollama}"
export RESEARCH_BATCH_SIZE="${RESEARCH_BATCH_SIZE:-20}"
export RESEARCH_MAX_ATTEMPTS="${RESEARCH_MAX_ATTEMPTS:-3}"
export SEC_REQUEST_DELAY_SECONDS="${SEC_REQUEST_DELAY_SECONDS:-0.12}"

echo "EquityLens local research worker"
echo "Provider: ${LOCAL_LLM_PROVIDER}"
echo "Batch size: ${RESEARCH_BATCH_SIZE}"

python scripts/local_research_status.py
python scripts/build_deep_research.py
python scripts/build_research_coverage.py

echo
echo "Batch complete."
python scripts/local_research_status.py
echo
echo "Review the generated JSON changes before committing them."
