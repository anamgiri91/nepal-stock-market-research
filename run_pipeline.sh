#!/usr/bin/env bash
# Run the full pipeline from a clean state, using the project virtualenv.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PY="./.venv/bin/python"
[ -x "$PY" ] || { echo "No .venv found. Run:  python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt"; exit 1; }
for s in scripts/[0-9]*.py; do
  echo "── $s"
  "$PY" "$s"
done
echo "── tests"; "$PY" -m pytest tests -q
echo "Pipeline complete. Exhibits in output/."
