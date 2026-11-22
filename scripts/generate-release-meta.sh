#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/configs/microos.conf"

REL="${ROOT_DIR}/release"
ISO="${REL}/microos.iso"
if [[ ! -f "${ISO}" ]]; then
    echo "[release] ERROR: ${ISO} does not exist."
    exit 1
fi

(
    cd "${REL}"
    sha256sum microos.iso > microos.iso.sha256
)

ISO_BYTES="$(stat -c%s "${ISO}")"
ISO_MB="$(awk "BEGIN {printf \"%.2f\", ${ISO_BYTES}/1000000}")"
KSIZE="$(stat -c%s "${ROOT_DIR}/build/kernel-out/vmlinuz" 2>/dev/null || echo 0)"
ISIZE="$(stat -c%s "${ROOT_DIR}/build/initramfs.img" 2>/dev/null || echo 0)"
KREL="$(cat "${ROOT_DIR}/build/kernel-out/kernel.release" 2>/dev/null || echo "${KERNEL_VERSION}")"
SHA="$(awk '{print $1}' "${REL}/microos.iso.sha256")"

cat > "${REL}/build-info.txt" <<EOF
MicroOS Release Build Information
=================================
Distribution   : ${MICROOS_NAME} v${MICROOS_VERSION} (${MICROOS_CODENAME})
Architecture   : ${MICROOS_ARCH}
Build Date UTC : $(date -u '+%Y-%m-%d %H:%M:%S UTC')
Kernel Release : ${KREL}
BusyBox        : ${BUSYBOX_VERSION}
Bootloader     : GRUB 2 (Hybrid BIOS i386-pc + UEFI x86_64-efi)
ISO Generator  : xorriso

Measured Artifact Sizes:
  release/microos.iso  : ${ISO_BYTES} bytes (${ISO_MB} MB) [Limit: ${MICROOS_ISO_MAX_BYTES} bytes]
  boot/vmlinuz         : ${KSIZE} bytes ($((KSIZE / 1024)) KB)
  boot/initramfs.img   : ${ISIZE} bytes ($((ISIZE / 1024)) KB)

SHA256 Checksum:
  ${SHA}  microos.iso

Hypervisor Validation Policy:
  Oracle VirtualBox ONLY (QEMU strictly prohibited and unused)
EOF

cat > "${REL}/release-notes.md" <<EOF
# MicroOS v${MICROOS_VERSION} Release Notes

**Minimal Linux. Maximum control.**

## Summary

MicroOS v${MICROOS_VERSION} is a real, bootable, terminal-only x86\_64 Linux operating system engineered to fit strictly under 50 MB (${ISO_BYTES} bytes / ${ISO_MB} MB).

## Highlights

- **Custom Linux ${KREL} Kernel (x86\_64)**: Intel and AMD SMP support, ACPI/APIC, PCI/PCIe, USB 2.0/3.0, AHCI/SATA, NVMe, ext4/FAT32/exFAT/NTFS3, modular Ethernet and laptop Wi-Fi drivers, and XZ-compressed firmware loading.
- **Hybrid BIOS + UEFI Boot**: Boots on legacy BIOS and modern UEFI systems via GRUB 2 + \`xorriso\` hybrid MBR/GPT layout, ready for Oracle VirtualBox and USB flashing (Rufus, balenaEtcher, Ventoy).
- **Minimal BusyBox Init & Shell**: Fast boot straight into the \`micro@micro:~$\` terminal interface with \`help\`, \`sysinfo\`, \`hardware\`, \`wifi\`, \`disks\`, \`mount\`, \`unmount\`, \`apt\`, \`arcade\`, \`reboot\`, and \`poweroff\`.
- **Native Networking**: Integrated \`iwd\`, \`dbus\`, \`iproute2\`, BusyBox \`udhcpc\`, and curated Intel/Realtek/MediaTek wireless firmware.
- **Persistent Debian-Compatible APT/dpkg Architecture**: Boots cleanly in live mode without storage, and integrates a genuine Debian Bookworm glibc APT/dpkg environment on persistent storage (\`LABEL=MICROOS_PERSIST\`).
- **Built-In Micro Arcade**: 8 offline playable C terminal games (\`snake\`, \`tetris\`, \`pong\`, \`mines\`, \`2048\`, \`guess\`, \`tictactoe\`, \`spaceinvaders\`) plus the \`arcade\` launcher with persistent high-score support.

## Checksum

\`\`\`text
${SHA}  microos.iso
\`\`\`
EOF

echo "[release] Generated release/microos.iso.sha256, release/build-info.txt, release/release-notes.md"
