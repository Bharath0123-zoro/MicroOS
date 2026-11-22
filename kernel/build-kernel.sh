#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/configs/microos.conf"

SRC_DIR="${ROOT_DIR}/build/sources"
KBUILD_DIR="${ROOT_DIR}/build/linux-${KERNEL_VERSION}"
KOUT_DIR="${ROOT_DIR}/build/kernel-out"
MOD_DIR="${ROOT_DIR}/build/modules-out"

mkdir -p "${SRC_DIR}" "${KOUT_DIR}" "${MOD_DIR}"

TARBALL="${SRC_DIR}/linux-${KERNEL_VERSION}.tar.xz"
if [[ ! -f "${TARBALL}" ]]; then
    echo "[kernel] Downloading Linux ${KERNEL_VERSION}..."
    curl -fSL -o "${TARBALL}" "${KERNEL_URL}"
fi

if [[ ! -d "${KBUILD_DIR}" ]]; then
    echo "[kernel] Extracting Linux ${KERNEL_VERSION}..."
    tar -xf "${TARBALL}" -C "${ROOT_DIR}/build"
fi

cd "${KBUILD_DIR}"

echo "[kernel] Generating MicroOS x86_64 kernel configuration..."
make ARCH=x86_64 defconfig
./scripts/kconfig/merge_config.sh -m .config "${ROOT_DIR}/kernel/microos_x86_64.config"
make ARCH=x86_64 olddefconfig

# Save reproducible resolved kernel config
cp .config "${ROOT_DIR}/configs/kernel-resolved.config"

echo "[kernel] Compiling bzImage and modules with -j${JOBS}..."
make ARCH=x86_64 -j"${JOBS}" bzImage modules

KREL="$(make -s kernelrelease)"
echo "[kernel] Kernel release: ${KREL}"
echo "${KREL}" > "${KOUT_DIR}/kernel.release"

cp arch/x86/boot/bzImage "${KOUT_DIR}/vmlinuz"

rm -rf "${MOD_DIR}"
mkdir -p "${MOD_DIR}"
make ARCH=x86_64 INSTALL_MOD_PATH="${MOD_DIR}" INSTALL_MOD_STRIP=1 modules_install

# Remove build/source symlinks from module output
rm -f "${MOD_DIR}/lib/modules/${KREL}/build" "${MOD_DIR}/lib/modules/${KREL}/source"

# Ensure all modules are xz-compressed if not already
find "${MOD_DIR}/lib/modules/${KREL}" -type f -name '*.ko' -exec xz -f -9 {} +

# Rebuild module dependency maps
depmod -b "${MOD_DIR}" "${KREL}"

KSIZE="$(stat -c%s "${KOUT_DIR}/vmlinuz")"
MSIZE="$(du -sb "${MOD_DIR}/lib/modules" | awk '{print $1}')"
echo "[kernel] Built vmlinuz: ${KSIZE} bytes ($((KSIZE / 1024)) KB)"
echo "[kernel] Built modules: ${MSIZE} bytes ($((MSIZE / 1024)) KB)"
