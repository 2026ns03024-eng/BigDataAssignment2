# CC ZG522 Assignment 2 — Scenario 3 (Healthcare Readmission)

**Track C — Hybrid:** MongoDB for document storage and aggregation analytics; Apache Spark (MLlib) for distributed feature engineering and readmission classification; predictions written back to MongoDB.

**Platform:** Self-hosted **two-VM** cluster (SSH). Run discovery and STEPS on the driver VM; see [old-context.md](old-context.md) when opening a **new** agent chat on the VMs.

## Quick start (driver VM)

1. [STEPS/00-prerequisites.md](STEPS/00-prerequisites.md) → [STEPS/08-screenshots.md](STEPS/08-screenshots.md)
2. `cp config.example.env config.env` (or `scripts/apply_cluster_env.sh`)
3. `bash scripts/discover_cluster.sh` before first run

## Repository layout

| Path | Purpose |
|------|---------|
| [old-context.md](old-context.md) | Handoff for new Cursor sessions on the cluster |
| `STEPS/` | Runbook (revalidate on your VMs) |
| `scripts/` | Pipeline and discovery |
| `queries/analytics.js` | Mongo aggregations for screenshots |
| `report/REPORT.md` | Submission (fill metrics after Spark run) |

## Dataset

UCI *Diabetes 130-US hospitals*, enriched with synthetic timestamps, vitals, and notes — see `report/REPORT.md`.

## Author

See the completed report cover in [report/REPORT.md](report/REPORT.md).
