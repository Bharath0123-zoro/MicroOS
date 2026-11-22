# MicroOS v1.0 System Architecture

## 1. Design Philosophy

MicroOS is a terminal-only x86_64 Linux operating system engineered around four strict invariants:

1. **Hard 50 MB ISO Ceiling (`<= 50,000,000 bytes`)**: Achieved via XZ-compressed Linux kernel (`CONFIG_KERNEL_XZ`), size-optimized kernel (`CONFIG_CC_OPTIMIZE_FOR_SIZE`), stripped static BusyBox, stripped minimal GRUB BIOS+UEFI images (zero locale/font bloat), pure-C ANSI terminal games (zero ncurses/SDL), and XZ-compressed initramfs (`--check=crc32`).
2. **Modular Hardware Driver Strategy**: Core storage (AHCI/SATA, IDE/PIIX, NVMe, USB 2.0/3.0, SCSI), partition tables (GPT/MBR), filesystems (ext4, FAT32, exFAT, NTFS3, ISO9660), input, and lightweight framebuffer consoles (VGA/VESA/EFI GOP) are built into the kernel for rock-solid boot across laptops and VirtualBox; Ethernet and Wi-Fi drivers are built as XZ-compressed loadable modules (`.ko.xz`) auto-loaded via PCI/USB `modalias` during `/etc/init.d/rcS`.
3. **Clean Separation of Live Boot vs. Persistent Debian APT/dpkg**:
   - The base initramfs boots completely independently into RAM (minimal BusyBox + native networking + hardware/storage tools + Micro Arcade).
   - Full Debian Bookworm (`amd64`) **glibc + `apt` + `dpkg` + GPG keyring** resides externally on persistent storage (`LABEL=MICROOS_PERSIST` -> `/persist/debian` or `/mnt/ssd/debian`).
   - `/usr/local/bin/apt` and `/usr/local/bin/dpkg` cleanly bind-mount `/proc`, `/sys`, `/dev`, `/dev/pts`, `/run`, sync `/etc/resolv.conf`, and `chroot` into the genuine Debian glibc userspace. Arbitrary Debian binaries are **never** executed against an incompatible musl libc.
4. **Data Safety First**: MicroOS never automatically formats, repartitions, or writes to unknown disks or filesystems.

## 2. Boot Chain

```text
Firmware (BIOS or UEFI)
  -> GRUB 2 (i386-pc El Torito / x86_64-efi BOOTX64.EFI)
    -> Linux 6.6 LTS x86_64 Kernel (/boot/vmlinuz)
      -> XZ Initramfs (/boot/initramfs.img)
        -> /init (mounts devtmpfs/proc/sys/run/tmp, shows banner, mdev)
          -> BusyBox /sbin/init (PID 1, /etc/inittab)
            -> /etc/init.d/rcS (modalias probing, safe persist attach, dbus, iwd, DHCP)
              -> /usr/local/sbin/microos-shell (micro@micro:~$)
```

## 3. Component Stack

| Layer | Technology | Rationale |
|---|---|---|
| Kernel | Linux 6.6 LTS (`x86_64`) | Long-term support, modern Intel/AMD/NVMe/Wi-Fi drivers |
| Bootloader | GRUB 2 (`i386-pc` + `x86_64-efi`) | Universal BIOS, UEFI, VirtualBox, and hybrid USB boot |
| Init & Shell | BusyBox `init` + `ash` (static) | Minimal footprint, fast boot, zero desktop dependencies |
| Networking | `iwd`, `dbus-daemon`, `iproute2`, `udhcpc` | Native Linux nl80211 Wi-Fi + Ethernet stack without host tools |
| Package Manager | Debian Bookworm `apt` + `dpkg` (glibc) | True Debian ABI compatibility stored externally on SSD |
| Micro Arcade | 9 C11 POSIX/ANSI binaries | Zero ncurses/SDL overhead; works on VGA, UEFI FB, and VT100 |
| ISO Builder | `xorriso` (hybrid MBR + GPT ESP) | Standard bootable image for VirtualBox, Rufus, Etcher, Ventoy |
| Virtual Testing | Oracle VirtualBox exclusively | Strictly compliant with project hypervisor policy (no QEMU) |
