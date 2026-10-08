#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${TEST_BASE_URL:-http://localhost:8088}"
PROM_URL="${TEST_PROM_URL:-http://localhost:9090}"

wait_for_provider() {
  for i in {1..30}; do
    state="$(
      docker inspect \
        -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' \
        gr8-lab-session-provider 2>/dev/null || true
    )"

    if [ "$state" = "healthy" ]; then
      return 0
    fi

    sleep 2
  done

  echo "FAIL: session-provider did not become healthy"
  docker compose ps
  return 1
}

cleanup() {
  echo "Cleanup: ensuring session-provider is running..."
  docker compose start session-provider >/dev/null 2>&1 || true
}

trap cleanup EXIT


echo "1. Ensuring healthy baseline..."

docker compose start session-provider >/dev/null
wait_for_provider

status="$(
  curl -sS \
    -o /dev/null \
    -w '%{http_code}' \
    -X POST \
    "$BASE_URL/api/v1/session"
)"

test "$status" = "200"

echo "PASS: baseline returned HTTP 200"


echo "2. Stopping real upstream dependency..."

docker compose stop session-provider

echo "PASS: session-provider stopped"


echo "3. Generating customer-facing failures..."

for i in {1..8}; do
  status="$(
    curl -sS \
      -o /dev/null \
      -w '%{http_code}' \
      -X POST \
      "$BASE_URL/api/v1/session"
  )"

  echo "failure=$i status=$status"

  test "$status" = "503"

  sleep 1
done

echo "PASS: 8/8 requests returned HTTP 503"


echo "4. Validating upstream failure in application logs..."

docker compose logs --no-color api \
  > /tmp/inc002-api.log 2>&1

if ! grep 'upstream_connection_failure' /tmp/inc002-api.log >/dev/null; then
  echo "FAIL: upstream_connection_failure not found"
  tail -50 /tmp/inc002-api.log
  exit 1
fi

echo "PASS: upstream_connection_failure found in logs"


echo "5. Waiting for Prometheus HighAPI5xxRate alert..."

alert_found=false

for i in {1..15}; do

  curl -fsS \
    "$PROM_URL/api/v1/alerts" \
    > /tmp/inc002-alerts.json

  if python3 - <<'PY'
import json
import sys

with open("/tmp/inc002-alerts.json") as f:
    payload = json.load(f)

alerts = payload.get("data", {}).get("alerts", [])

found = any(
    alert.get("labels", {}).get("alertname") == "HighAPI5xxRate"
    and alert.get("state") == "firing"
    for alert in alerts
)

sys.exit(0 if found else 1)
PY
  then
    alert_found=true
    break
  fi

  sleep 2
done

if [ "$alert_found" != "true" ]; then
  echo "FAIL: HighAPI5xxRate did not enter FIRING state"
  cat /tmp/inc002-alerts.json
  exit 1
fi

echo "PASS: Prometheus HighAPI5xxRate is FIRING"


echo "6. Restoring upstream dependency..."

docker compose start session-provider

wait_for_provider

echo "PASS: session-provider healthy"


echo "7. Validating recovery..."

for i in {1..10}; do
  status="$(
    curl -sS \
      -o /dev/null \
      -w '%{http_code}' \
      -X POST \
      "$BASE_URL/api/v1/session"
  )"

  echo "recovery=$i status=$status"

  test "$status" = "200"
done

echo "PASS: 10/10 recovery requests returned HTTP 200"


trap - EXIT

echo
echo "PASS: INC002 real upstream outage and recovery validated"
