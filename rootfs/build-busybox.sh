#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/configs/microos.conf"

SRC_DIR="${ROOT_DIR}/build/sources"
BB_DIR="${ROOT_DIR}/build/busybox-${BUSYBOX_VERSION}"
BB_OUT="${ROOT_DIR}/build/busybox-out"

mkdir -p "${SRC_DIR}" "${BB_OUT}"

TARBALL="${SRC_DIR}/busybox-${BUSYBOX_VERSION}.tar.bz2"
if [[ ! -f "${TARBALL}" ]]; then
    echo "[busybox] Downloading BusyBox ${BUSYBOX_VERSION}..."
    curl -fSL -o "${TARBALL}" "${BUSYBOX_URL}"
fi

if [[ ! -d "${BB_DIR}" ]]; then
    echo "[busybox] Extracting BusyBox ${BUSYBOX_VERSION}..."
    tar -xf "${TARBALL}" -C "${ROOT_DIR}/build"
fi

cd "${BB_DIR}"
make defconfig

# Configure BusyBox cleanly for MicroOS (static binary, disable CONFIG_TC incompatible with Linux >= 6.8 headers)
sed -i 's/^# CONFIG_STATIC is not set/CONFIG_STATIC=y/' .config
sed -i 's/^CONFIG_TC=y/# CONFIG_TC is not set/' .config
# Disable SHA1/SHA256 HW accel flags that can fail on older/musl toolchains
sed -i 's/^CONFIG_SHA1_HWACCEL=y/# CONFIG_SHA1_HWACCEL is not set/' .config
sed -i 's/^CONFIG_SHA256_HWACCEL=y/# CONFIG_SHA256_HWACCEL is not set/' .config
# Ensure core utilities are enabled
for opt in CONFIG_ASH CONFIG_INIT CONFIG_MDEV CONFIG_UDHCPC CONFIG_BLKID CONFIG_FDISK CONFIG_MOUNT CONFIG_UMOUNT CONFIG_MODPROBE CONFIG_INSMOD CONFIG_LSMOD CONFIG_POWEROFF CONFIG_REBOOT CONFIG_CHROOT CONFIG_GETTY CONFIG_STTY CONFIG_PIDOF CONFIG_KILLALL CONFIG_FEATURE_BLKID_TYPE; do
    if grep -q "^# ${opt} is not set" .config; then
        sed -i "s/^# ${opt} is not set/${opt}=y/" .config
    elif ! grep -q "^${opt}=y" .config; then
        echo "${opt}=y" >> .config
    fi
done

make oldconfig </dev/null >/dev/null || true
cp .config "${ROOT_DIR}/configs/busybox-resolved.config"

echo "[busybox] Compiling static BusyBox with -j${JOBS}..."
make -j"${JOBS}"
make CONFIG_PREFIX="${BB_OUT}" install
strip --strip-all "${BB_OUT}/bin/busybox" 2>/dev/null || true

BBSIZE="$(stat -c%s "${BB_OUT}/bin/busybox")"
echo "[busybox] Built static busybox: ${BBSIZE} bytes ($((BBSIZE / 1024)) KB)"
