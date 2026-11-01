#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p output

# shellcheck disable=SC1091
source "$ROOT/scripts/source_cluster_env.sh" 2>/dev/null || true

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

DEPENDENCIES=()
case "$(basename "$JAR")" in
  mongo-spark-connector_2.13-11.1.0.jar)
    DEPENDENCIES=(mongodb-driver-sync-5.1.4.jar mongodb-driver-core-5.1.4.jar bson-5.1.4.jar bson-record-codec-5.1.4.jar)
    ;;
  mongo-spark-connector_2.12-10.2.0.jar)
    DEPENDENCIES=(mongodb-driver-sync-4.8.2.jar mongodb-driver-core-4.8.2.jar bson-4.8.2.jar bson-record-codec-4.8.2.jar)
    ;;
  mongo-spark-connector_2.11-2.4.4.jar)
    DEPENDENCIES=(mongo-java-driver-3.12.5.jar)
    ;;
esac

JARS="$JAR"
for dependency in "${DEPENDENCIES[@]}"; do
  dependency_path="$ROOT/jars/$dependency"
  if [[ ! -f "$dependency_path" ]]; then
    echo "Missing connector dependency: $dependency_path — run bash scripts/fetch_mongo_spark_jar.sh"
    exit 1
  fi
  JARS="$JARS,$dependency_path"
done

spark-submit \
  --master "$MASTER" \
  --deploy-mode client \
  --driver-memory 2g \
  --executor-memory 2g \
  --conf spark.driver.port=7079 \
  --conf spark.blockManager.port=7081 \
  --conf spark.sql.shuffle.partitions=8 \
  --jars "$JARS" \
  "$ROOT/scripts/train_readmission.py"
