#!/usr/bin/env bash
set -euo pipefail

# ── Deploy Monitoring Susenas ──────────────────────────────────────
# Prerequisites:
#   1. Docker & Docker Compose installed
#   2. Prefect server + PostgreSQL already running (separate docker-compose)
#   3. .env file configured
#   4. sso_auth wheel copied to vendor/

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== 1. Checking prerequisites ==="

if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Copy .env.example and fill in credentials:"
    echo "  cp .env.example .env"
    exit 1
fi

if [ ! -d vendor ] || [ -z "$(ls vendor/*.whl 2>/dev/null)" ]; then
    echo "ERROR: No .whl file found in vendor/. Copy sso_auth wheel:"
    echo "  mkdir -p vendor && cp /path/to/sso_auth-0.1.1-py3-none-any.whl vendor/"
    exit 1
fi

# Source .env
set -a; source .env; set +a

echo "=== 2. Building Docker image ==="
docker build -t monitoring-susenas:latest .

echo "=== 3. Initializing database table ==="
docker run --rm \
    --network datahub_prefect-network \
    -e POSTGRES_USER="${POSTGRES_USER}" \
    -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    -e POSTGRES_HOST=postgres \
    -e POSTGRES_PORT=5432 \
    -e POSTGRES_DB="${POSTGRES_DB}" \
    monitoring-susenas:latest \
    python -c "from src.database import init_db; init_db(); print('Table created.')"

echo "=== 4. Deploying Prefect flow ==="
docker run --rm \
    --network datahub_prefect-network \
    -e PREFECT_API_URL=http://prefect-server:4200/api \
    -e SSO_USERNAME="${SSO_USERNAME}" \
    -e SSO_PASSWORD="${SSO_PASSWORD}" \
    -e POSTGRES_USER="${POSTGRES_USER}" \
    -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    -e POSTGRES_HOST=postgres \
    -e POSTGRES_PORT=5432 \
    -e POSTGRES_DB="${POSTGRES_DB}" \
    -e PREFECT_WORK_POOL_NAME="${PREFECT_WORK_POOL_NAME:-default-worker-pool}" \
    -v "${SCRIPT_DIR}/prefect.yaml:/app/prefect.yaml" \
    monitoring-susenas:latest \
    prefect deploy --all

echo "=== 5. Starting Streamlit dashboard ==="
docker compose up -d streamlit

echo ""
echo "=== Deployment complete! ==="
echo "  - Database:     PostgreSQL (shared with Prefect)"
echo "  - Prefect flow: deployed with cron '0 8 * * *' (Asia/Makassar)"
echo "  - Streamlit:    http://localhost:${STREAMLIT_PORT:-8501}"
echo ""
echo "To trigger a manual run:"
echo "  docker run --rm --network datahub_prefect-network \\"
echo "    -e POSTGRES_USER=${POSTGRES_USER} \\"
echo "    -e POSTGRES_PASSWORD=*** \\"
echo "    -e POSTGRES_HOST=postgres \\"
echo "    -e POSTGRES_DB=${POSTGRES_DB} \\"
echo "    -e SSO_USERNAME=*** \\"
echo "    -e SSO_PASSWORD=*** \\"
echo "    monitoring-susenas:latest"
