#!/bin/bash
#
# API Demo - Simple Template
#
set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8080/api/v1}"
CAST_FILE="${CAST_FILE:-demo.cast}"
CLEANUP="${CLEANUP:-false}"

TOKEN=""
CREATED_RESOURCES=()

refresh_auth() {
  # Adapt to your auth mechanism:
  #   Bearer token:  TOKEN=$(curl -s -X POST "$AUTH_URL" -d '...' | jq -r '.token')
  #   kubectl:       TOKEN=$(kubectl create token -n "$NS" admin)
  #   Static key:    TOKEN="$API_KEY"
  TOKEN="${API_TOKEN:?Set API_TOKEN or edit refresh_auth()}"
}

api() {
  local method=$1 path=$2
  shift 2
  local response http_code body
  response=$(curl -sk -w '\n%{http_code}' -X "${method}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    "${API_BASE}${path}" "$@")
  http_code=$(echo "${response}" | tail -1)
  body=$(echo "${response}" | sed '$d')
  if (( http_code >= 400 )); then
    echo "ERROR: HTTP ${http_code}" >&2
    echo "${body}" | jq . 2>/dev/null || echo "${body}" >&2
    return 1
  fi
  echo "${body}"
}

wait_for_state() {
  local url=$1 jq_filter=$2 desired_state=$3 timeout=${4:-300}
  local elapsed=0
  while true; do
    refresh_auth
    local state
    state=$(api GET "${url}" | jq -r "${jq_filter} // \"UNKNOWN\"")
    if [[ "${state}" == *"${desired_state}"* ]]; then
      echo "State: ${state}"
      return 0
    fi
    if [[ "${state}" == *"FAILED"* ]]; then
      echo "State: ${state}" >&2
      return 1
    fi
    if (( elapsed >= timeout )); then
      echo "Timed out (${timeout}s)" >&2
      return 1
    fi
    echo -ne "Waiting... ${state} (${elapsed}s)\r"
    sleep 5
    elapsed=$((elapsed + 5))
  done
}

cleanup_resources() {
  for ((i=${#CREATED_RESOURCES[@]}-1; i>=0; i--)); do
    echo "Deleting ${CREATED_RESOURCES[$i]}"
    # Adapt deletion to your API/CLI
    api DELETE "/${CREATED_RESOURCES[$i]}" || true
  done
}

run_demo() {
  refresh_auth

  # TODO: Add your demo steps here
  # Example (API):
  #   result=$(api POST "/resources" -d '{"name":"demo"}')
  #   id=$(echo "$result" | jq -r '.id')
  #   CREATED_RESOURCES+=("resources/${id}")
  #   wait_for_state "/resources/${id}" '.status' 'ready'
  # Example (CLI):
  #   myctl create widget --name demo-widget
  #   CREATED_RESOURCES+=("widget/demo-widget")

  if [[ "${CLEANUP}" == "true" ]]; then
    cleanup_resources
  fi
}

# Main
case "${1:-}" in
  --dry-run)
    run_demo
    ;;
  --cleanup)
    CLEANUP=true
    asciinema rec --title "API Demo" -c "bash -c 'source $0 && run_demo'" "${CAST_FILE}"
    ;;
  *)
    asciinema rec --title "API Demo" -c "bash -c 'source $0 && run_demo'" "${CAST_FILE}"
    ;;
esac
