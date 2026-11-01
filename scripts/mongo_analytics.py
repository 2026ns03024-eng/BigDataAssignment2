#!/usr/bin/env python3
"""Run MongoDB aggregation pipelines (same as queries/analytics.js) and print summaries."""
import json
import sys
from pathlib import Path

from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_loader import load, mongo_uri


def run_lookup(db):
    pipe = [
        {"$lookup": {
            "from": "patients",
            "localField": "patient_nbr",
            "foreignField": "patient_nbr",
            "as": "patient",
        }},
        {"$unwind": "$patient"},
        {"$group": {
            "_id": {
                "$cond": [
                    {"$in": [
                        {"$toLower": {"$ifNull": ["$patient.race", ""]}},
                        ["", "nan", "?"],
                    ]},
                    "Unknown",
                    "$patient.race",
                ]
            },
            "encounters": {"$sum": 1},
            "readmit_30d": {
                "$sum": {"$cond": [{"$eq": ["$readmitted", "<30"]}, 1, 0]}
            },
        }},
        {"$addFields": {
            "readmit_rate": {"$divide": ["$readmit_30d", "$encounters"]},
        }},
        {"$sort": {"encounters": -1}},
    ]
    return list(db.encounters.aggregate(pipe, allowDiskUse=True))


def run_graph(db):
    pipe = [
        {"$match": {"prev_encounter_id": {"$ne": None}}},
        {"$sort": {"encounter_id": 1}},
        {"$limit": 500},
        {"$graphLookup": {
            "from": "encounters",
            "startWith": "$prev_encounter_id",
            "connectFromField": "prev_encounter_id",
            "connectToField": "encounter_id",
            "as": "prior_stays",
            "maxDepth": 5,
        }},
        {"$group": {
            "_id": None,
            "avg_prior_stays": {"$avg": {"$size": "$prior_stays"}},
            "max_prior_stays": {"$max": {"$size": "$prior_stays"}},
        }},
    ]
    return list(db.encounters.aggregate(pipe, allowDiskUse=True))


def run_window(db):
    sample = db.encounters.find_one(
        {}, {"encounter_id": 1}, sort=[("encounter_id", 1)]
    )
    if not sample:
        return []
    eid = sample["encounter_id"]
    pipe = [
        {"$match": {"encounter_id": eid}},
        {"$sort": {"ts": 1}},
        {"$setWindowFields": {
            "partitionBy": "$encounter_id",
            "sortBy": {"ts": 1},
            "output": {
                "rolling_hr_mean": {
                    "$avg": "$heart_rate_bpm",
                    "window": {"documents": [-2, 0]},
                },
            },
        }},
    ]
    return list(db.vitals.aggregate(pipe))


def run_bucket(db):
    pipe = [
        {"$addFields": {
            "readmit_flag": {"$cond": [{"$eq": ["$readmitted", "<30"]}, 1, 0]},
        }},
        {"$bucket": {
            "groupBy": "$time_in_hospital",
            "boundaries": [1, 4, 8, 12, 16],
            "default": "16+",
            "output": {
                "encounters": {"$sum": 1},
                "readmit_30d": {"$sum": "$readmit_flag"},
            },
        }},
        {"$addFields": {
            "readmit_rate": {
                "$round": [{"$divide": ["$readmit_30d", "$encounters"]}, 4],
            },
        }},
        {"$sort": {"_id": 1}},
    ]
    return list(db.encounters.aggregate(pipe, allowDiskUse=True))


def main():
    cfg = load()
    client = MongoClient(mongo_uri(cfg), serverSelectionTimeoutMS=15000)
    db = client[cfg["MONGO_DB"]]

    print("=== $lookup summary by race ===")
    print(json.dumps(run_lookup(db), indent=2, default=str))

    print("\n=== $graphLookup prior stay stats (500 sample) ===")
    print(json.dumps(run_graph(db), indent=2, default=str))

    print("\n=== $setWindowFields sample vitals ===")
    window_rows = run_window(db)
    print(json.dumps(window_rows[:3], indent=2, default=str))

    print("\n=== $bucket LOS readmission rate ===")
    print(json.dumps(run_bucket(db), indent=2, default=str))


if __name__ == "__main__":
    main()
