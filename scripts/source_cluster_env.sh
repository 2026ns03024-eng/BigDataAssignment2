#!/usr/bin/env bash
# Load Spark/Hadoop paths on Linux VMs (lab or self-hosted).
# Usage (from repo root):  source scripts/source_cluster_env.sh
#
# Do NOT run under sudo — root uses a minimal PATH and hides lab tools.

if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
  echo "WARNING: you are root/sudo. Spark and yarn are usually missing from PATH." >&2
  echo "  Exit sudo and run:  source scripts/source_cluster_env.sh" >&2
fi

for base in "$HOME"/mongo/mongodb-*/bin "$HOME/mongosh/bin"; do
  if [[ -x "$base/mongod" || -x "$base/mongosh" ]]; then
    export PATH="$base:$PATH"
  fi
done

# Lab-provided snippets (if present)
for f in /etc/profile.d/spark.sh /etc/profile.d/hadoop.sh /etc/profile.d/bigdata.sh; do
  if [[ -f "$f" ]]; then
    # shellcheck disable=SC1090
    source "$f"
  fi
done

# Common install roots (first match wins)
if [[ -z "${SPARK_HOME:-}" ]] || [[ ! -x "${SPARK_HOME}/bin/spark-submit" ]]; then
  for base in \
    /usr/local/spark \
    /usr/local/spark/current \
    /opt/spark \
    /opt/cloudera/parcels/CDH/lib/spark \
    /usr/hdp/current/spark3-client \
    /usr/hdp/current/spark2-client \
    "$HOME/spark" \
    "$HOME/spark/current"; do
    if [[ -x "$base/bin/spark-submit" ]]; then
      export SPARK_HOME="$base"
      break
    fi
  done
fi

if [[ -n "${SPARK_HOME:-}" ]]; then
  export PATH="$SPARK_HOME/bin:$SPARK_HOME/sbin:${PATH}"
fi

if [[ -z "${HADOOP_HOME:-}" ]] || [[ ! -x "${HADOOP_HOME}/bin/yarn" ]]; then
  for base in \
    /usr/local/hadoop \
    /opt/hadoop \
    /usr/hdp/current/hadoop-client \
    "$HOME/hadoop"; do
    if [[ -x "$base/bin/yarn" ]]; then
      export HADOOP_HOME="$base"
      break
    fi
  done
fi

if [[ -n "${HADOOP_HOME:-}" ]]; then
  export PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:${PATH}"
fi

# Last resort: search shallow paths (can be slow on some systems)
if ! command -v spark-submit >/dev/null 2>&1; then
  found="$(find /usr/local /opt /usr/hdp -maxdepth 5 -name spark-submit -type f 2>/dev/null | head -1 || true)"
  if [[ -n "$found" ]]; then
    export SPARK_HOME="$(dirname "$(dirname "$found")")"
    export PATH="$(dirname "$found"):$PATH"
  fi
fi

if command -v spark-submit >/dev/null 2>&1; then
  echo "SPARK_HOME=${SPARK_HOME:-unknown}  spark-submit=$(command -v spark-submit)"
else
  echo "spark-submit still not on PATH — set SPARK_HOME or install Spark; see STEPS/01b." >&2
fi

if command -v yarn >/dev/null 2>&1; then
  echo "yarn=$(command -v yarn)"
fi
