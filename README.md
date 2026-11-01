# Healthcare Readmission Analytics

A hybrid analytics pipeline using MongoDB for document storage and aggregations,
Apache Spark MLlib for readmission classification, and Python for data preparation
and visualization. Predictions are written back to MongoDB.

## Problem

Estimate whether a hospital encounter is followed by readmission within 30 days,
while demonstrating how document-local analytics and distributed model training
can be combined. The target is 1 for the source label `<30`, and 0 for `NO` or `>30`.

The UCI *Diabetes 130-US hospitals* dataset is enriched with synthetic timestamps,
vitals, and notes for document and time-series demonstrations. Synthetic vitals
depend on the target label and are deliberately excluded from model features.
Evaluation uses a patient-level holdout to prevent the same patient appearing in
both training and test sets. This is an experimental pipeline, not a clinical tool.

## Quick start (driver VM)

Follow the [setup and execution runbook](STEPS/00-prerequisites.md) through
[model training](STEPS/07-spark-training.md). Configure your own infrastructure
using [config.example.env](config.example.env); host addresses in
[cluster/cluster.env.example](cluster/cluster.env.example) are documentation-only
examples, not live endpoints.

Once MongoDB, Spark, and Python dependencies are available:

```bash
source scripts/source_cluster_env.sh
bash scripts/download_uci_diabetes.sh
python3 scripts/prepare_documents.py
python3 scripts/load_mongo.py
python3 scripts/mongo_analytics.py
bash scripts/fetch_mongo_spark_jar.sh
bash scripts/run_spark_train.sh
python3 scripts/make_charts.py
```

**Warning:** the loader drops and recreates the project collections, including
predictions. Use a dedicated database. Training overwrites the predictions collection.

## Repository layout

| Path | Purpose |
|------|---------|
| [STEPS/](STEPS/) | Infrastructure and pipeline runbook |
| [scripts/](scripts/) | Data preparation, ingestion, analytics, training, and visualization |
| [queries/analytics.js](queries/analytics.js) | Interactive MongoDB operator examples |
| [docs/RESULTS.md](docs/RESULTS.md) | Observed results, interpretation, and limitations |
| [docs/figures/](docs/figures/) | Architecture and analytical figures |

Local configuration, source data, connector JARs, and runtime logs are ignored
by Git. Do not publish real host addresses, credentials, or environment snapshots.
