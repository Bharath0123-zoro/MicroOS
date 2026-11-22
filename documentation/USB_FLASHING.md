# MicroOS v1.0 USB Flashing & Native Boot Guide

`release/microos.iso` is a standard **hybrid BIOS + UEFI bootable ISO9660** image. It does **not** run an installer and **never** automatically formats or modifies your laptop's internal drive.

## 1. Verify ISO Integrity First

Compare the SHA256 checksum against `release/microos.iso.sha256`:

- **Windows (PowerShell):**
  ```powershell
  Get-FileHash release\microos.iso -Algorithm SHA256
  Get-Content release\microos.iso.sha256
  ```
- **Linux:**
  ```bash
  sha256sum -c release/microos.iso.sha256
  ```

## 2. Flashing Options

### Option A: Rufus (Windows)
1. Insert a USB flash drive (any size >= 128 MB; all data on the USB drive will be erased).
2. Open **Rufus**, select your USB device, and click **SELECT** to choose `release/microos.iso`.
3. Click **START**. When prompted, choose **Write in DD Image mode** (recommended for hybrid BIOS+UEFI compatibility) or **ISO Image mode**.

### Option B: balenaEtcher (Windows / macOS / Linux)
1. Open **balenaEtcher**.
2. Click **Flash from file** and pick `release/microos.iso`.
3. Select your target USB drive and click **Flash!**.

### Option C: Ventoy
1. Install Ventoy onto a USB drive.
2. Copy `release/microos.iso` directly onto the Ventoy data partition.
3. Boot the USB drive and select `microos.iso` from the Ventoy menu.

## 3. Booting on a Physical Laptop

1. Insert the flashed USB drive and reboot.
2. Enter your laptop's boot menu (commonly `F12`, `F11`, `F8`, `F2`, or `Esc`).
3. **Secure Boot**: MicroOS uses a custom unsigned Linux kernel; disable **Secure Boot** in UEFI settings if firmware refuses unsigned kernels.
4. Select the USB drive (UEFI or Legacy BIOS entry).
5. At the GRUB menu, press Enter on **MicroOS v1.0 (Standard Boot)**.

## 4. Optional Persistent Storage on SSD / External Drive

MicroOS boots cleanly into RAM without touching internal storage. To enable persistent files, Wi-Fi profiles, arcade high scores, and Debian `apt`/`dpkg`:
1. Create an `ext4` partition on an external SSD or dedicated partition labeled `MICROOS_PERSIST`.
2. Mount it manually via `mount /dev/<part> /mnt/ssd` or reboot to auto-attach `/persist`.
3. Extract a Debian Bookworm `amd64` minbase rootfs into `/persist/debian`, then verify with `apt status`.
