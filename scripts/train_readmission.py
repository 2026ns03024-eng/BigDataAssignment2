#!/usr/bin/env python3
"""
Track C: Spark MLlib readmission model — read MongoDB, train RF/GBT, write predictions back.
Run via: bash scripts/run_spark_train.sh
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from config_loader import load, mongo_uri  # noqa: E402

from pyspark.ml.classification import (  # noqa: E402
    GBTClassifier,
    RandomForestClassifier,
)
from pyspark.ml.evaluation import BinaryClassificationEvaluator  # noqa: E402
from pyspark.ml.feature import StringIndexer, VectorAssembler  # noqa: E402
from pyspark.sql.types import DoubleType  # noqa: E402
from pyspark.sql import SparkSession  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402


def read_collection(spark, cfg, uri, name, spark24):
    reader = spark.read.format("mongodb")
    if spark24:
        coll_uri = "{}.{}".format(uri.rstrip("/"), name)
        return reader.option("spark.mongodb.input.uri", coll_uri).load()
    return (
        reader.option("spark.mongodb.read.connection.uri", uri)
        .option("database", cfg["MONGO_DB"])
        .option("collection", name)
        .load()
    )


def downsample_train(train_df, label_col="label", seed=42):
    pos = train_df.filter(F.col(label_col) == 1.0)
    neg = train_df.filter(F.col(label_col) == 0.0)
    n_pos = pos.count()
    n_neg = neg.count()
    if n_pos == 0 or n_neg == 0:
        return train_df
    fraction = min(1.0, (2.0 * n_pos) / float(n_neg))
    neg_sample = neg.sample(withReplacement=False, fraction=fraction, seed=seed)
    return pos.unionByName(neg_sample)


def eval_model(model, test_df, label_col="label"):
    pred = model.transform(test_df)
    evaluator_roc = BinaryClassificationEvaluator(
        labelCol=label_col, rawPredictionCol="rawPrediction", metricName="areaUnderROC"
    )
    evaluator_pr = BinaryClassificationEvaluator(
        labelCol=label_col, rawPredictionCol="rawPrediction", metricName="areaUnderPR"
    )
    auroc = evaluator_roc.evaluate(pred)
    aupr = evaluator_pr.evaluate(pred)
    positive_prediction = F.col("prediction") == 1.0
    negative_prediction = F.col("prediction") == 0.0
    positive_label = F.col(label_col) == 1.0
    negative_label = F.col(label_col) == 0.0
    counts = pred.agg(
        F.count(F.lit(1)).alias("total"),
        F.sum(F.when(positive_label, 1).otherwise(0)).alias("actual_positive"),
        F.sum(F.when(negative_label, 1).otherwise(0)).alias("actual_negative"),
        F.sum(F.when(positive_prediction & positive_label, 1).otherwise(0)).alias("tp"),
        F.sum(F.when(negative_prediction & negative_label, 1).otherwise(0)).alias("tn"),
        F.sum(F.when(positive_prediction & negative_label, 1).otherwise(0)).alias("fp"),
        F.sum(F.when(negative_prediction & positive_label, 1).otherwise(0)).alias("fn"),
    ).first()
    total = int(counts["total"])
    tp, tn, fp, fn = (int(counts[key] or 0) for key in ("tp", "tn", "fp", "fn"))
    actual_positive = int(counts["actual_positive"] or 0)
    actual_negative = int(counts["actual_negative"] or 0)
    acc = (tp + tn) / float(total) if total else 0.0
    precision = tp / float(tp + fp) if tp + fp else 0.0
    recall = tp / float(tp + fn) if tp + fn else 0.0
    specificity = tn / float(tn + fp) if tn + fp else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return {
        "auroc": round(auroc, 4),
        "aupr": round(aupr, 4),
        "accuracy": round(acc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "specificity": round(specificity, 4),
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "test_positive_rows": actual_positive,
        "test_negative_rows": actual_negative,
        "predictions_df": pred,
    }


def main():
    cfg = load()
    uri = mongo_uri(cfg)
    spark24 = cfg.get("USE_SPARK24_URI", "").strip() in ("1", "true", "yes")

    spark = (
        SparkSession.builder.appName("BDS_Assignment2_Readmission_TrackC")
        .config("spark.sql.execution.arrow.pyspark.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    numpy_versions = spark.sparkContext.parallelize([0], 1).map(
        lambda _: __import__("numpy").__version__
    ).collect()
    print("Executor NumPy:", numpy_versions[0])

    enc = read_collection(spark, cfg, uri, "encounters", spark24)
    pts = read_collection(spark, cfg, uri, "patients", spark24)
    base = enc.join(pts.select("patient_nbr", "gender", "age"), "patient_nbr", "left")
    base = base.withColumn("label", F.col("label_readmit_30d").cast("double"))
    base = base.persist()
    base.count()

    numeric = [
        "time_in_hospital",
        "num_lab_procedures",
        "num_procedures",
        "num_medications",
        "number_outpatient",
        "number_emergency",
        "number_inpatient",
        "number_diagnoses",
    ]
    categorical = ["gender", "age", "A1Cresult", "diabetesMed", "insulin"]

    for c in numeric:
        base = base.withColumn(c, F.coalesce(F.col(c).cast("double"), F.lit(0.0)))
    for c in categorical:
        base = base.withColumn(c, F.coalesce(F.col(c).cast("string"), F.lit("unknown")))

    indexed_cols = []
    stages_index = []
    for c in categorical:
        idx = c + "_idx"
        si = StringIndexer(inputCol=c, outputCol=idx, handleInvalid="keep")
        stages_index.append(si)
        indexed_cols.append(idx)

    assembler = VectorAssembler(
        inputCols=numeric + indexed_cols, outputCol="features", handleInvalid="keep"
    )

    test_patient = F.pmod(
        F.xxhash64(F.col("patient_nbr"), F.lit(42)), F.lit(5)
    ) == 0
    train_all = base.filter(~test_patient).persist()
    test = base.filter(test_patient).persist()
    train_patients = train_all.select("patient_nbr").distinct().count()
    test_patients = test.select("patient_nbr").distinct().count()
    overlapping_patients = (
        train_all.select("patient_nbr")
        .distinct()
        .intersect(test.select("patient_nbr").distinct())
        .limit(1)
        .count()
    )
    if overlapping_patients:
        raise RuntimeError("Patient-level split contains patient overlap")

    train = downsample_train(train_all).persist()
    train_rows = train.count()
    train_model_patients = train.select("patient_nbr").distinct().count()
    train_label_counts = {
        int(row["label"]): int(row["count"])
        for row in train.groupBy("label").count().collect()
    }
    test_rows = test.count()

    from pyspark.ml import Pipeline  # noqa: E402

    rf = RandomForestClassifier(
        labelCol="label", featuresCol="features", numTrees=80, seed=42
    )
    gbt = GBTClassifier(
        labelCol="label", featuresCol="features", maxIter=40, seed=42
    )

    prep = Pipeline(stages=stages_index + [assembler])
    prep_model = prep.fit(train)
    train_fe = prep_model.transform(train).persist()
    test_fe = prep_model.transform(test).persist()
    train_fe.count()
    test_fe.count()
    train.unpersist()
    train_all.unpersist()
    test.unpersist()
    base.unpersist()

    rf_model = rf.fit(train_fe)
    gbt_model = gbt.fit(train_fe)

    rf_metrics = eval_model(rf_model, test_fe)
    gbt_metrics = eval_model(gbt_model, test_fe)
    if any(
        sum(metrics["confusion"].values()) != test_rows
        for metrics in (rf_metrics, gbt_metrics)
    ):
        raise RuntimeError("Confusion matrix counts do not match the held-out test size")

    best_name = "gbt" if gbt_metrics["auroc"] >= rf_metrics["auroc"] else "random_forest"
    best = gbt_metrics if best_name == "gbt" else rf_metrics
    prob_udf = F.udf(lambda v: float(v[1]), DoubleType())
    pred_df = best["predictions_df"].select(
        "encounter_id",
        F.col("label").alias("label"),
        prob_udf("probability").alias("probability"),
        "prediction",
    ).withColumn("model", F.lit(best_name))

    write_uri = uri
    writer = pred_df.write.format("mongodb").mode("overwrite")
    if spark24:
        writer = writer.option(
            "spark.mongodb.output.uri", "{}.predictions".format(write_uri.rstrip("/"))
        )
    else:
        writer = (
            writer.option("spark.mongodb.write.connection.uri", write_uri)
            .option("database", cfg["MONGO_DB"])
            .option("collection", "predictions")
        )
    writer.save()

    out_dir = ROOT / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "random_forest": {
            k: rf_metrics[k]
            for k in (
                "auroc",
                "aupr",
                "accuracy",
                "precision",
                "recall",
                "f1",
                "specificity",
                "confusion",
            )
        },
        "gbt": {
            k: gbt_metrics[k]
            for k in (
                "auroc",
                "aupr",
                "accuracy",
                "precision",
                "recall",
                "f1",
                "specificity",
                "confusion",
            )
        },
        "best_model": best_name,
        "train_rows": train_rows,
        "test_rows": test_rows,
        "train_split_patients": train_patients,
        "train_model_patients": train_model_patients,
        "test_patients": test_patients,
        "train_label_counts": train_label_counts,
        "test_positive_rows": rf_metrics["test_positive_rows"],
        "test_negative_rows": rf_metrics["test_negative_rows"],
        "majority_baseline_accuracy": round(
            max(rf_metrics["test_positive_rows"], rf_metrics["test_negative_rows"])
            / float(test_rows),
            4,
        ),
        "split_method": "patient_hash_80_20_seed_42",
        "excluded_features": ["synthetic_vitals"],
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Random Forest:", metrics["random_forest"])
    print("GBT:", metrics["gbt"])
    print("Best model:", best_name)
    print("Wrote predictions to MongoDB and", out_dir / "metrics.json")

    spark.stop()


if __name__ == "__main__":
    main()
