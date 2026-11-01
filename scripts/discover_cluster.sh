#!/usr/bin/env bash
# Discover cluster software for Assignment 2 Track C.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p output jars

echo "=== Host ==="
hostname -f 2>/dev/null || hostname
echo "=== Working directory ==="
pwd
echo "=== User ==="
whoami
if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
  echo ""
  echo "*** WARNING: Running as root (sudo). Lab tools (spark-submit, yarn, pip) are often NOT on root's PATH."
  echo "    Re-run WITHOUT sudo:  bash scripts/discover_cluster.sh | tee output/discover.log"
  echo ""
fi
echo ""
echo "=== Load lab environment (optional) ==="
# shellcheck disable=SC1091
if [[ -f "$ROOT/scripts/source_cluster_env.sh" ]]; then
  source "$ROOT/scripts/source_cluster_env.sh" || true
else
  echo "(source_cluster_env.sh missing)"
fi
set -a
[[ -f "$ROOT/config.env" ]] && source "$ROOT/config.env"
set +a
MONGO_HOST="${MONGO_HOST:-${SPARK_LOCAL_IP:-127.0.0.1}}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_DB="${MONGO_DB:-readmission}"
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
echo "=== Python / pip ==="
python3 --version 2>&1 || echo "python3 NOT FOUND"
if command -v pip3 >/dev/null 2>&1; then
  pip3 --version 2>&1
elif python3 -m pip --version >/dev/null 2>&1; then
  python3 -m pip --version 2>&1
  echo "# Install deps with: python3 -m pip install --user -r requirements.txt"
else
  echo "pip NOT FOUND — try: python3 -m ensurepip --user  OR ask lab support"
fi
echo ""
echo "=== Spark ==="
SPARK_VER=""
if command -v spark-submit >/dev/null 2>&1; then
  spark-submit --version 2>&1 | head -8
  SPARK_VER=$(spark-submit --version 2>&1 | grep -oE 'version [0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 | awk '{print $2}' || true)
else
  echo "spark-submit NOT FOUND on PATH"
  echo "  Try:  source scripts/source_cluster_env.sh"
  echo "  Then start Spark master/worker (see STEPS/01b-two-node-cluster.md)."
  echo "  Search hints:"
  find /usr/local /opt /usr/hdp -maxdepth 5 -name spark-submit -type f 2>/dev/null | head -5 || true
fi
echo ""
echo "=== YARN ==="
YARN_OK=0
if command -v yarn >/dev/null 2>&1; then
  YARN_OUT=$(yarn node -list 2>&1 | head -15 || true)
  echo "$YARN_OUT"
  if echo "$YARN_OUT" | grep -qiE 'Total Nodes:[1-9]|RUNNING'; then
    YARN_OK=1
  elif echo "$YARN_OUT" | grep -qi 'Retrying connect'; then
    echo "# ResourceManager not reachable — use Spark standalone spark://<driver-ip>:7077"
  fi
else
  echo "yarn NOT FOUND on PATH (source source_cluster_env.sh or use Spark standalone master URL)"
fi
echo ""
echo "=== MongoDB ==="
command -v mongod >/dev/null 2>&1 && mongod --version | head -1 || echo "mongod NOT FOUND"
command -v mongosh >/dev/null 2>&1 && mongosh --version 2>&1 | head -1 || echo "mongosh NOT FOUND (try mongo shell)"
command -v mongo >/dev/null 2>&1 && mongo --version 2>&1 | head -1 || true
if command -v mongosh >/dev/null 2>&1; then
  mongosh --host "$MONGO_HOST" --port "$MONGO_PORT" --quiet --eval 'db.runCommand({ ping: 1 })' 2>&1 | head -3 || echo "mongosh ping failed — is mongod running?"
fi
echo ""
echo "=== Suggested config.env values ==="
DRIVER_IP="${SPARK_LOCAL_IP:-CHANGE_ME_DRIVER_PRIVATE_IP}"

SPARK_MASTER_SUGGEST="spark://${DRIVER_IP}:7077"
if [[ "$YARN_OK" -eq 1 ]]; then
  SPARK_MASTER_SUGGEST="yarn"
fi
echo "MONGO_HOST=$MONGO_HOST"
echo "MONGO_PORT=$MONGO_PORT"
echo "MONGO_DB=$MONGO_DB"
echo "SPARK_MASTER=$SPARK_MASTER_SUGGEST"
echo "SPARK_LOCAL_IP=$DRIVER_IP"

MAJOR=""
MINOR=""
if [[ -n "$SPARK_VER" ]]; then
  MAJOR=$(echo "$SPARK_VER" | cut -d. -f1)
  MINOR=$(echo "$SPARK_VER" | cut -d. -f2)
fi
if [[ "$MAJOR" == "2" ]]; then
  JAR_REL="jars/mongo-spark-connector_2.11-2.4.4.jar"
  echo "MONGO_SPARK_JAR=$JAR_REL"
  echo "USE_SPARK24_URI=1"
  echo "# Spark 2.4 — run: bash scripts/fetch_mongo_spark_jar.sh spark24"
elif [[ "$MAJOR" -ge 4 ]] 2>/dev/null || [[ "$MAJOR" == "4" ]]; then
  JAR_REL="jars/mongo-spark-connector_2.13-11.1.0.jar"
  echo "MONGO_SPARK_JAR=$JAR_REL"
  echo "# Spark 4.x — run: bash scripts/fetch_mongo_spark_jar.sh spark4"
else
  JAR_REL="jars/mongo-spark-connector_2.12-10.2.0.jar"
  echo "MONGO_SPARK_JAR=$JAR_REL"
  echo "# Spark 3.x — run: bash scripts/fetch_mongo_spark_jar.sh spark3"
fi
echo "DATA_CSV=data/diabetic_data.csv"
echo ""
echo "# Two-VM cluster: see STEPS/01b-two-node-cluster.md and cluster/cluster.env.example"
echo "# Set SPARK_LOCAL_IP to the driver's private IP reachable from the worker; use it in MONGO_HOST and SPARK_MASTER."
echo ""
echo "Copy the block above into config.env after: cp config.example.env config.env"
echo "Before Spark jobs, each new shell:  source scripts/source_cluster_env.sh"
