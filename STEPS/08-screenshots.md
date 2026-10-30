# Step 08 — Screenshots and submission checklist

Collect evidence for the assignment report. Export `report/REPORT.md` to PDF if required; embed images from `report/figures/`.

## Required captures

| # | Subject | When |
|---|---------|------|
| 1 | **Two-VM setup** — SSH hosts or diagram (VM1 driver, VM2 worker) | After cluster is wired |
| 2 | Spark master UI — worker(s) alive | After STEPS 01b |
| 3 | `mongosh` — counts or aggregation output | STEPS 05–06 |
| 4 | `spark-submit` / Spark UI stages on worker | STEPS 07 |
| 5 | Two+ figures from `report/figures/` | After `make_charts.py` |

## Report completion

1. Fill **Name** and **BITS ID** on the cover in `report/REPORT.md`.
2. Paste **metrics** from `output/metrics.json` into Section 6.
3. Note platform as **self-hosted VMs (Option B)** if not using BITS Prayogshala.

## Git sync

```bash
git add -A && git commit -m "..." && git push   # from laptop or VM
```

On driver VM: `git pull` before each session.
