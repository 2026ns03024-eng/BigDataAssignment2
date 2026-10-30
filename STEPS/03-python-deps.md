# Step 03 — Python dependencies and Spark connector JAR

From the repository root, with `config.env` in place:

```bash
pip3 install --user -r requirements.txt
```

Download the Mongo Spark connector JAR (Spark 3.x path by default):

```bash
mkdir -p jars
bash scripts/fetch_mongo_spark_jar.sh
```

If the cluster has **no outbound internet**, download the JAR on your laptop from Maven Central, upload to `jars/` on the master, and set `MONGO_SPARK_JAR` in `config.env` to that filename.

Confirm:

```bash
ls -la "$MONGO_SPARK_JAR"
spark-submit --version 2>&1 | head -5
```

Proceed to [04-download-data.md](04-download-data.md).
