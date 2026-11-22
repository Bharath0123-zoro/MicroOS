# Building MicroOS v1.0

## Prerequisites (Linux x86_64 Build Host)

Required packages on Alpine Linux (`3.20`) or Debian (`12 Bookworm`):

- Toolchain: `gcc`, `make`, `bc`, `flex`, `bison`, `perl`, `openssl-dev`/`libssl-dev`, `elfutils-dev`/`libelf-dev`, `linux-headers`
- Boot & ISO: `grub`, `grub-bios`/`grub-pc-bin`, `grub-efi`/`grub-efi-amd64-bin`, `xorriso`, `mtools`, `dosfstools`
- Utilities: `xz`, `cpio`, `tar`, `curl`, `bash`, `kmod` (`depmod`), `e2fsprogs`
- Userspace Networking & Curated Firmware: `iwd`, `dbus`, `iproute2`, `blkid`, Intel/Realtek/MediaTek Wi-Fi & NIC firmware packages
- Optional Persistent Debian Image: `debootstrap`, `dpkg`

On Windows hosts without WSL, MicroOS uses an automated headless **Oracle VirtualBox** Linux x86_64 builder VM (`MicroOS-Builder`). QEMU is never used.

## Reproducible Build Commands

```bash
# Full end-to-end build, size check (< 50 MB), and SHA256 release generation
make all

# Individual stages
make check-env
make kernel
make busybox
make arcade
make rootfs
make iso
make verify-size
make checksum
```

## Optional: Build External Debian Persistent Disk Image

To create a ready-to-attach persistent ext4 volume (`LABEL=MICROOS_PERSIST`) containing Debian Bookworm glibc + `apt` + `dpkg`:

```bash
sudo bash package-manager/build-debian-persist.sh build/microos-persist.img 1024
```

Convert to VirtualBox VDI for persistent VM testing:

```powershell
VBoxManage convertfromraw build\microos-persist.img build\vm-disks\microos-persist.vdi --format VDI
```
