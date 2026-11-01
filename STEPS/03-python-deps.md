# Step 03 — Python dependencies and Spark connector JAR

Load installed tool paths first:

```bash
source scripts/source_cluster_env.sh
```

From the repository root, with `config.env` in place:

```bash
python3 -m pip install --user -r requirements.txt
```

Or:

```bash
bash scripts/install_python_deps.sh
```

If `ensurepip` is missing, install Python's pip package using your operating
system's package manager, or use a virtual environment.

Download the Mongo Spark connector JAR (Spark 3.x path by default):

```bash
mkdir -p jars
bash scripts/fetch_mongo_spark_jar.sh
# or: bash scripts/fetch_mongo_spark_jar.sh spark4
```

If the cluster has **no outbound internet**, download the JAR on your laptop from Maven Central, upload to `jars/` on the master, and set `MONGO_SPARK_JAR` in `config.env` to that filename.

Confirm:

```bash
set -a && source config.env && set +a
ls -la "$MONGO_SPARK_JAR"
spark-submit --version 2>&1 | head -5
```

If `spark-submit` is still missing, return to [01-discover-cluster.md](01-discover-cluster.md) — do not use sudo.

Proceed to [04-download-data.md](04-download-data.md).
