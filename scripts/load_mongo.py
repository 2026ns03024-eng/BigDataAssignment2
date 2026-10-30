#!/usr/bin/env python3
"""Bulk load JSONL into MongoDB and create indexes."""
import json
import sys
from pathlib import Path

from pymongo import MongoClient, ASCENDING, DESCENDING

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_loader import load, mongo_uri


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def main():
    cfg = load()
    uri = mongo_uri(cfg)
    db_name = cfg["MONGO_DB"]
    data_dir = Path(cfg["DATA_CSV"]).parent

    client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    client.admin.command("ping")
    db = client[db_name]

    for coll in ("patients", "encounters", "vitals", "predictions"):
        db[coll].drop()

    batches = {
        "patients": data_dir / "patients.jsonl",
        "encounters": data_dir / "encounters.jsonl",
        "vitals": data_dir / "vitals.jsonl",
    }
    for name, path in batches.items():
        if not path.exists():
            raise SystemExit("Run prepare_documents.py first — missing {}".format(path))
        docs = list(load_jsonl(path))
        if docs:
            db[name].insert_many(docs, ordered=False)
        print("{}: {} documents".format(name, len(docs)))

    db.patients.create_index([("patient_nbr", ASCENDING)], unique=True)
    db.encounters.create_index([("encounter_id", ASCENDING)], unique=True)
    db.encounters.create_index([("patient_nbr", ASCENDING)])
    db.encounters.create_index([("readmitted", ASCENDING)])
    db.encounters.create_index([("prev_encounter_id", ASCENDING)])
    db.vitals.create_index([("encounter_id", ASCENDING), ("ts", ASCENDING)])
    db.vitals.create_index([("patient_nbr", ASCENDING)])

    print("Indexes created.")
    for name in ("patients", "encounters", "vitals"):
        print("  {} count = {}".format(name, db[name].count_documents({})))


if __name__ == "__main__":
    main()
