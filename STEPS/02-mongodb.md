# Step 02 — MongoDB on the master

MongoDB holds patient and encounter documents. Spark reads/writes via the Mongo Spark connector in later steps.

## Use an existing MongoDB service

Check for an existing service before installing another instance. **Do not**
run `install_mongo_user.sh` unless you need a user-local installation.

```bash
which mongod mongosh
mongosh --eval 'db.runCommand({ ping: 1 })'
```

If ping succeeds, note the host/port in `config.env` and skip to Step 03.

## User-local MongoDB (no sudo)

Only if `mongod` is missing:

```bash
bash scripts/install_mongo_user.sh
```

The cluster helper adds the user-local MongoDB and mongosh binaries to `PATH` when present. Source it, then start the server:

```bash
source scripts/source_cluster_env.sh
bash scripts/start_mongod.sh
```

Verify:

```bash
mongosh --host "${MONGO_HOST:-127.0.0.1}" --port "${MONGO_PORT:-27017}" --eval 'db.runCommand({ ping: 1 })'
```

Set `MONGO_HOST` to the master's private interface address so Spark workers can reach MongoDB. The start script binds only to that configured address; allow port 27017 through the firewall from the worker private IP only. Verify connectivity from the worker before running training.

Proceed to [03-python-deps.md](03-python-deps.md).
