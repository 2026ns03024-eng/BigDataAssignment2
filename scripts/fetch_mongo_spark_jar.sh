#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p jars
MODE="${1:-spark3}"

if [[ "$MODE" == "spark24" ]]; then
  JAR="mongo-spark-connector_2.11-2.4.4.jar"
  URL="https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.11/2.4.4/${JAR}"
else
  JAR="mongo-spark-connector_2.12-10.2.0.jar"
  URL="https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.2.0/${JAR}"
fi

DEST="jars/$JAR"
if [[ -f "$DEST" ]]; then
  echo "Already present: $DEST"
  exit 0
fi

curl -fL -o "$DEST" "$URL"
echo "Downloaded $DEST"
ls -la "$DEST"
