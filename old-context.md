# Handoff context — CC ZG522 Assignment 2 (fresh VM / new agent)

Share this file in a **new Cursor chat** on your cluster VMs so the agent can continue without the old conversation.

---

## 1. Assignment goal (unchanged)

| Item | Choice |
|------|--------|
| Course | Big Data Systems (CC ZG522), Assignment 2 |
| Scenario | **3 — Healthcare** (30-day readmission risk) |
| Track | **C — Hybrid**: MongoDB (documents + aggregations) + Spark MLlib (training) + write predictions back to MongoDB |
| Marks context | ~10 marks; report + screenshots + reproducible pipeline |

**Not in scope for Track C:** Spark-only or Mongo-only tracks. Python is for ETL, orchestration, and matplotlib charts—not for model training (that is Spark).

Official brief (local copy): [ASSIGNMENT-2-BDS-12-10-2026.md](ASSIGNMENT-2-BDS-12-10-2026.md)

---

## 2. What this repo already contains

Implemented end-to-end **before** the user moved off BITS Prayogshala to a **self-managed 2-VM cluster** (SSH via Cursor).

| Path | Purpose |
|------|---------|
| [STEPS/](STEPS/) | Numbered runbook — **must be revalidated** on the new cluster |
| [scripts/](scripts/) | `prepare_documents.py`, `load_mongo.py`, `mongo_analytics.py`, `train_readmission.py`, `make_charts.py`, shell helpers |
| [queries/analytics.js](queries/analytics.js) | `$lookup`, `$graphLookup`, `$setWindowFields`, `$bucket` for mongosh |
| [report/REPORT.md](report/REPORT.md) | Submission write-up; **metrics still TBD** until Spark runs |
| `config.env` | **Not in git** — create from `config.example.env` + discovery |
| `data/` | UCI CSV + generated JSONL (gitignored) |
| `output/metrics.json` | Written by Spark job (gitignored) |

**Dataset:** UCI Diabetes 130-US hospitals CSV, enriched with synthetic admission times, `prev_encounter_id`, 8 vitals/encounter, templated notes. Download: `bash scripts/download_uci_diabetes.sh` (URL: UCI static `.../296/data.csv`).

**Mongo collections** (`readmission` DB): `patients`, `encounters`, `vitals`, `predictions` (Spark output).

---

## 3. What changed (BITS → your 2 VMs)

- User **abandoned BITS Prayogshala** (sudo/PATH issues, no `/etc/hosts`, YARN down, Spark 4.1.2 on master only after `source scripts/source_cluster_env.sh`).
- User now has **2 VMs** (typical layout: **VM1 = Mongo + Spark master + driver**, **VM2 = Spark worker**). Exact IPs, OS, and install paths are **unknown to this handoff** — the next agent must **discover and replan**, not assume Prayogshala IPs or 3 nodes.

**Repo cleanup:** BITS/Prayogshala-specific steps and hard-coded AWS IPs were removed. Generic cluster notes live in `STEPS/01b-two-node-cluster.md` and `cluster/cluster.env.example`.

---

## 4. First actions for the next agent (mandatory)

1. **Read** this file and [README.md](README.md).
2. **Run discovery on VM1** (repo root, no sudo):
   ```bash
   source scripts/source_cluster_env.sh
   mkdir -p output && bash scripts/discover_cluster.sh | tee output/discover.log
   ```
3. **Inspect VM2** via SSH: Spark worker, Java, can it `mongosh`/`telnet` to VM1 Mongo on 27017?
4. **Write or update `config.env`** with:
   - `MONGO_HOST` = IP reachable from **both** VMs (usually VM1’s IP, not `127.0.0.1` if executors run on VM2)
   - `SPARK_MASTER` = `spark://<VM1-IP>:7077` or `yarn` if YARN works, or `local[*]` as last resort
   - `MONGO_SPARK_JAR` = match Spark major version (Spark **4.x** → `jars/mongo-spark-connector_2.13-11.1.0.jar`; Spark 3.x → `_2.12-10.2.0.jar`)
5. **Replan STEPS 01b** if needed: start Spark master/worker, firewall, Mongo bind address, connector jar fetch.
6. **Execute pipeline** in order: STEPS 03 → 07, then fill [report/REPORT.md](report/REPORT.md) from `output/metrics.json` and capture screenshots per STEPS/08.

Do **not** invent AUROC/accuracy in the report; only values from `output/metrics.json` after a real run.

---

## 5. Technical pitfalls already hit once

| Issue | Mitigation |
|-------|------------|
| `sudo` hides `spark-submit`, `yarn`, pip | Never use sudo for project scripts |
| No `pip3` on PATH | `bash scripts/install_python_deps.sh` (`python3 -m pip`) |
| Mongo on `127.0.0.1` only | Workers cannot read Mongo; bind/listen on VM1 LAN IP or use `local` Spark on VM1 only |
| Spark 4.1 + old connector 10.2 | Use connector **11.1.0** / Scala **2.13** |
| Empty `/etc/hosts` | Normal; use **IPs** in `SPARK_MASTER`, `MONGO_HOST`, `SPARK_LOCAL_IP` |
| YARN unreachable | Spark standalone master + workers |

---

## 6. Pipeline command cheat sheet (after `config.env` is correct)

On **VM1** (from repo root):

```bash
source scripts/source_cluster_env.sh
set -a && source config.env && set +a

bash scripts/install_python_deps.sh
bash scripts/fetch_mongo_spark_jar.sh
bash scripts/download_uci_diabetes.sh
python3 scripts/prepare_documents.py
python3 scripts/load_mongo.py
python3 scripts/mongo_analytics.py
bash scripts/run_spark_train.sh
python3 scripts/make_charts.py
```

---

## 7. Git / workspace

- Project may live at `~/workspace/BigDataAssignment2` or similar on the VMs.
- User develops with Cursor SSH to the cluster; laptop may only push/pull git.
- `.gitignore` excludes `config.env`, `data/*.csv`, `data/*.jsonl`, `output/`, `jars/`, `cluster/cluster.env`.

---

## 8. User preferences

- Submission tone: **M.Tech student**, not generic AI prose.
- Report cover: user fills **name** and **BITS ID** (do not guess from email).
- Assignment PDF still mentions Prayogshala as *Option A*; user uses **Option B** (own VMs) — screenshots should show **their** Spark UI / SSH hosts, not Prayogshala UI.

---

## 9. Suggested agent prompt (copy-paste)

```text
Read old-context.md and ASSIGNMENT-2-BDS-12-10-2026.md. This is CC ZG522 Assignment 2 Track C (healthcare readmission). I have a 2-VM cluster over SSH. Run discover_cluster.sh on VM1, SSH to VM2, update config.env and STEPS/01b if needed, then run the full pipeline and fill report metrics from output/metrics.json. Do not use sudo. Do not invent metrics.
```

---

*Last updated when migrating off BITS Prayogshala to self-hosted 2-VM cluster.*
