# MicroOS v1.0 Troubleshooting Guide

## Boot Issues

- **UEFI Secure Boot blocks boot**: MicroOS v1.0 ships an unsigned custom kernel. Disable Secure Boot in your laptop's UEFI firmware settings.
- **Blank screen after GRUB**: Select **MicroOS v1.0 (Verbose / Diagnostic Boot)** in GRUB to inspect kernel boot output (`loglevel=7`).
- **Init failure / emergency recovery**: Select **MicroOS v1.0 (Emergency Shell)** in GRUB (appends `microos.emergency=1` to kernel cmdline) to drop directly into `/bin/sh` before `/sbin/init`.

## Networking & Wi-Fi

- **`wifi scan` reports no wireless interface in VirtualBox**: VirtualBox emulates wired Ethernet (`e1000` / `pcnet32`), not a physical Wi-Fi radio. Use `wifi status` to verify Ethernet or test Wi-Fi natively on a laptop.
- **Physical laptop Wi-Fi not showing up**:
  1. Run `hardware network` and `hardware pci` to identify the PCI vendor/device ID and bound driver.
  2. Run `dmesg | grep -iE 'firmware|iwlwifi|rtw|mt7921|ath'` to see if a specific firmware file is missing.
  3. Install additional vendor firmware packages via persistent Debian APT (`firmware-iwlwifi`, `firmware-realtek`, `firmware-misc-nonfree`) and copy the required `.ucode`/`.bin` files into `/lib/firmware`.
- **Static IP setup**: Run `wifi static <iface> <ip/prefix> [gateway] [dns]`.

## Storage & APT

- **`mount` refuses an unknown filesystem**: MicroOS refuses blind read-write mounts on unrecognized filesystems to protect user data. Inspect with `disks info /dev/<dev>`.
- **`apt` reports `PERSISTENT STORAGE REQUIRED`**: Base MicroOS boots in minimal live RAM mode to stay below 50 MB. Attach an ext4 partition labeled `MICROOS_PERSIST` containing `/persist/debian` (Debian Bookworm glibc rootfs) and verify with `apt status`.

## Micro Arcade

- **Small terminal window**: All 8 games query terminal dimensions (`TIOCGWINSZ`) and adapt playfield sizes gracefully. Minimum recommended terminal size is 60x20.
- **Stuck terminal state after abnormal kill**: Run `reset` or `stty sane`.
