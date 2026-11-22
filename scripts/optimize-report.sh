#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE="${ROOT_DIR}/build/rootfs-stage"
ISO="${ROOT_DIR}/release/microos.iso"

echo "=== MicroOS Size & Optimization Breakdown ($(date -u '+%Y-%m-%d %H:%M UTC')) ==="
[[ -f "${ROOT_DIR}/build/kernel-out/vmlinuz" ]] && echo "Kernel (vmlinuz)       : $(stat -c%s "${ROOT_DIR}/build/kernel-out/vmlinuz") bytes"
[[ -f "${ROOT_DIR}/build/initramfs.img" ]]      && echo "Initramfs (XZ)         : $(stat -c%s "${ROOT_DIR}/build/initramfs.img") bytes"
[[ -d "${STAGE}/lib/modules" ]]                 && echo "  - Modules (unpacked) : $(du -sb "${STAGE}/lib/modules" | awk '{print $1}') bytes"
[[ -d "${STAGE}/lib/firmware" ]]                && echo "  - Firmware (packed)  : $(du -sb "${STAGE}/lib/firmware" | awk '{print $1}') bytes"
[[ -f "${STAGE}/bin/busybox" ]]                 && echo "  - BusyBox (stripped) : $(stat -c%s "${STAGE}/bin/busybox") bytes"
[[ -d "${ROOT_DIR}/build/arcade-bin" ]]         && echo "  - Arcade (9 C bins)  : $(du -sb "${ROOT_DIR}/build/arcade-bin" | awk '{print $1}') bytes"
[[ -f "${ISO}" ]]                               && echo "Final ISO (microos.iso): $(stat -c%s "${ISO}") bytes"
