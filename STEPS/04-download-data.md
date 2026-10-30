# Step 04 — Download UCI diabetes dataset

```bash
mkdir -p data
bash scripts/download_uci_diabetes.sh
```

Expected file: `data/diabetic_data.csv` (Diabetes 130-US hospitals).

### If `curl` fails on the cluster

1. On a machine with internet, download:
   - https://archive.ics.uci.edu/static/public/296/data.csv
2. Save as `data/diabetic_data.csv` on the driver VM (SCP, `rsync`, etc.).

Quick sanity check:

```bash
wc -l data/diabetic_data.csv
head -1 data/diabetic_data.csv
```

Proceed to [05-prepare-and-load.md](05-prepare-and-load.md).
