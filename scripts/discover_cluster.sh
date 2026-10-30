#!/usr/bin/env bash
# Discover Prayogshala / lab environment for Assignment 2 Track C.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p output jars

echo "=== Host ==="
hostname -f 2>/dev/null || hostname
echo "=== Working directory ==="
pwd
echo ""
echo "=== /etc/hosts (grep -E 'master|slave|node') ==="
grep -E 'master|slave|node|prayog' /etc/hosts 2>/dev/null || echo "(no matching lines or permission denied)"
echo ""
echo "=== Java ==="
if command -v java >/dev/null 2>&1; then
  java -version 2>&1 | head -3
else
  echo "java NOT FOUND"
fi
echo ""
echo "=== Python ==="
python3 --version 2>&1 || echo "python3 NOT FOUND"
pip3 --version 2>&1 || echo "pip3 NOT FOUND"
echo ""
echo "=== Spark ==="
if command -v spark-submit >/dev/null 2>&1; then
  spark-submit --version 2>&1 | head -8
  SPARK_VER=$(spark-submit --version 2>&1 | grep -oE 'version [0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 | awk '{print $2}' || true)
else
  echo "spark-submit NOT FOUND"
  SPARK_VER=""
fi
echo ""
echo "=== YARN ==="
if command -v yarn >/dev/null 2>&1; then
  yarn node -list 2>&1 | head -10 || echo "yarn node -list failed"
else
  echo "yarn NOT FOUND"
fi
echo ""
echo "=== MongoDB ==="
command -v mongod >/dev/null 2>&1 && mongod --version | head -1 || echo "mongod NOT FOUND"
command -v mongosh >/dev/null 2>&1 && mongosh --version 2>&1 | head -1 || echo "mongosh NOT FOUND (try mongo shell)"
command -v mongo >/dev/null 2>&1 && mongo --version 2>&1 | head -1 || true
echo ""
echo "=== Suggested config.env values ==="
MONGO_HOST="${MONGO_HOST:-127.0.0.1}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_DB="${MONGO_DB:-readmission}"

SPARK_MASTER_SUGGEST="spark://$(hostname -f 2>/dev/null || hostname):7077"
if command -v yarn >/dev/null 2>&1 && yarn node -list >/dev/null 2>&1; then
  SPARK_MASTER_SUGGEST="yarn"
fi
echo "MONGO_HOST=$MONGO_HOST"
echo "MONGO_PORT=$MONGO_PORT"
echo "MONGO_DB=$MONGO_DB"
echo "SPARK_MASTER=$SPARK_MASTER_SUGGEST"

MAJOR=""
if [[ -n "$SPARK_VER" ]]; then
  MAJOR=$(echo "$SPARK_VER" | cut -d. -f1)
fi
if [[ "$MAJOR" == "2" ]]; then
  JAR_REL="jars/mongo-spark-connector_2.11-2.4.4.jar"
  echo "MONGO_SPARK_JAR=$JAR_REL"
  echo "USE_SPARK24_URI=1"
  echo "# Spark 2.4 detected — run: bash scripts/fetch_mongo_spark_jar.sh spark24"
else
  JAR_REL="jars/mongo-spark-connector_2.12-10.2.0.jar"
  echo "MONGO_SPARK_JAR=$JAR_REL"
  echo "# Spark 3.x assumed — run: bash scripts/fetch_mongo_spark_jar.sh"
fi
echo "DATA_CSV=data/diabetic_data.csv"
echo ""
echo "Copy the block above into config.env after: cp config.example.env config.env"
