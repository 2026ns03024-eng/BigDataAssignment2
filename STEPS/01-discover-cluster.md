# Step 01 — Discover cluster layout

## Important: do not use `sudo`

Prayogshala tools (`spark-submit`, `yarn`, user `pip`) are on **your student PATH**, not root’s. If you run:

```bash
sudo bash scripts/discover_cluster.sh   # wrong
```

you will see **spark-submit NOT FOUND** and **yarn NOT FOUND** even when the lab is fine.

Use:

```bash
mkdir -p output
bash scripts/discover_cluster.sh | tee output/discover.log
```

## Load Spark / Hadoop into PATH

In **every new terminal** (and before discover if Spark was missing):

```bash
cd ~/workspace/BigDataAssignment2   # your repo path
source scripts/source_cluster_env.sh
bash scripts/discover_cluster.sh | tee output/discover.log
```

If Spark is still missing, ensure **3/3 nodes are active** in Prayogshala and any **Start Hadoop / Spark** action in the lab UI has been run. Then ask lab support for the correct `SPARK_HOME` on your image.

## YARN vs Spark standalone

| Symptom | What to put in `config.env` |
|---------|------------------------------|
| `yarn node -list` shows live worker nodes | `SPARK_MASTER=yarn` |
| YARN retries `0.0.0.0:8032` / ResourceManager down | `SPARK_MASTER=spark://<master-hostname>:7077` (use FQDN from discover output) |
| MongoDB already running (you have `mongosh` + ping OK) | Keep `MONGO_HOST=127.0.0.1` — **do not** run `install_mongo_user.sh` |

Your host looked like: `ip-10-3-21-218.ap-south-1.compute.internal` — that FQDN in `spark://...:7077` is correct when YARN is down but Spark master is on this VM.

## Configure `config.env`

```bash
cp config.example.env config.env
vi config.env   # or nano
```

Edit using the discover block:

| Variable | What to set |
|----------|-------------|
| `MONGO_HOST` | `127.0.0.1` if Mongo is on this node (you already have Mongo 8.x) |
| `MONGO_PORT` | `27017` |
| `SPARK_MASTER` | `yarn` **only if** YARN lists nodes; else `spark://ip-10-3-21-218.ap-south-1.compute.internal:7077` |
| `MONGO_SPARK_JAR` | Path from discover |

Verify config:

```bash
python3 -c "import sys; sys.path.insert(0,'scripts'); import config_loader; print(config_loader.load())"
```

Proceed to [01b-prayogshala-spark-cluster.md](01b-prayogshala-spark-cluster.md) if `/etc/hosts` has no master/slave lines (typical Prayogshala AWS VMs).

Proceed to [02-mongodb.md](02-mongodb.md) — skip user Mongo install if `mongosh` ping works.
