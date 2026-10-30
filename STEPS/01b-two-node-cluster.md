# Step 01b — Two-VM Spark cluster (agent: discover first, then edit)

This project assumes **two Linux VMs** you control over SSH (Option B in the assignment brief). There is no shared lab UI — you must learn IPs, installed software, and open ports yourself.

## Agent checklist

1. On **VM1** (driver): `bash scripts/discover_cluster.sh | tee output/discover.log`
2. On **VM2**: same discover snippet for Java/Spark paths; test Mongo from VM2:
   ```bash
   mongosh "mongodb://${VM1_IP}:27017" --eval 'db.runCommand({ ping: 1 })'
   ```
3. Copy [cluster/cluster.env.example](../cluster/cluster.env.example) → `cluster/cluster.env` with real IPs; run `bash scripts/apply_cluster_env.sh`
4. Start **Spark standalone** (if not already running):
   - VM1: `export SPARK_MASTER_HOST=<VM1_IP> SPARK_LOCAL_IP=<VM1_IP>` then `$SPARK_HOME/sbin/start-master.sh`
   - VM2: `export SPARK_LOCAL_IP=<VM2_IP>` then `$SPARK_HOME/sbin/start-worker.sh spark://<VM1_IP>:7077`
5. Confirm Spark master UI (port **8080**) shows **1 worker** (or 2 if you add more VMs later).

## `config.env` rules

| Setting | Guidance |
|---------|----------|
| `MONGO_HOST` | VM1 IP if Mongo runs on VM1 and Spark executors may run on VM2 |
| `SPARK_MASTER` | `spark://<VM1-IP>:7077` unless YARN works (`discover` will suggest) |
| `MONGO_SPARK_JAR` | From discover output (Spark 4 → `_2.13-11.1.0.jar`) |

If Mongo is **localhost-only** and cannot be opened on the LAN, either fix `mongod` bind/firewall or set `SPARK_MASTER=local[4]` and `MONGO_HOST=127.0.0.1` on VM1 only and note the limitation in the report.

## Screenshots for report

Spark master UI with worker(s), `mongosh` aggregation sample, Spark job log — not a third-party lab portal.

Proceed to [03-python-deps.md](03-python-deps.md) after `config.env` is set.
