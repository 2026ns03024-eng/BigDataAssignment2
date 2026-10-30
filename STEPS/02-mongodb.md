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

Then start the server (each lab session):

```bash
bash scripts/start_mongod.sh
```

Verify:

```bash
mongosh --host "${MONGO_HOST:-127.0.0.1}" --port "${MONGO_PORT:-27017}" --eval 'db.runCommand({ ping: 1 })'
```

**Note:** Bind address is set to the master hostname or `127.0.0.1` so Spark on workers can reach Mongo if your lab network allows it. If workers cannot reach the master’s Mongo port, ask your TA whether Mongo should run on a shared service host; update `MONGO_HOST` in `config.env` accordingly.

Proceed to [03-python-deps.md](03-python-deps.md).
