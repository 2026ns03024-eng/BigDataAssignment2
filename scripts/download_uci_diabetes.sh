#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data
CSV="data/diabetic_data.csv"
# UCI repository id=296 (replaces legacy /00296/ zip path)
URL="https://archive.ics.uci.edu/static/public/296/data.csv"

if [[ -f "$CSV" ]]; then
  echo "Already present: $CSV"
  exit 0
fi

curl -fL -o "$CSV" "$URL"
echo "Ready: $CSV ($(wc -l < "$CSV") lines)"
