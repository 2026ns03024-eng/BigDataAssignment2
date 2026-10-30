# Step 01 — Discover cluster layout

Run the discovery script from the repository root:

```bash
bash scripts/discover_cluster.sh | tee output/discover.log
```

Create `output/` if needed:

```bash
mkdir -p output
bash scripts/discover_cluster.sh | tee output/discover.log
```

## Configure `config.env`

```bash
cp config.example.env config.env
```

Edit `config.env` using the script output:

| Variable | What to set |
|----------|-------------|
| `MONGO_HOST` | Usually `127.0.0.1` if Mongo runs on master |
| `MONGO_PORT` | Default `27017` |
| `SPARK_MASTER` | `yarn` if `yarn node -list` works; else `spark://<master-hostname>:7077` from the script |
| `MONGO_SPARK_JAR` | Path printed by discover (Spark 3.x vs 2.4) |

Save the file, then verify Python can read it:

```bash
python3 -c "from scripts import config_loader; print(config_loader.load())"
```

If that import fails, use:

```bash
set -a && source config.env && set +a
echo $SPARK_MASTER
```

Proceed to [02-mongodb.md](02-mongodb.md).
