# Step 06 — MongoDB aggregation analytics

Run the Python driver for aggregation summaries:

```bash
python3 scripts/mongo_analytics.py | tee output/mongo_analytics.log
```

For interactive operator examples, use `mongosh`:

```bash
mongosh "mongodb://${MONGO_HOST}:${MONGO_PORT}/${MONGO_DB}" --file queries/analytics.js
```

Pipelines included:

1. **`$lookup`** — join patient demographics onto encounters  
2. **`$graphLookup`** — prior hospital stays along `prev_encounter_id`  
3. **`$setWindowFields`** — rolling mean heart rate within an encounter  
4. **`$bucket`** — length-of-stay buckets with readmission rate  

Proceed to [07-spark-training.md](07-spark-training.md).
