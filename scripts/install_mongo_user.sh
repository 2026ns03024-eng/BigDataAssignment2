#!/usr/bin/env bash
# Install MongoDB Community tarball under $HOME/mongo (no root).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MONGO_HOME="${MONGO_HOME:-$HOME/mongo}"
VERSION="${MONGO_VERSION:-7.0.14}"
OS="$(uname -s)"
ARCH="$(uname -m)"

if command -v mongod >/dev/null 2>&1; then
  echo "mongod already on PATH: $(command -v mongod)"
  exit 0
fi

mkdir -p "$MONGO_HOME"
cd "$MONGO_HOME"

if [[ "$OS" == "Linux" && "$ARCH" == "x86_64" ]]; then
  TGZ="mongodb-linux-x86_64-ubuntu2204-${VERSION}.tgz"
  URL="https://fastdl.mongodb.org/linux/${TGZ}"
elif [[ "$OS" == "Linux" && "$ARCH" == "aarch64" ]]; then
  TGZ="mongodb-linux-aarch64-ubuntu2204-${VERSION}.tgz"
  URL="https://fastdl.mongodb.org/linux/${TGZ}"
else
  echo "Unsupported OS/ARCH: $OS $ARCH — install MongoDB manually or use lab package."
  exit 1
fi

if [[ ! -d "mongodb-linux-"*"/bin" ]]; then
  echo "Downloading $URL ..."
  curl -fL -o "$TGZ" "$URL"
  tar xzf "$TGZ"
fi

BIN="$(find "$MONGO_HOME" -maxdepth 2 -type f -name mongod 2>/dev/null | head -1)"
if [[ -z "$BIN" ]]; then
  echo "mongod binary not found after extract."
  exit 1
fi
BINDIR="$(dirname "$BIN")"
echo ""
echo "Add to ~/.bashrc:"
echo "  export PATH=\"$BINDIR:\$PATH\""
echo "Then: source ~/.bashrc"
echo "Run: bash scripts/start_mongod.sh"
