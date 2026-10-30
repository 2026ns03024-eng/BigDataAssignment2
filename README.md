# CC ZG522 Assignment 2 — Scenario 3 (Healthcare Readmission)

**Track C — Hybrid:** MongoDB for document storage and aggregation analytics; Apache Spark (MLlib) for distributed feature engineering and readmission classification; predictions written back to MongoDB.

**Platform:** BITS Prayogshala cluster (master + slave1 + slave2). This repository is developed locally and run entirely on the cluster after `git pull`.

## Quick start (on cluster master)

1. Follow [STEPS/00-prerequisites.md](STEPS/00-prerequisites.md) through [STEPS/08-screenshots.md](STEPS/08-screenshots.md) in order.
2. Copy `config.example.env` to `config.env` and adjust using output from `bash scripts/discover_cluster.sh`.
3. Run the pipeline: data prep → Mongo load → Mongo analytics → Spark training → charts.

## Repository layout

| Path | Purpose |
|------|---------|
| `STEPS/` | Lab instructions for Prayogshala |
| `scripts/` | Python and shell automation |
| `queries/analytics.js` | Aggregation pipelines for `mongosh` screenshots |
| `report/REPORT.md` | Submission write-up (fill metrics after cluster run) |
| `data/` | UCI CSV and generated JSONL (not committed) |
| `output/` | `metrics.json` from Spark (not committed) |

## Dataset

UCI *Diabetes 130-US hospitals* encounter data, enriched with synthetic admission timestamps, prior-encounter links, vital sign samples, and brief clinical note text for document shape. See `report/REPORT.md` for limitations.

## Author

Fill name and BITS ID on the report cover before submission.
