#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p output

set -a
# shellcheck disable=SC1091
[[ -f config.env ]] && source config.env
set +a

JAR="${MONGO_SPARK_JAR:-jars/mongo-spark-connector_2.12-10.2.0.jar}"
MASTER="${SPARK_MASTER:-yarn}"

if [[ ! -f "$JAR" ]]; then
  echo "Missing jar: $JAR — run bash scripts/fetch_mongo_spark_jar.sh"
  exit 1
fi

spark-submit \
  --master "$MASTER" \
  --deploy-mode client \
  --driver-memory 2g \
  --executor-memory 2g \
  --conf spark.sql.shuffle.partitions=8 \
  --jars "$JAR" \
  "$ROOT/scripts/train_readmission.py"
