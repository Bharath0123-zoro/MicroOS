#!/usr/bin/env bash
set -euo pipefail

echo "[check-env] Verifying Linux x86_64 build host tools..."
MISSING=()
for tool in gcc make bc flex bison perl xz cpio tar curl grub-mkimage xorriso mformat mmd mcopy depmod strip; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        MISSING+=("$tool")
    fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "[check-env] Missing required build tools: ${MISSING[*]}"
    exit 1
fi

echo "[check-env] Architecture: $(uname -m)"
echo "[check-env] Kernel host : $(uname -sr)"
echo "[check-env] GCC         : $(gcc --version | head -n1)"
echo "[check-env] xorriso     : $(xorriso --version 2>&1 | head -n1)"
echo "[check-env] grub-mkimage: $(grub-mkimage --version | head -n1)"
echo "[check-env] All required build tools verified."
