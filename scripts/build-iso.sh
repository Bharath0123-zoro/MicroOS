#!/usr/bin/env bash
# MicroOS v1.0 Hybrid BIOS + UEFI Bootable ISO Generator
# Uses minimal GRUB i386-pc + x86_64-efi images and xorriso (zero locale/font bloat)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/configs/microos.conf"

ISO_STAGE="${ROOT_DIR}/build/iso-stage"
KOUT="${ROOT_DIR}/build/kernel-out"
INITRAMFS="${ROOT_DIR}/build/initramfs.img"
OUT_ISO="${ROOT_DIR}/release/microos.iso"

mkdir -p "${ROOT_DIR}/release"
rm -rf "${ISO_STAGE}"
mkdir -p "${ISO_STAGE}/boot/grub" "${ISO_STAGE}/EFI/BOOT"

# 1. Copy kernel, initramfs, and GRUB config (ensure LF line endings)
cp "${KOUT}/vmlinuz" "${ISO_STAGE}/boot/vmlinuz"
cp "${INITRAMFS}" "${ISO_STAGE}/boot/initramfs.img"
sed 's/\r$//' "${ROOT_DIR}/boot/grub.cfg" > "${ISO_STAGE}/boot/grub/grub.cfg"

# Detect GRUB platform directories
GRUB_BIOS_DIR="/usr/lib/grub/i386-pc"
GRUB_EFI_DIR="/usr/lib/grub/x86_64-efi"

if [[ ! -d "${GRUB_BIOS_DIR}" ]]; then
    echo "ERROR: Missing GRUB BIOS modules at ${GRUB_BIOS_DIR}"
    exit 1
fi
if [[ ! -d "${GRUB_EFI_DIR}" ]]; then
    echo "ERROR: Missing GRUB UEFI modules at ${GRUB_EFI_DIR}"
    exit 1
fi

# Embedded early config so GRUB locates the ISO root reliably on BIOS, UEFI, USB & VirtualBox
EARLY_CFG="${ROOT_DIR}/build/grub-early.cfg"
cat > "${EARLY_CFG}" <<'EOF'
search --no-floppy --file --set=root /boot/vmlinuz
set prefix=($root)/boot/grub
configfile ($root)/boot/grub/grub.cfg
EOF

# 2. Build compact BIOS El Torito boot image (i386-pc)
BIOS_CORE="${ROOT_DIR}/build/grub-bios-core.img"
BIOS_ELTORITO="${ISO_STAGE}/boot/grub/bios-eltorito.img"

echo "[iso] Building GRUB BIOS (i386-pc) El Torito boot image..."
grub-mkimage \
    -O i386-pc \
    -d "${GRUB_BIOS_DIR}" \
    -c "${EARLY_CFG}" \
    -p /boot/grub \
    -o "${BIOS_CORE}" \
    biosdisk iso9660 part_msdos part_gpt ext2 fat normal linux configfile search search_fs_file boot echo sleep test

cat "${GRUB_BIOS_DIR}/cdboot.img" "${BIOS_CORE}" > "${BIOS_ELTORITO}"

# 3. Build compact UEFI boot image (x86_64-efi) and FAT EFI System Partition image
EFI_BIN="${ISO_STAGE}/EFI/BOOT/BOOTX64.EFI"
EFI_IMG="${ISO_STAGE}/boot/grub/efi.img"

echo "[iso] Building GRUB UEFI (x86_64-efi) BOOTX64.EFI and FAT ESP image..."
grub-mkimage \
    -O x86_64-efi \
    -d "${GRUB_EFI_DIR}" \
    -c "${EARLY_CFG}" \
    -p /boot/grub \
    -o "${EFI_BIN}" \
    iso9660 part_gpt part_msdos ext2 fat normal linux configfile search search_fs_file boot echo sleep test efi_gop efi_uga all_video

# Create minimal 2880 KB FAT12/16 EFI System Partition image containing /EFI/BOOT/BOOTX64.EFI
dd if=/dev/zero of="${EFI_IMG}" bs=1024 count=2880 status=none
mkfs.vfat -F 12 -n "MICROOS_EFI" "${EFI_IMG}" >/dev/null 2>&1 || mformat -i "${EFI_IMG}" -f 2880 ::
mmd -i "${EFI_IMG}" ::/EFI ::/EFI/BOOT
mcopy -i "${EFI_IMG}" "${EFI_BIN}" ::/EFI/BOOT/BOOTX64.EFI

# 4. Generate hybrid BIOS + UEFI bootable ISO9660 image with xorriso
echo "[iso] Generating hybrid BIOS+UEFI bootable ISO via xorriso..."
XORRISO_HYBRID_ARGS=()
if [[ -f "${GRUB_BIOS_DIR}/boot_hybrid.img" ]]; then
    XORRISO_HYBRID_ARGS=(-G "${GRUB_BIOS_DIR}/boot_hybrid.img")
fi

xorriso -as mkisofs \
    -o "${OUT_ISO}" \
    -V "MICROOS_V1_0" \
    -r -J -l \
    "${XORRISO_HYBRID_ARGS[@]}" \
    -partition_offset 16 \
    -b boot/grub/bios-eltorito.img \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    --grub2-boot-info \
    -eltorito-alt-boot \
    -e boot/grub/efi.img \
    -no-emul-boot \
    -isohybrid-gpt-basdat \
    "${ISO_STAGE}"

ISO_SIZE="$(stat -c%s "${OUT_ISO}")"
echo "[iso] Generated ${OUT_ISO}: ${ISO_SIZE} bytes ($(awk "BEGIN {printf \"%.2f\", ${ISO_SIZE}/1000000}") MB)"
