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
    tp = pred.filter((F.col("prediction") == 1.0) & (F.col(label_col) == 1.0)).count()
    tn = pred.filter((F.col("prediction") == 0.0) & (F.col(label_col) == 0.0)).count()
    fp = pred.filter((F.col("prediction") == 1.0) & (F.col(label_col) == 0.0)).count()
    fn = pred.filter((F.col("prediction") == 0.0) & (F.col(label_col) == 1.0)).count()
    total = pred.count()
    acc = (tp + tn) / float(total) if total else 0.0
    return {
        "auroc": round(auroc, 4),
        "aupr": round(aupr, 4),
        "accuracy": round(acc, 4),
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
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

    enc = read_collection(spark, cfg, uri, "encounters", spark24)
    pts = read_collection(spark, cfg, uri, "patients", spark24)
    vit = read_collection(spark, cfg, uri, "vitals", spark24).repartition(8)

    vital_stats = vit.groupBy("encounter_id").agg(
        F.avg("heart_rate_bpm").alias("hr_mean"),
        F.stddev("heart_rate_bpm").alias("hr_std"),
        F.min("heart_rate_bpm").alias("hr_min"),
        F.max("heart_rate_bpm").alias("hr_max"),
        F.avg("glucose_mg_dl").alias("glu_mean"),
        F.stddev("glucose_mg_dl").alias("glu_std"),
    )

    base = enc.join(pts.select("patient_nbr", "gender", "age"), "patient_nbr", "left")
    base = base.join(vital_stats, "encounter_id", "left")
    base = base.withColumn("label", F.col("label_readmit_30d").cast("double"))

    numeric = [
        "time_in_hospital",
        "num_lab_procedures",
        "num_procedures",
        "num_medications",
        "number_outpatient",
        "number_emergency",
        "number_inpatient",
        "number_diagnoses",
        "hr_mean",
        "hr_std",
        "hr_min",
        "hr_max",
        "glu_mean",
        "glu_std",
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

    train_all, test = base.randomSplit([0.8, 0.2], seed=42)
    train = downsample_train(train_all)

    from pyspark.ml import Pipeline  # noqa: E402

    rf = RandomForestClassifier(
        labelCol="label", featuresCol="features", numTrees=80, seed=42
    )
    gbt = GBTClassifier(
        labelCol="label", featuresCol="features", maxIter=40, seed=42
    )

    prep = Pipeline(stages=stages_index + [assembler])
    prep_model = prep.fit(train)
    train_fe = prep_model.transform(train)
    test_fe = prep_model.transform(test)

    rf_model = rf.fit(train_fe)
    gbt_model = gbt.fit(train_fe)

    rf_metrics = eval_model(rf_model, test_fe)
    gbt_metrics = eval_model(gbt_model, test_fe)

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
            k: rf_metrics[k] for k in ("auroc", "aupr", "accuracy", "confusion")
        },
        "gbt": {k: gbt_metrics[k] for k in ("auroc", "aupr", "accuracy", "confusion")},
        "best_model": best_name,
        "train_rows": train.count(),
        "test_rows": test.count(),
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
