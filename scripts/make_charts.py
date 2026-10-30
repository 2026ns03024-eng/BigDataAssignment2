#!/usr/bin/env python3
"""Generate static charts for the assignment report (matplotlib Agg backend)."""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from pymongo import MongoClient  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_loader import load, mongo_uri  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "report" / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def bucket_los(days):
    if days < 4:
        return "1-3"
    if days < 8:
        return "4-7"
    if days < 12:
        return "8-11"
    if days < 16:
        return "12-15"
    return "16+"


def main():
    cfg = load()
    client = MongoClient(mongo_uri(cfg), serverSelectionTimeoutMS=15000)
    db = client[cfg["MONGO_DB"]]

    # 1) Class distribution
    labels = ["NO", ">30", "<30"]
    counts = [
        db.encounters.count_documents({"readmitted": x}) for x in labels
    ]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, counts, color=["#4C72B0", "#55A868", "#C44E52"])
    ax.set_title("Readmission label distribution (encounters)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(FIG / "fig1_readmission_counts.png", dpi=120)
    plt.close(fig)

    # 2) Readmission rate by age band
    pipe = [
        {
            "$group": {
                "_id": "$age",
                "n": {"$sum": 1},
                "pos": {"$sum": {"$cond": [{"$eq": ["$readmitted", "<30"]}, 1, 0]}},
            }
        },
        {"$match": {"n": {"$gte": 500}}},
        {"$sort": {"_id": 1}},
    ]
    rows = list(db.encounters.aggregate(pipe))
    ages = [r["_id"] for r in rows]
    rates = [r["pos"] / r["n"] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(len(ages)), rates, color="#8172B2")
    ax.set_xticks(range(len(ages)))
    ax.set_xticklabels(ages, rotation=45, ha="right")
    ax.set_ylabel("30-day readmission rate")
    ax.set_title("Readmission rate by age bracket (UCI encoding)")
    fig.tight_layout()
    fig.savefig(FIG / "fig2_readmission_by_age.png", dpi=120)
    plt.close(fig)

    # 3) LOS buckets
    los_pipe = [
        {
            "$project": {
                "los": "$time_in_hospital",
                "flag": {"$cond": [{"$eq": ["$readmitted", "<30"]}, 1, 0]},
            }
        }
    ]
    bucket_stats = {}
    for doc in db.encounters.aggregate(los_pipe):
        b = bucket_los(int(doc["los"]))
        bucket_stats.setdefault(b, {"n": 0, "pos": 0})
        bucket_stats[b]["n"] += 1
        bucket_stats[b]["pos"] += doc["flag"]
    order = ["1-3", "4-7", "8-11", "12-15", "16+"]
    brates = [
        bucket_stats[b]["pos"] / bucket_stats[b]["n"]
        for b in order
        if b in bucket_stats
    ]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(order[: len(brates)], brates, marker="o")
    ax.set_ylabel("Readmission rate (<30)")
    ax.set_xlabel("Length of stay (days)")
    ax.set_title("LOS bucket vs readmission rate")
    fig.tight_layout()
    fig.savefig(FIG / "fig3_los_readmission.png", dpi=120)
    plt.close(fig)

    # 4) Sample vitals time series
    sample = db.encounters.find_one({"readmitted": "<30"}, {"encounter_id": 1})
    if not sample:
        sample = db.encounters.find_one({}, {"encounter_id": 1})
    eid = sample["encounter_id"]
    vitals = list(
        db.vitals.find({"encounter_id": eid}).sort("ts", 1)
    )
    if vitals:
        xs = list(range(len(vitals)))
        hr = [v["heart_rate_bpm"] for v in vitals]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(xs, hr, marker="s", label="Heart rate (bpm)")
        ax.set_xlabel("Sample index (3h spacing)")
        ax.set_ylabel("bpm")
        ax.set_title("Vital signs for encounter {}".format(eid))
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG / "fig4_vitals_series.png", dpi=120)
        plt.close(fig)

    # 5) Model metrics comparison
    metrics_path = ROOT / "output" / "metrics.json"
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        names = ["Random Forest", "GBT"]
        keys = ["random_forest", "gbt"]
        auroc = [metrics[k]["auroc"] for k in keys]
        aupr = [metrics[k]["aupr"] for k in keys]
        x = range(len(names))
        width = 0.35
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar([i - width / 2 for i in x], auroc, width, label="AUROC")
        ax.bar([i + width / 2 for i in x], aupr, width, label="AUPR")
        ax.set_xticks(list(x))
        ax.set_xticklabels(names)
        ax.set_ylim(0, 1)
        ax.legend()
        ax.set_title("Spark MLlib test-set performance")
        fig.tight_layout()
        fig.savefig(FIG / "fig5_model_metrics.png", dpi=120)
        plt.close(fig)
    else:
        print("Skip fig5 — run Spark training first (output/metrics.json missing)")

    print("Figures written to", FIG)


if __name__ == "__main__":
    main()
