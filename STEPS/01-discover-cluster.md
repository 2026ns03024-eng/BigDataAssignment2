# Step 01 — Discover cluster layout

## Do not use `sudo`

If you run `sudo bash scripts/discover_cluster.sh`, you may see **spark-submit NOT FOUND** even when Spark is installed for your user.

```bash
mkdir -p output
source scripts/source_cluster_env.sh
bash scripts/discover_cluster.sh | tee output/discover.log
```

Repeat on **VM2** (at least Java, Spark paths, and Mongo reachability to VM1).

## Configure `config.env`

```bash
cp config.example.env config.env
```

Either edit manually using the discover block, or:

```bash
cp cluster/cluster.env.example cluster/cluster.env
# set VM1_IP, VM2_IP, MONGO_HOST, SPARK_MASTER_URL
bash scripts/apply_cluster_env.sh
```

| Variable | What to set |
|----------|-------------|
| `MONGO_HOST` | IP where `mongod` listens and workers can connect |
| `MONGO_PORT` | Usually `27017` |
| `SPARK_MASTER` | From discover (`yarn` or `spark://<ip>:7077`) |
| `MONGO_SPARK_JAR` | From discover (Spark 4 → `_2.13-11.1.0.jar`) |

Verify:

```bash
python3 -c "import sys; sys.path.insert(0,'scripts'); import config_loader; print(config_loader.load())"
```

Proceed to [01b-two-node-cluster.md](01b-two-node-cluster.md) to start Spark master/worker and validate Mongo from VM2.

Proceed to [02-mongodb.md](02-mongodb.md) when Mongo ping works.
