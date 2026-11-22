#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/configs/microos.conf"

ISO_FILE="${1:-${ROOT_DIR}/release/microos.iso}"
if [[ ! -f "${ISO_FILE}" ]]; then
    echo "[size-check] ERROR: ISO file not found: ${ISO_FILE}"
    exit 1
fi

ACTUAL_BYTES="$(stat -c%s "${ISO_FILE}")"
ACTUAL_MB="$(awk "BEGIN {printf \"%.2f\", ${ACTUAL_BYTES}/1000000}")"
ACTUAL_MIB="$(awk "BEGIN {printf \"%.2f\", ${ACTUAL_BYTES}/1048576}")"
LIMIT_BYTES="${MICROOS_ISO_MAX_BYTES}"
HEADROOM="$((LIMIT_BYTES - ACTUAL_BYTES))"

echo "=================================================="
echo "MicroOS v${MICROOS_VERSION} ISO SIZE VERIFICATION"
echo "=================================================="
echo "  ISO Path     : ${ISO_FILE}"
echo "  Actual Size  : ${ACTUAL_BYTES} bytes (${ACTUAL_MB} MB / ${ACTUAL_MIB} MiB)"
echo "  Hard Ceiling : ${LIMIT_BYTES} bytes (50.00 MB)"
if [[ "${ACTUAL_BYTES}" -le "${LIMIT_BYTES}" ]]; then
    echo "  Headroom     : +${HEADROOM} bytes ($(awk "BEGIN {printf \"%.2f\", ${HEADROOM}/1000000}") MB under limit)"
    echo "  Result       : PASS"
    echo "=================================================="
    exit 0
else
    OVER="$((ACTUAL_BYTES - LIMIT_BYTES))"
    echo "  Overflow     : -${OVER} bytes OVER LIMIT"
    echo "  Result       : FAIL (EXCEEDS 50 MB HARD CAP)"
    echo "=================================================="
    exit 1
fi
