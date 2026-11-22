#!/usr/bin/env bash
# Build an external persistent ext4 disk image (LABEL=MICROOS_PERSIST)
# containing a genuine Debian Bookworm amd64 glibc + APT + dpkg rootfs.
# Stored externally on persistent storage (SSD / VirtualBox VDI), NEVER inside the 50 MB ISO.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/configs/microos.conf"

OUT_IMG="${1:-${ROOT_DIR}/build/microos-persist.img}"
SIZE_MB="${2:-1024}"
WORK_MNT="${ROOT_DIR}/build/persist-mnt"

if [[ $EUID -ne 0 ]]; then
    echo "Please run as root (needed for debootstrap & loop mount)."
    exit 1
fi

echo "[persist-img] Creating ${SIZE_MB} MB ext4 persistent image at ${OUT_IMG}..."
rm -f "${OUT_IMG}"
truncate -s "${SIZE_MB}M" "${OUT_IMG}"
mkfs.ext4 -F -L MICROOS_PERSIST "${OUT_IMG}"

mkdir -p "${WORK_MNT}"
mount -o loop "${OUT_IMG}" "${WORK_MNT}"
trap 'umount -R "${WORK_MNT}" 2>/dev/null || true' EXIT

mkdir -p "${WORK_MNT}/debian" "${WORK_MNT}/arcade" "${WORK_MNT}/etc/iwd" "${WORK_MNT}/home" "${WORK_MNT}/config"
chmod 0700 "${WORK_MNT}/etc/iwd"

echo "[persist-img] Bootstrapping Debian ${DEBIAN_RELEASE} (${DEBIAN_ARCH}) minimal glibc + apt + dpkg..."
debootstrap --variant=minbase --arch="${DEBIAN_ARCH}" \
    --include=apt,dpkg,debian-archive-keyring,ca-certificates,gpgv \
    "${DEBIAN_RELEASE}" "${WORK_MNT}/debian" "${DEBIAN_MIRROR}"

cat > "${WORK_MNT}/debian/etc/apt/sources.list" <<EOF
deb ${DEBIAN_MIRROR} ${DEBIAN_RELEASE} main contrib non-free non-free-firmware
deb ${DEBIAN_MIRROR} ${DEBIAN_RELEASE}-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security ${DEBIAN_RELEASE}-security main contrib non-free non-free-firmware
EOF

chroot "${WORK_MNT}/debian" apt-get clean
sync
umount -R "${WORK_MNT}"
trap - EXIT

echo "[persist-img] Successfully built ${OUT_IMG} (LABEL=MICROOS_PERSIST)."
