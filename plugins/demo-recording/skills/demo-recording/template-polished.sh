#!/bin/bash
#
# API Demo - Polished Template (with colors and animations)
#
set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8080/api/v1}"
CAST_FILE="${CAST_FILE:-demo.cast}"
CLEANUP="${CLEANUP:-false}"

# Colors
BOLD='\033[1m'
DIM='\033[2m'
CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
MAGENTA='\033[1;35m'
RED='\033[1;31m'
RESET='\033[0m'

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
  response=$(curl -s -w '\n%{http_code}' -X "${method}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    "${API_BASE}${path}" "$@")
  http_code=$(echo "${response}" | tail -1)
  body=$(echo "${response}" | sed '$d')
  if (( http_code >= 400 )); then
    echo -e "${RED}ERROR: HTTP ${http_code}${RESET}" >&2
    echo "${body}" | jq . 2>/dev/null || echo "${body}" >&2
    return 1
  fi
  echo "${body}"
}

type_cmd() {
  local cmd="$1"
  echo ""
  echo -ne "${GREEN}\$ ${RESET}"
  for (( i=0; i<${#cmd}; i++ )); do
    echo -n "${cmd:$i:1}"
    sleep 0.03
  done
  echo ""
  sleep 0.3
}

header() {
  echo ""
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${CYAN}  $*${RESET}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  sleep 1
}

info() {
  echo -e "  ${BLUE}ℹ${RESET} $*"
}

ok() {
  echo -e "  ${GREEN}✓${RESET} $*"
}

wait_for_state() {
  local url=$1 jq_filter=$2 desired_state=$3 timeout=${4:-300}
  local elapsed=0
  while true; do
    refresh_auth
    local state
    state=$(api GET "${url}" | jq -r "${jq_filter} // \"UNKNOWN\"")
    if [[ "${state}" == *"${desired_state}"* ]]; then
      ok "State: ${GREEN}${state}${RESET}"
      return 0
    fi
    if [[ "${state}" == *"FAILED"* ]]; then
      echo -e "  ${RED}✗ State: ${state}${RESET}" >&2
      return 1
    fi
    if (( elapsed >= timeout )); then
      echo -e "  ${RED}✗ Timed out (${timeout}s)${RESET}" >&2
      return 1
    fi
    echo -ne "  ${YELLOW}⏳${RESET} Waiting... ${DIM}${state} (${elapsed}s)${RESET}      \r"
    sleep 5
    elapsed=$((elapsed + 5))
  done
}

cleanup_resources() {
  header "Cleanup"
  for ((i=${#CREATED_RESOURCES[@]}-1; i>=0; i--)); do
    info "Deleting ${CREATED_RESOURCES[$i]}"
    api DELETE "/${CREATED_RESOURCES[$i]}" || true
  done
}

run_demo() {
  refresh_auth

  if [[ "${CLEANUP}" == "true" ]]; then
    trap 'rc=$?; cleanup_resources; exit $rc' EXIT INT TERM
  fi

  # TODO: Add your demo steps here
}

# Main
case "${1:-}" in
  --no-record)
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
