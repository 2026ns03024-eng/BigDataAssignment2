# Step 05 — Prepare documents and load MongoDB

## 1. Generate JSONL collections

```bash
python3 scripts/prepare_documents.py
```

Outputs under `data/`:

- `patients.jsonl`
- `encounters.jsonl`
- `vitals.jsonl`

## 2. Bulk load

```bash
python3 scripts/load_mongo.py
```

This drops and recreates collections in database `readmission`, creates indexes, and prints document counts.

Verify in `mongosh`:

```javascript
use readmission
db.encounters.countDocuments()
db.vitals.countDocuments()
db.patients.countDocuments()
```

**Screenshot (for report):** `mongosh` showing counts and one sample `encounters` document (redact if needed).

Proceed to [06-mongo-analytics.md](06-mongo-analytics.md).
