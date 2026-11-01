#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p jars

# shellcheck disable=SC1091
source "$ROOT/scripts/source_cluster_env.sh" 2>/dev/null || true

MODE="${1:-auto}"
if [[ "$MODE" == "auto" ]] && command -v spark-submit >/dev/null 2>&1; then
  VER=$(spark-submit --version 2>&1 | grep -oE 'version [0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 | awk '{print $2}' || echo "3")
  MAJOR=$(echo "$VER" | cut -d. -f1)
  if [[ "$MAJOR" -ge 4 ]]; then
    MODE="spark4"
  elif [[ "$MAJOR" == "2" ]]; then
    MODE="spark24"
  else
    MODE="spark3"
  fi
  echo "Detected Spark $VER -> fetch mode $MODE"
fi

if [[ "$MODE" == "spark24" ]]; then
  JAR="mongo-spark-connector_2.11-2.4.4.jar"
  URL="https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.11/2.4.4/${JAR}"
  EXTRA_ARTIFACTS=("mongo-java-driver:3.12.5")
elif [[ "$MODE" == "spark4" ]]; then
  JAR="mongo-spark-connector_2.13-11.1.0.jar"
  URL="https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.13/11.1.0/${JAR}"
  EXTRA_ARTIFACTS=("mongodb-driver-sync:5.1.4" "mongodb-driver-core:5.1.4" "bson:5.1.4" "bson-record-codec:5.1.4")
else
  JAR="mongo-spark-connector_2.12-10.2.0.jar"
  URL="https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.2.0/${JAR}"
  EXTRA_ARTIFACTS=("mongodb-driver-sync:4.8.2" "mongodb-driver-core:4.8.2" "bson:4.8.2" "bson-record-codec:4.8.2")
fi

DEST="jars/$JAR"
if [[ -f "$DEST" ]]; then
  echo "Already present: $DEST"
else
  curl -fL -o "$DEST" "$URL"
  echo "Downloaded $DEST"
fi

for dependency in "${EXTRA_ARTIFACTS[@]}"; do
  artifact="${dependency%%:*}"
  version="${dependency#*:}"
  dependency_jar="jars/${artifact}-${version}.jar"
  if [[ -f "$dependency_jar" ]]; then
    echo "Already present: $dependency_jar"
    continue
  fi
  curl -fL -o "$dependency_jar" \
    "https://repo1.maven.org/maven2/org/mongodb/${artifact}/${version}/${artifact}-${version}.jar"
  echo "Downloaded $dependency_jar"
done

ls -la jars/*.jar
echo "Set in config.env: MONGO_SPARK_JAR=jars/$JAR"
echo "Runtime dependency jars are loaded by scripts/run_spark_train.sh."
