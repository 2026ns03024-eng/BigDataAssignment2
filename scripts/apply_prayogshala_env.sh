#!/usr/bin/env bash
# Merge cluster/prayogshala.env into config.env (Prayogshala IP-based layout).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SRC="${1:-$ROOT/cluster/prayogshala.env}"
if [[ ! -f "$SRC" ]]; then
  echo "Copy cluster/prayogshala.env.example to cluster/prayogshala.env and edit IPs."
  exit 1
fi

cp -n config.example.env config.env 2>/dev/null || true

while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%%#*}"
  line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  [[ -z "$line" || "$line" != *=* ]] && continue
  key="${line%%=*}"
  val="${line#*=}"
  if grep -q "^${key}=" config.env 2>/dev/null; then
    sed -i.bak "s|^${key}=.*|${key}=${val}|" config.env
  else
    echo "${key}=${val}" >> config.env
  fi
done < "$SRC"
rm -f config.env.bak

# Map cluster file to config keys
if grep -q '^SPARK_MASTER_URL=' "$SRC"; then
  url="$(grep '^SPARK_MASTER_URL=' "$SRC" | cut -d= -f2-)"
  sed -i.bak "s|^SPARK_MASTER=.*|SPARK_MASTER=${url}|" config.env
  rm -f config.env.bak
fi

echo "Updated config.env from $SRC"
grep -E '^(MONGO_|SPARK_|DATA_)' config.env || true
