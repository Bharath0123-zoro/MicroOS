# MicroOS v1.0

**Minimal Linux. Maximum control.**

MicroOS is a real, bootable, ultra-lightweight x86_64 terminal-only Linux operating system engineered to fit inside a **50 MB (50,000,000 bytes) hard ISO ceiling** while providing:

- **Custom x86_64 Linux 6.6 LTS Kernel** — Intel & AMD CPU support, ACPI/APIC, PCI/PCIe, USB 2.0/3.0, AHCI/SATA, NVMe, ext4/FAT/exFAT/NTFS3, modular Ethernet and Wi-Fi drivers, and compressed firmware loading.
- **Hybrid BIOS + UEFI Bootloader (GRUB 2)** — boots natively on physical laptops (USB flash via Rufus, balenaEtcher, Ventoy) and Oracle VirtualBox (1024 MB RAM, 1 CPU).
- **Minimal BusyBox Init & Shell** — fast boot to the custom `micro@micro:~$` CLI with zero desktop/GUI overhead.
- **Automatic Hardware Discovery (`hardware`)** — reads live kernel interfaces (`sysfs`, `procfs`, PCI/USB/block/net subsystems) without fabricating device data.
- **Native Linux Networking & Wi-Fi (`wifi`)** — `iwd`, `dbus`, `iproute2`, BusyBox `udhcpc`, DNS resolver, secure credential storage, and curated laptop wireless drivers/firmware.
- **Safe Storage & Persistent Environment (`disks`, `mount`, `unmount`)** — supports internal/external SATA, NVMe, and USB drives without automatic formatting.
- **Debian-Compatible `apt` / `dpkg` Architecture** — runs genuine Debian Bookworm glibc userspace on persistent storage while keeping the base ISO lean and independently bootable in live mode.
- **Built-In Micro Arcade (`arcade`)** — 8 playable offline C terminal games (`snake`, `tetris`, `pong`, `mines`, `2048`, `guess`, `tictactoe`, `spaceinvaders`) with persistent high-score support.

## Directory Layout

```text
MicroOS/
├── boot/             # GRUB configuration (BIOS & UEFI)
├── kernel/           # Custom Linux x86_64 kernel config & build script
├── rootfs/           # BusyBox config, rootfs overlay & initramfs builder
├── init/             # /init, BusyBox rcS/rcK scripts & emergency shell
├── networking/       # Native wifi CLI, iwd/dbus/udhcpc configuration
├── hardware/         # Live sysfs/procfs hardware discovery utility
├── storage/          # Safe disk inspection, mount/unmount & persistence setup
├── package-manager/  # Debian-compatible glibc APT/dpkg wrapper & bootstrapper
├── shell/            # MicroOS CLI profile, help system & sysinfo
├── arcade/           # Micro Arcade launcher & persistent score library (C)
├── games/            # 8 standalone C terminal arcade games
├── scripts/          # Build, ISO generation, size verification & optimization scripts
├── configs/          # Pinned versions, module & firmware manifests
├── tests/            # Automated Oracle VirtualBox BIOS/UEFI/offline/network tests
├── documentation/    # Architecture, build, hardware, testing, USB & troubleshooting docs
├── build/            # Intermediate build outputs & progress.json
├── logs/             # Build, test, and optimization logs
├── release/          # microos.iso, microos.iso.sha256, build-info.txt, release-notes.md
├── Makefile
└── README.md
```

## Quick Build (Linux x86_64 Build Host)

```bash
make all
```

See [documentation/BUILD.md](documentation/BUILD.md) for full build prerequisites and [documentation/USB_FLASHING.md](documentation/USB_FLASHING.md) for flashing `release/microos.iso` to a USB drive.
