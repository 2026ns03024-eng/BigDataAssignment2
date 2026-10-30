# Step 01b — Prayogshala three-node Spark (no /etc/hosts entries)

Prayogshala shows **master** and **worker** VMs by **IP only**. A minimal `/etc/hosts` (localhost only) is normal. You do **not** need `master` / `slave1` hostnames if you use IPs everywhere.

| Role | Prayogshala name | IP (your lab) |
|------|------------------|---------------|
| Node 1 | master | **10.3.21.218** |
| Node 2 | slave1 / worker | **10.3.23.119** |
| Node 3 | slave2 / worker | **10.3.23.64** |

YARN is not on your PATH — use **Spark standalone** at `spark://10.3.21.218:7077`.

## 1. One-time `config.env` from IPs

On the **master** terminal:

```bash
cp cluster/prayogshala.env.example cluster/prayogshala.env
# edit if Prayogshala assigns new IPs after terminate/start
bash scripts/apply_prayogshala_env.sh
```

Important: **`MONGO_HOST=10.3.21.218`**, not `127.0.0.1`, so executors on the two workers can reach MongoDB on the master.

Test from **slave1** terminal (Prayogshala → Connect on Node 2):

```bash
mongosh "mongodb://10.3.21.218:27017" --eval 'db.runCommand({ ping: 1 })'
```

If ping fails, Mongo may be bound to localhost only — ask lab support to allow remote connections on port 27017, or run Spark in local mode on the master only (see note at bottom).

## 2. Start Spark standalone (three nodes)

Load Spark on **each** node in every session:

```bash
cd ~/workspace/BigDataAssignment2
source scripts/source_cluster_env.sh
```

### On master (10.3.21.218)

```bash
export SPARK_MASTER_HOST=10.3.21.218
export SPARK_LOCAL_IP=10.3.21.218
$SPARK_HOME/sbin/start-master.sh
```

Open Spark UI: `http://10.3.21.218:8080` (or the URL printed in the log). Confirm master URL **`spark://10.3.21.218:7077`**.

### On slave1 (10.3.23.119)

Use Prayogshala **Connect** on Node 2:

```bash
source ~/workspace/BigDataAssignment2/scripts/source_cluster_env.sh
export SPARK_LOCAL_IP=10.3.23.119
$SPARK_HOME/sbin/start-worker.sh spark://10.3.21.218:7077
```

### On slave2 (10.3.23.64)

Same on Node 3 with `SPARK_LOCAL_IP=10.3.23.64`.

Refresh the master UI — you should see **2 workers alive**.

**Screenshot (for report):** Spark master UI with 2 workers + Prayogshala 3/3 nodes.

## 3. Python packages (no `pip3` command)

On the **master** only:

```bash
bash scripts/install_python_deps.sh
bash scripts/fetch_mongo_spark_jar.sh
# auto-detects Spark 4.x -> mongo-spark-connector_2.13-11.1.0.jar
```

## 4. Continue pipeline

Return to [04-download-data.md](04-download-data.md) through [07-spark-training.md](07-spark-training.md). Before training:

```bash
source scripts/source_cluster_env.sh
set -a && source config.env && set +a
bash scripts/run_spark_train.sh
```

### Fallback: Spark local mode on master only

If Mongo cannot be reached from workers, set in `config.env`:

```bash
SPARK_MASTER=local[4]
MONGO_HOST=127.0.0.1
```

You lose multi-node Spark for the assignment demo, but Mongo + ML still run for partial credit; mention the network limit in the report.

Proceed to [02-mongodb.md](02-mongodb.md) if you have not loaded data yet.
