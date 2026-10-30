# Step 00 — Prerequisites (self-hosted cluster)

## 1. Two-VM layout (typical)

| VM | Role |
|----|------|
| **VM1** | Git repo, MongoDB, Spark master, Python driver, `spark-submit` |
| **VM2** | Spark worker |

Connect both with SSH (e.g. Cursor Remote). Exact IPs and packages are **not** fixed in this repo — discover them on your machines.

**Do not use `sudo`** for project scripts; it often hides `spark-submit` and pip from your user PATH.

Each shell on VM1:

```bash
cd ~/workspace/BigDataAssignment2   # or your clone path
source scripts/source_cluster_env.sh
```

## 2. Clone or pull the repo

On VM1 (and sync repo to VM2 if Spark worker needs the same `SPARK_HOME` paths only — code can stay on VM1):

```bash
git clone <YOUR_REMOTE_URL> BigDataAssignment2
cd BigDataAssignment2
git pull
```

## 3. New Cursor chat on these VMs?

Open [old-context.md](../old-context.md) in the agent chat so it knows Track C scope, repo layout, and that it must **rediscover** your cluster and finish STEPS + report metrics.

## 4. Requirements

- Java 17+ (Spark 4.x)
- `python3` and `python3 -m pip` (via `scripts/install_python_deps.sh`)
- MongoDB + `mongosh` on VM1 (or user-local install per STEPS/02)
- Spark on PATH after `source scripts/source_cluster_env.sh`

Proceed to [01-discover-cluster.md](01-discover-cluster.md).
