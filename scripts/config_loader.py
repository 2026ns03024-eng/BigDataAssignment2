"""Load config.env from repository root."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    cfg = {}
    env_path = ROOT / "config.env"
    if not env_path.exists():
        env_path = ROOT / "config.example.env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    for key in (
        "MONGO_HOST",
        "MONGO_PORT",
        "MONGO_DB",
        "SPARK_MASTER",
        "MONGO_SPARK_JAR",
        "DATA_CSV",
        "USE_SPARK24_URI",
    ):
        if key in os.environ:
            cfg[key] = os.environ[key]
    cfg.setdefault("MONGO_HOST", "127.0.0.1")
    cfg.setdefault("MONGO_PORT", "27017")
    cfg.setdefault("MONGO_DB", "readmission")
    cfg.setdefault("SPARK_MASTER", "yarn")
    cfg.setdefault("DATA_CSV", "data/diabetic_data.csv")
    jar = cfg.get("MONGO_SPARK_JAR", "")
    if jar and not os.path.isabs(jar):
        cfg["MONGO_SPARK_JAR"] = str(ROOT / jar)
    data_csv = cfg.get("DATA_CSV", "data/diabetic_data.csv")
    if not os.path.isabs(data_csv):
        cfg["DATA_CSV"] = str(ROOT / data_csv)
    return cfg


def mongo_uri(cfg=None):
    c = cfg or load()
    host = c["MONGO_HOST"]
    port = c["MONGO_PORT"]
    db = c["MONGO_DB"]
    return "mongodb://{host}:{port}/{db}".format(host=host, port=port, db=db)
