# Step 07 — Spark MLlib training and write-back to MongoDB

Ensure `config.env` is loaded and workers can reach Mongo at `MONGO_HOST:MONGO_PORT`.
Install NumPy for `python3` on every Spark node before training (on Rocky Linux:
`sudo dnf install -y python3-numpy`). The training job checks the executor's NumPy
availability before starting the feature and model stages.

The model reads encounters and patient demographics. It intentionally excludes
the synthetic vitals because their generation uses the readmission label; using
them as features would leak the target. Evaluation uses a deterministic
patient-level hash split so a patient's encounters cannot appear in both sets.

```bash
set -o pipefail
bash scripts/run_spark_train.sh 2>&1 | tee output/spark_train.log
```

Use the provided script rather than passing only the connector JAR directly: it adds the MongoDB Java driver/BSON runtime JARs required by the connector and fixes Spark's driver/block-manager ports for the private cluster firewall.

After success:

- Collection `readmission.predictions` contains test-set scores.
- File `output/metrics.json` holds AUROC, AUPR, accuracy, precision, recall,
  confusion matrices, and split counts for Random Forest and GBT.

Verify Mongo:

```javascript
use readmission
db.predictions.countDocuments()
db.predictions.findOne()
```

## Charts and results

```bash
python3 scripts/make_charts.py
```

Charts are written to `docs/figures/`. See [docs/RESULTS.md](../docs/RESULTS.md)
for the observed metrics and methodological limitations.

The Spark master UI normally listens on port 8080. The application UI normally
listens on port 4040 only while a job is running. Use the **Stages** and
**Executors** tabs to inspect task execution; do not expose these interfaces publicly.
