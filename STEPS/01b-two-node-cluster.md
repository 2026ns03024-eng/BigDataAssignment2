# Step 01b — Two-VM Spark cluster (agent: discover first, then edit)

This project assumes **two Linux VMs** you control over SSH (Option B in the assignment brief). There is no shared lab UI — you must learn IPs, installed software, and open ports yourself.

## Agent checklist

1. On **VM1** (driver): `mkdir -p output && bash scripts/discover_cluster.sh | tee output/discover.log`
2. On **VM2**: same discover snippet for Java/Spark paths; test Mongo from VM2:
   ```bash
   mongosh "mongodb://${VM1_IP}:27017" --eval 'db.runCommand({ ping: 1 })'
   ```
3. Copy [cluster/cluster.env.example](../cluster/cluster.env.example) → `cluster/cluster.env` with real IPs; run `bash scripts/apply_cluster_env.sh`
4. Start **Spark standalone** (if not already running):
   - Use the same private interface on both VMs for Spark and Mongo traffic. Confirm the peer private IP is reachable before choosing it.
   - VM1:
     ```bash
     unset SPARK_MASTER
     export SPARK_LOCAL_IP=<VM1_PRIVATE_IP>
     export SPARK_MASTER_HOST=$SPARK_LOCAL_IP SPARK_MASTER_PORT=7077 SPARK_MASTER_WEBUI_PORT=8080
     $SPARK_HOME/sbin/start-master.sh
     ```
   - VM2:
     ```bash
     unset SPARK_MASTER
     export SPARK_LOCAL_IP=<VM2_PRIVATE_IP>
     export SPARK_WORKER_PORT=7078 SPARK_WORKER_WEBUI_PORT=8081
     export SPARK_WORKER_MEMORY=6g SPARK_WORKER_CORES=4
     $SPARK_HOME/sbin/start-worker.sh spark://<VM1_PRIVATE_IP>:7077
     ```
5. Confirm Spark master UI (port **8080**) shows **1 worker** (or 2 if you add more VMs later).

### Firewalld

On each VM, allow the other VM's private IP only; do not expose MongoDB or Spark ports to the public NIC. Add one rule per port, then reload:

```bash
sudo firewall-cmd --permanent --add-rich-rule="rule family=ipv4 source address=<PEER_PRIVATE_IP>/32 port port=<PORT> protocol=tcp accept"
sudo firewall-cmd --reload
```

Allow **7077, 7079, 7081, 27017, 8080** on VM1. Allow **7078, 7081, 8081** on VM2. The training script fixes Spark's driver/block-manager ports to 7079/7081; 27017 is only needed on VM1 when MongoDB runs there.

Do not export the project's `SPARK_MASTER=spark://...` setting while running the standalone start scripts: Spark's daemon scripts also use that variable for an optional rsync source. If `config.env` was sourced, run `unset SPARK_MASTER` before starting them.

## `config.env` rules

| Setting | Guidance |
|---------|----------|
| `MONGO_HOST` | VM1 private IP if Mongo runs on VM1 and Spark executors may run on VM2 |
| `SPARK_MASTER` | `spark://<VM1-private-IP>:7077` unless YARN works (`discover` will suggest) |
| `MONGO_SPARK_JAR` | From discover output (Spark 4 → `_2.13-11.1.0.jar`) |

Set MongoDB's bind address to `MONGO_HOST`; the provided start script binds only to that address. If Mongo is **localhost-only**, set `SPARK_MASTER=local[4]` and `MONGO_HOST=127.0.0.1` on VM1 only and note the limitation in the report.

## Screenshots for report

Spark master UI with worker(s), `mongosh` aggregation sample, Spark job log — not a third-party lab portal.

Proceed to [03-python-deps.md](03-python-deps.md) after `config.env` is set.
