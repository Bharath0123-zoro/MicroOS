# MicroOS v1.0 Release Notes

**Minimal Linux. Maximum control.**

## Summary

MicroOS v1.0 is a real, bootable, terminal-only x86\_64 Linux operating system engineered to fit strictly under 50 MB (12769280 bytes / 12.77 MB).

## Highlights

- **Custom Linux 6.6.63 Kernel (x86\_64)**: Intel and AMD SMP support, ACPI/APIC, PCI/PCIe, USB 2.0/3.0, AHCI/SATA, NVMe, ext4/FAT32/exFAT/NTFS3, modular Ethernet and laptop Wi-Fi drivers, and XZ-compressed firmware loading.
- **Hybrid BIOS + UEFI Boot**: Boots on legacy BIOS and modern UEFI systems via GRUB 2 + `xorriso` hybrid MBR/GPT layout, ready for Oracle VirtualBox and USB flashing (Rufus, balenaEtcher, Ventoy).
- **Minimal BusyBox Init & Shell**: Fast boot straight into the `micro@micro:~$` terminal interface with `help`, `sysinfo`, `hardware`, `wifi`, `disks`, `mount`, `unmount`, `apt`, `arcade`, `reboot`, and `poweroff`.
- **Native Networking**: Integrated `iwd`, `dbus`, `iproute2`, BusyBox `udhcpc`, and curated Intel/Realtek/MediaTek wireless firmware.
- **Persistent Debian-Compatible APT/dpkg Architecture**: Boots cleanly in live mode without storage, and integrates a genuine Debian Bookworm glibc APT/dpkg environment on persistent storage (`LABEL=MICROOS_PERSIST`).
- **Built-In Micro Arcade**: 8 offline playable C terminal games (`snake`, `tetris`, `pong`, `mines`, `2048`, `guess`, `tictactoe`, `spaceinvaders`) plus the `arcade` launcher with persistent high-score support.

## Checksum

```text
f072e24fbc9e64ce31fae7f495ac6f55104391fee57ddc455d48237fb5532ed1  microos.iso
```
