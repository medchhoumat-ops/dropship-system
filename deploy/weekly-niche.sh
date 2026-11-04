#!/usr/bin/env bash
# Weekly niche scan for every market in config/settings.toml (run from cron).
# Usage: deploy/weekly-niche.sh ["pets,kitchen,home"]
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SEEDS="${1:-${DROPSHIP_SEEDS:-pets,kitchen,home,fitness}}"
IMAGE="${DROPSHIP_IMAGE:-dropship-system:latest}"
cd "$APP_DIR"

# markets = ["US", "UK"]  ->  US UK
MARKETS=$(python3 - <<'PY'
import tomllib
with open("config/settings.toml", "rb") as fh:
    print(" ".join(tomllib.load(fh).get("markets", ["US"])))
PY
)

for COUNTRY in $MARKETS; do
  echo "[$(date -Is)] niche scan ${COUNTRY} seeds=${SEEDS}"
  docker run --rm \
    --env-file "$APP_DIR/.env" \
    -v "$APP_DIR/data:/app/data" \
    -v "$APP_DIR/config:/app/config:ro" \
    "$IMAGE" niche --country "$COUNTRY" --seeds "$SEEDS"
done

# keep 90 days of cache/runs/reports
find "$APP_DIR/data/cache" -type f -mtime +90 -delete || true
find "$APP_DIR/data/runs" "$APP_DIR/data/reports" -type f -mtime +90 -delete || true
