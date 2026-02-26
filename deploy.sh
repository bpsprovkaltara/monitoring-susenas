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

echo "=== 4. Ensuring work pool exists ==="
docker run --rm \
    --network datahub_prefect-network \
    -e PREFECT_API_URL=http://prefect-server:4200/api \
    monitoring-susenas:latest \
    prefect work-pool create "${PREFECT_WORK_POOL_NAME:-default-worker-pool}" \
        --type docker 2>/dev/null || echo "  Work pool already exists, skipping."

echo "=== 4a. Configuring work pool defaults ==="
docker run --rm \
    --network datahub_prefect-network \
    -e PREFECT_API_URL=http://prefect-server:4200/api \
    monitoring-susenas:latest \
    python -c "
import httpx, json
api = 'http://prefect-server:4200/api'
pool_name = '${PREFECT_WORK_POOL_NAME:-default-worker-pool}'
r = httpx.get(f'{api}/work_pools/{pool_name}')
r.raise_for_status()
pool = r.json()
template = pool.get('base_job_template', {})

# Set image_pull_policy default to Never
variables = template.get('variables', {})
props = variables.get('properties', {})
if 'image_pull_policy' in props:
    props['image_pull_policy']['default'] = 'Never'
    print('  image_pull_policy set to Never')

# Set dns in job_configuration to enable external DNS resolution
job_config = template.get('job_configuration', {})
job_config.setdefault('dns', ['8.8.8.8', '8.8.4.4'])
template['job_configuration'] = job_config
print('  dns set to [8.8.8.8, 8.8.4.4]')

r2 = httpx.patch(f'{api}/work_pools/{pool_name}', json={'base_job_template': template})
r2.raise_for_status()
print('  Work pool configured successfully')
"

echo "=== 5. Deploying Prefect flow ==="
WORK_POOL_NAME="${PREFECT_WORK_POOL_NAME:-default-worker-pool}"
envsubst '${PREFECT_WORK_POOL_NAME} ${SSO_USERNAME} ${SSO_PASSWORD} ${POSTGRES_USER} ${POSTGRES_PASSWORD} ${POSTGRES_DB}' \
    < "${SCRIPT_DIR}/prefect.yaml" > "${SCRIPT_DIR}/prefect.rendered.yaml"
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
    -e PREFECT_WORK_POOL_NAME="${WORK_POOL_NAME}" \
    -v "${SCRIPT_DIR}/prefect.rendered.yaml:/app/prefect.yaml" \
    monitoring-susenas:latest \
    prefect deploy --all
rm -f "${SCRIPT_DIR}/prefect.rendered.yaml"

echo "=== 6. Starting Streamlit dashboard ==="
docker compose up -d streamlit

echo ""
echo "=== 7. Deployment complete! ==="
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
