# Step 00 — Prerequisites (self-hosted cluster)

## 1. Two-VM layout (typical)

| VM | Role |
|----|------|
| **VM1** | Git repo, MongoDB, Spark master, Python driver, `spark-submit` |
| **VM2** | Spark worker |

Connect both with SSH. Exact IPs and packages are **not** fixed in this repo — discover them on your machines.

**Do not use `sudo`** for project scripts; it often hides `spark-submit` and pip from your user PATH.

Each shell on VM1:

```bash
cd ~/workspace/readmission-analytics   # or your clone path
source scripts/source_cluster_env.sh
```

## 2. Clone or pull the repo

On VM1 (and sync repo to VM2 if Spark worker needs the same `SPARK_HOME` paths only — code can stay on VM1):

```bash
git clone <YOUR_REMOTE_URL> readmission-analytics
cd readmission-analytics
git pull
```

## 3. Requirements

- Java 17+ (Spark 4.x)
- `python3` and `python3 -m pip` (via `scripts/install_python_deps.sh`)
- MongoDB + `mongosh` on VM1 (or user-local install per STEPS/02)
- Spark on PATH after `source scripts/source_cluster_env.sh`

If an editor sets `JAVA_HOME` to an inaccessible location, point it to your
installed JDK before starting Spark. Verify with `"$JAVA_HOME/bin/java" -version`.

Proceed to [01-discover-cluster.md](01-discover-cluster.md).
