# Step 02 — MongoDB on the master

MongoDB holds operational documents for Scenario 3. Spark reads/writes via the Mongo Spark connector in later steps.

## Option A — Lab already has MongoDB

You already saw **MongoDB 8.x** and **mongosh 2.9** on the cluster — use the lab service only. **Do not** run `install_mongo_user.sh` unless `mongod` is missing for your user.

```bash
which mongod mongosh
mongosh --eval 'db.runCommand({ ping: 1 })'
```

If ping succeeds, note the host/port in `config.env` and skip to Step 03.

## Option B — User-local MongoDB (no sudo)

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

Set `MONGO_HOST` to the master's private interface address so Spark workers can reach MongoDB. The start script binds only to that configured address; allow port 27017 through the firewall from the worker private IP only. If workers cannot reach the master's Mongo port, ask your TA whether Mongo should run on a shared service host; update `MONGO_HOST` in `config.env` accordingly.

Proceed to [03-python-deps.md](03-python-deps.md).
