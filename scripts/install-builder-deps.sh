#!/usr/bin/env bash
set -euo pipefail

echo "[builder-deps] Installing Linux kernel, BusyBox, GRUB, xorriso, networking, and Debian bootstrap dependencies..."
apk add --no-cache \
    build-base \
    musl-dev \
    linux-headers \
    bc \
    flex \
    bison \
    perl \
    openssl-dev \
    elfutils-dev \
    findutils \
    diffutils \
    patch \
    ncurses-dev \
    xz \
    cpio \
    tar \
    gzip \
    bzip2 \
    kmod \
    grub \
    grub-bios \
    grub-efi \
    xorriso \
    mtools \
    dosfstools \
    iwd \
    dbus \
    iproute2 \
    blkid \
    e2fsprogs \
    debootstrap \
    dpkg \
    gnupg \
    python3

echo "[builder-deps] Installing curated laptop Wi-Fi & Ethernet firmware packages..."
# Install available Alpine split firmware packages for Intel, Realtek, MediaTek
for fw_pkg in linux-firmware-intel linux-firmware-iwlwifi linux-firmware-rtw88 linux-firmware-rtl_nic linux-firmware-mediatek; do
    if apk info "$fw_pkg" >/dev/null 2>&1; then
        apk add --no-cache "$fw_pkg" || true
    fi
done

echo "[builder-deps] Installed firmware directories:"
ls -la /lib/firmware 2>/dev/null | head -n 40 || true
echo "[builder-deps] All build dependencies ready."
