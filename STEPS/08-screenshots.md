# Step 08 — Screenshots and submission checklist

Collect evidence for the assignment report (Option A — Prayogshala). Export `report/REPORT.md` to PDF if your instructor requires PDF; embed images from `report/figures/` and cluster screenshots.

## Required captures

| # | Subject | Where |
|---|---------|--------|
| 1 | Prayogshala **3/3 nodes active** | Web UI |
| 2 | `mongosh` — collection counts or sample encounter | Step 05 |
| 3 | **`$lookup` / `$bucket` / `$graphLookup`** output | Step 06 (`queries/analytics.js` or analytics log) |
| 4 | **`spark-submit`** completion or Spark UI workers | Step 07 |
| 5 | At least **two figures** from `report/figures/` | After `make_charts.py` |

## Report completion

1. Fill **Name** and **BITS ID** on the cover in `report/REPORT.md`.
2. Paste **metrics** from `output/metrics.json` into Section 6 (Results).
3. Add screenshot filenames or paste images under Section 7.
4. Briefly note any cluster-specific issues (Mongo bind address, YARN queue, jar download).

## Optional push from laptop

After editing locally:

```bash
git add -A
git commit -m "Assignment 2 Track C healthcare readmission"
git push
```

On master: `git pull` and re-run only the steps that changed.
