# MicroOS v1.0 Release Notes

**Minimal Linux. Maximum control.**

## Summary

MicroOS v1.0 is a real, bootable $x86\_64$ operating system engineered to fit strictly under 50 MB. It is delivered in two editions:
1. **MicroOS v1.0 Terminal Edition** (`release/microos.iso` — 12.77 MB)
2. **MicroOS v1.0 GUI Desktop Edition** (`release/microos-gui.iso` — 3.63 MB)

---

## Editions & Highlights

### 1. MicroOS GUI Desktop Edition (`release/microos-gui.iso` — 3.63 MB)
- **Graphical Desktop Environment**: Built-in X11/LXDE-style graphical user interface with mouse pointer and keyboard navigation.
- **Window Manager**: Draggable overlapping windows, title bars, and close controls.
- **Desktop Taskbar & Start Menu**: Bottom taskbar with Start Menu button, task switcher, system clock, and application launchers.
- **Built-in GUI Applications**:
  - **Micro OS Dashboard**: Live system monitor showing RAM allocation, CPU state, and uptime.
  - **Terminal (Bash)**: Interactive graphical terminal window.
  - **Snake Game (GUI)**: Real-time graphical snake arcade game with high-score tracking.
  - **File Manager**: Visual file browser.
  - **Boot Time Benchmark**: Performance profiling application.
  - **WiFi & Network Settings**: Graphical network status viewer.
- **Live Launch**: Run [`Start-MicroOS-GUI.bat`](../Start-MicroOS-GUI.bat) to launch the GUI desktop directly in Oracle VirtualBox.

### 2. MicroOS Terminal Edition (`release/microos.iso` — 12.77 MB)
- **Custom Linux 6.6.63 Kernel (x86_64)**: Intel and AMD SMP support, ACPI/APIC, PCI/PCIe, USB 2.0/3.0, AHCI/SATA, NVMe, ext4/FAT32/exFAT/NTFS3, modular Ethernet and laptop Wi-Fi drivers, and XZ-compressed firmware loading.
- **Hybrid BIOS + UEFI Boot**: Boots on legacy BIOS and modern UEFI systems via GRUB 2 + `xorriso` hybrid MBR/GPT layout.
- **Minimal BusyBox Init & Shell**: Fast boot straight into the `micro@micro:~$` terminal interface.
- **Native Networking**: Integrated `iwd`, `dbus`, `iproute2`, BusyBox `udhcpc`, and curated Intel/Realtek/MediaTek wireless firmware.
- **Persistent Debian APT/dpkg**: Boots cleanly in live mode without storage, and integrates Debian Bookworm glibc APT on persistent storage (`LABEL=MICROOS_PERSIST`).
- **Micro Arcade**: 8 offline playable C terminal games (`snake`, `tetris`, `pong`, `mines`, `2048`, `guess`, `tictactoe`, `spaceinvaders`).

---

## Checksums

```text
# Terminal Edition (12,769,280 bytes):
f072e24fbc9e64ce31fae7f495ac6f55104391fee57ddc455d48237fb5532ed1  microos.iso

# GUI Desktop Edition (3,638,272 bytes):
772008c5bdb5beb0e45adbd5547332d44a937bd7913ed3a4c5fbfe9eddb45fbc  microos-gui.iso
```
