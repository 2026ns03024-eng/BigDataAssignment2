# Step 07 — Spark MLlib training and write-back to MongoDB

Ensure `config.env` is loaded and workers can reach Mongo at `MONGO_HOST:MONGO_PORT`.

```bash
bash scripts/run_spark_train.sh 2>&1 | tee output/spark_train.log
```

Or directly:

```bash
set -a && source config.env && set +a
spark-submit \
  --master "$SPARK_MASTER" \
  --jars "$MONGO_SPARK_JAR" \
  scripts/train_readmission.py
```

After success:

- Collection `readmission.predictions` contains test-set scores.
- File `output/metrics.json` holds AUROC / AUPR / accuracy for Random Forest and GBT.

Verify Mongo:

```javascript
use readmission
db.predictions.countDocuments()
db.predictions.findOne()
```

**Screenshot (for report):** Spark driver log showing application finished, or Spark UI **Stages** view with tasks on worker nodes.

## Charts and report numbers

```bash
python3 scripts/make_charts.py
```

Copy metrics from `output/metrics.json` into the results table in [report/REPORT.md](../report/REPORT.md).

Proceed to [08-screenshots.md](08-screenshots.md).
