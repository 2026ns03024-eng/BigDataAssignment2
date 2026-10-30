#!/usr/bin/env python3
"""
Transform UCI Diabetes 130-US hospitals CSV into MongoDB-shaped JSONL:
patients, encounters (nested diagnoses), vitals (synthetic time series).
"""
import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_loader import load

SEED = 42
VITALS_PER_ENCOUNTER = 8


def main():
    cfg = load()
    csv_path = Path(cfg["DATA_CSV"])
    if not csv_path.exists():
        raise SystemExit("Missing CSV: {} — run STEPS/04-download-data.md".format(csv_path))

    random.seed(SEED)
    rng = random.Random(SEED)

    data_dir = csv_path.parent
    out_patients = data_dir / "patients.jsonl"
    out_encounters = data_dir / "encounters.jsonl"
    out_vitals = data_dir / "vitals.jsonl"

    print("Reading", csv_path)
    df = pd.read_csv(csv_path, na_values=["?", "NULL", ""], low_memory=False)
    df["encounter_id"] = df["encounter_id"].astype(int)
    df["patient_nbr"] = df["patient_nbr"].astype(int)

    # Patient-level documents (one per patient_nbr, first row demographics)
    patients = {}
    for _, row in df.drop_duplicates("patient_nbr").iterrows():
        pid = int(row["patient_nbr"])
        patients[pid] = {
            "patient_nbr": pid,
            "race": str(row.get("race", "")),
            "gender": str(row.get("gender", "")),
            "age": str(row.get("age", "")),
        }

    # Admission times and prev_encounter_id per patient timeline
    df = df.sort_values(["patient_nbr", "encounter_id"])
    base = datetime(1999, 1, 15)
    prev_map = {}
    admit_map = {}

    for pid, grp in df.groupby("patient_nbr"):
        prev = None
        t = base + timedelta(days=int(pid % 400))
        for eid in grp["encounter_id"]:
            eid = int(eid)
            admit_map[eid] = t
            prev_map[eid] = prev
            prev = eid
            los = int(grp.loc[grp["encounter_id"] == eid, "time_in_hospital"].iloc[0])
            t = t + timedelta(days=max(los, 1) + rng.randint(14, 120))

    def med_summary(row):
        active = []
        for c in df.columns:
            if c.startswith(("metformin", "repaglinide", "nateglinide", "chlorpropamide",
                              "glimepiride", "acetohexamide", "glipizide", "glyburide",
                              "tolbutamide", "pioglitazone", "rosiglitazone", "acarbose",
                              "miglitol", "troglitazone", "tolazamide", "examide", "citoglipton",
                              "insulin", "glyburide-metformin", "glipizide-metformin",
                              "glimepiride-pioglitazone", "metformin-rosiglitazone",
                              "metformin-pioglitazone")):
                val = str(row.get(c, ""))
                if val not in ("No", "?", "nan", ""):
                    active.append({"drug": c, "status": val})
        return active

    encounters = []
    vitals_lines = []

    for _, row in df.iterrows():
        eid = int(row["encounter_id"])
        pid = int(row["patient_nbr"])
        readmitted = str(row.get("readmitted", "NO"))
        positive = 1 if readmitted == "<30" else 0

        diagnoses = []
        for dcol in ("diag_1", "diag_2", "diag_3"):
            code = row.get(dcol)
            if pd.notna(code) and str(code).strip():
                diagnoses.append({"icd9": str(code).strip(), "rank": dcol})

        los = int(row.get("time_in_hospital", 1) or 1)
        note = (
            "Patient {} age {} admitted for {} days; "
            "primary diagnosis {}; A1C {}; insulin {}."
        ).format(
            pid,
            row.get("age", ""),
            los,
            diagnoses[0]["icd9"] if diagnoses else "unspecified",
            row.get("A1Cresult", "?"),
            row.get("insulin", "?"),
        )

        enc = {
            "encounter_id": eid,
            "patient_nbr": pid,
            "admission_ts": admit_map[eid].isoformat() + "Z",
            "prev_encounter_id": prev_map[eid],
            "time_in_hospital": los,
            "admission_type_id": int(row.get("admission_type_id", 0) or 0),
            "discharge_disposition_id": int(row.get("discharge_disposition_id", 0) or 0),
            "admission_source_id": int(row.get("admission_source_id", 0) or 0),
            "num_lab_procedures": int(row.get("num_lab_procedures", 0) or 0),
            "num_procedures": int(row.get("num_procedures", 0) or 0),
            "num_medications": int(row.get("num_medications", 0) or 0),
            "number_outpatient": int(row.get("number_outpatient", 0) or 0),
            "number_emergency": int(row.get("number_emergency", 0) or 0),
            "number_inpatient": int(row.get("number_inpatient", 0) or 0),
            "number_diagnoses": int(row.get("number_diagnoses", 0) or 0),
            "max_glu_serum": str(row.get("max_glu_serum", "?")),
            "A1Cresult": str(row.get("A1Cresult", "?")),
            "change": str(row.get("change", "No")),
            "diabetesMed": str(row.get("diabetesMed", "No")),
            "insulin": str(row.get("insulin", "No")),
            "diagnoses": diagnoses,
            "medications": med_summary(row),
            "clinical_note": note,
            "readmitted": readmitted,
            "label_readmit_30d": positive,
        }
        encounters.append(enc)

        admit = admit_map[eid]
        hr_base = 78 + (8 if positive else 0) + rng.gauss(0, 4)
        glu_base = 145 + (18 if positive else 0) + rng.gauss(0, 12)
        for i in range(VITALS_PER_ENCOUNTER):
            ts = admit + timedelta(hours=i * 3)
            hr = max(55, min(130, hr_base + rng.gauss(0, 3)))
            glu = max(70, min(350, glu_base + rng.gauss(0, 8)))
            vitals_lines.append(
                {
                    "encounter_id": eid,
                    "patient_nbr": pid,
                    "ts": ts.isoformat() + "Z",
                    "heart_rate_bpm": round(hr, 1),
                    "glucose_mg_dl": round(glu, 1),
                }
            )

    with out_patients.open("w", encoding="utf-8") as f:
        for doc in patients.values():
            f.write(json.dumps(doc) + "\n")

    with out_encounters.open("w", encoding="utf-8") as f:
        for doc in encounters:
            f.write(json.dumps(doc) + "\n")

    with out_vitals.open("w", encoding="utf-8") as f:
        for doc in vitals_lines:
            f.write(json.dumps(doc) + "\n")

    print("Wrote {} patients, {} encounters, {} vitals".format(
        len(patients), len(encounters), len(vitals_lines)
    ))
    print("Positive class (<30):", sum(1 for e in encounters if e["label_readmit_30d"] == 1))


if __name__ == "__main__":
    main()
