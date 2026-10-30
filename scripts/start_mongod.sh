#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
set -a
# shellcheck disable=SC1091
[[ -f config.env ]] && source config.env
set +a

MONGO_HOST="${MONGO_HOST:-127.0.0.1}"
MONGO_PORT="${MONGO_PORT:-27017}"
DBPATH="${MONGO_DBPATH:-$HOME/mongo-data/db}"
LOGPATH="${MONGO_LOGPATH:-$HOME/mongo-data/mongod.log}"
PIDFILE="${MONGO_PIDFILE:-$HOME/mongo-data/mongod.pid}"

mkdir -p "$DBPATH" "$(dirname "$LOGPATH")"

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "mongod already running (pid $(cat "$PIDFILE"))"
  exit 0
fi

BIND="$MONGO_HOST"
if [[ "$BIND" == "127.0.0.1" ]]; then
  # Allow workers to connect when lab firewall permits
  BIND="0.0.0.0"
fi

mongod --dbpath "$DBPATH" --port "$MONGO_PORT" --bind_ip "$BIND" \
  --logpath "$LOGPATH" --fork --pidfilepath "$PIDFILE"

echo "mongod started on port $MONGO_PORT (bind $BIND)"
mongosh --host "$MONGO_HOST" --port "$MONGO_PORT" --eval 'db.runCommand({ ping: 1 })'
