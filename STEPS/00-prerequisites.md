# Step 00 — Prerequisites and Prayogshala access

## 1. Start cluster nodes

1. Open [Prayogshala login](https://prayogshala.bits-pilani.ac.in/auth/login) and sign in with your BITS credentials.
2. Open the **Big Data Systems** lab (or the environment that lists **Node 1 master**, **Node 2 slave1**, **Node 3 slave2**).
3. Start all three nodes until the dashboard shows **3/3 Active** (or equivalent).
4. Open a terminal **on the master node** (Node 1). All commands in this project assume you are in that shell unless noted.

**Do not use `sudo`** for discovery, Python, Mongo load, or Spark jobs. Sudo hides `spark-submit`, `yarn`, and `pip` on most lab images.

In each terminal session, from the repo root:

```bash
source scripts/source_cluster_env.sh
```

## 2. Get the project on the master

From your home directory (or a workspace folder):

```bash
git clone <YOUR_REMOTE_URL> bds-assignment2
cd bds-assignment2
```

If you already cloned once, update before each session:

```bash
cd bds-assignment2
git pull
```

**Screenshot (for report):** Cluster dashboard with three active nodes.

## 3. What you need on the master

- `python3` and **`python3 -m pip`** (a `pip3` command is not required)
- `java` (for Spark; usually preinstalled on the lab image)
- `spark-submit` on `PATH`
- Optional: `mongod` / `mongosh` — if missing, Step 02 installs MongoDB in your home directory (no root).

Proceed to [01-discover-cluster.md](01-discover-cluster.md).
