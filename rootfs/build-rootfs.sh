#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/configs/microos.conf"

STAGE="${ROOT_DIR}/build/rootfs-stage"
BB_OUT="${ROOT_DIR}/build/busybox-out"
MOD_OUT="${ROOT_DIR}/build/modules-out"
ARC_OUT="${ROOT_DIR}/build/arcade-bin"
INITRAMFS="${ROOT_DIR}/build/initramfs.img"

echo "[rootfs] Staging MicroOS v${MICROOS_VERSION} minimal root filesystem..."
rm -rf "${STAGE}"
mkdir -p "${STAGE}"/{bin,sbin,dev,proc,sys,etc,lib,lib64,tmp,run,mnt,mnt/ssd,persist,root,home/micro}
mkdir -p "${STAGE}"/etc/{init.d,iwd,dbus-1,dbus-1/system.d,microos}
mkdir -p "${STAGE}"/usr/{bin,sbin,lib,libexec,local/bin,local/sbin,share/udhcpc,share/dbus-1/system.d}
mkdir -p "${STAGE}"/var/{lib/iwd,run,log,tmp}
chmod 1777 "${STAGE}/tmp" "${STAGE}/var/tmp"
chmod 0700 "${STAGE}/var/lib/iwd"

# 1. Install BusyBox
cp -a "${BB_OUT}/." "${STAGE}/"

# 2. Core /etc configuration files
cat > "${STAGE}/etc/hostname" <<'EOF'
micro
EOF

cat > "${STAGE}/etc/hosts" <<'EOF'
127.0.0.1   localhost micro
::1         localhost ip6-localhost ip6-loopback
EOF

cat > "${STAGE}/etc/passwd" <<'EOF'
root:x:0:0:root:/root:/bin/sh
micro:x:1000:1000:MicroOS User:/home/micro:/bin/sh
messagebus:x:100:101:D-Bus:/run/dbus:/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/sbin/nologin
EOF

cat > "${STAGE}/etc/group" <<'EOF'
root:x:0:
tty:x:5:
disk:x:6:
wheel:x:10:micro
messagebus:x:101:
micro:x:1000:
nogroup:x:65534:
EOF

cat > "${STAGE}/etc/fstab" <<'EOF'
proc      /proc     proc      defaults        0 0
sysfs     /sys      sysfs     defaults        0 0
devpts    /dev/pts  devpts    gid=5,mode=620  0 0
tmpfs     /run      tmpfs     defaults        0 0
tmpfs     /tmp      tmpfs     mode=1777       0 0
EOF

cat > "${STAGE}/etc/nsswitch.conf" <<'EOF'
passwd: files
group:  files
hosts:  files dns
EOF

cat > "${STAGE}/etc/os-release" <<EOF
NAME="MicroOS"
VERSION="${MICROOS_VERSION}"
ID=microos
PRETTY_NAME="MicroOS v${MICROOS_VERSION} (Minimal Linux)"
HOME_URL="https://microos.local"
EOF
cp "${STAGE}/etc/os-release" "${STAGE}/etc/microos-release"

cat > "${STAGE}/etc/issue" <<EOF

MICROOS v${MICROOS_VERSION}
Minimal Linux. Maximum control.

EOF

# 3. Install Init system & Shell
install -m 0755 "${ROOT_DIR}/init/init"                 "${STAGE}/init"
install -m 0644 "${ROOT_DIR}/init/inittab"              "${STAGE}/etc/inittab"
install -m 0755 "${ROOT_DIR}/init/rcS"                  "${STAGE}/etc/init.d/rcS"
install -m 0755 "${ROOT_DIR}/init/rcK"                  "${STAGE}/etc/init.d/rcK"
install -m 0755 "${ROOT_DIR}/init/microos-serial-tty"   "${STAGE}/usr/local/sbin/microos-serial-tty"

install -m 0755 "${ROOT_DIR}/shell/microos-shell"       "${STAGE}/usr/local/sbin/microos-shell"
install -m 0644 "${ROOT_DIR}/shell/profile"             "${STAGE}/etc/profile"
install -m 0755 "${ROOT_DIR}/shell/help"                "${STAGE}/usr/local/bin/help"
install -m 0755 "${ROOT_DIR}/shell/sysinfo"             "${STAGE}/usr/local/bin/sysinfo"

# 4. Install Hardware, Networking, Storage, Package Manager utilities
install -m 0755 "${ROOT_DIR}/hardware/hardware"                 "${STAGE}/usr/local/bin/hardware"
install -m 0755 "${ROOT_DIR}/networking/wifi"                   "${STAGE}/usr/local/bin/wifi"
install -m 0755 "${ROOT_DIR}/networking/udhcpc-default.script"  "${STAGE}/usr/share/udhcpc/default.script"
install -m 0644 "${ROOT_DIR}/networking/iwd-main.conf"          "${STAGE}/etc/iwd/main.conf"
install -m 0644 "${ROOT_DIR}/networking/dbus-system.conf"       "${STAGE}/etc/dbus-1/system.conf"

install -m 0755 "${ROOT_DIR}/storage/disks"                     "${STAGE}/usr/local/bin/disks"
install -m 0755 "${ROOT_DIR}/storage/microos-mount"             "${STAGE}/usr/local/bin/mount"
install -m 0755 "${ROOT_DIR}/storage/unmount"                   "${STAGE}/usr/local/bin/unmount"
install -m 0755 "${ROOT_DIR}/storage/microos-persist-attach"    "${STAGE}/usr/local/sbin/microos-persist-attach"

install -m 0755 "${ROOT_DIR}/package-manager/apt"               "${STAGE}/usr/local/bin/apt"
install -m 0755 "${ROOT_DIR}/package-manager/dpkg"              "${STAGE}/usr/local/bin/dpkg"

# 5. Install Micro Arcade (launcher + 8 games)
for g in arcade snake tetris pong mines 2048 guess tictactoe spaceinvaders; do
    install -m 0755 "${ARC_OUT}/${g}" "${STAGE}/usr/local/bin/${g}"
done

# 6. Integrate native Linux networking binaries (iwd, iwctl, dbus-daemon, iproute2 ip) + minimal shared libs
copy_bin_with_libs() {
    local src="$1"
    local dst="$2"
    [[ -x "$src" ]] || return 0
    mkdir -p "$(dirname "${STAGE}${dst}")"
    cp -L "$src" "${STAGE}${dst}"
    chmod 0755 "${STAGE}${dst}"
    strip --strip-unneeded "${STAGE}${dst}" 2>/dev/null || true

    # Copy required dynamic linker & shared libraries
    ldd "$src" 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /^\//) print $i}' | sort -u | while read -r lib; do
        [[ -f "$lib" ]] || continue
        local ldir
        ldir="$(dirname "$lib")"
        mkdir -p "${STAGE}${ldir}"
        if [[ ! -e "${STAGE}${lib}" ]]; then
            cp -L "$lib" "${STAGE}${lib}"
            strip --strip-unneeded "${STAGE}${lib}" 2>/dev/null || true
        fi
    done
}

# Copy iproute2 'ip', dbus-daemon, iwd, iwctl
if [[ -x /sbin/ip ]]; then
    copy_bin_with_libs /sbin/ip /usr/sbin/ip
elif [[ -x /usr/sbin/ip ]]; then
    copy_bin_with_libs /usr/sbin/ip /usr/sbin/ip
elif [[ -x /bin/ip ]]; then
    copy_bin_with_libs /bin/ip /usr/sbin/ip
fi

[[ -x /usr/bin/dbus-daemon ]] && copy_bin_with_libs /usr/bin/dbus-daemon /usr/bin/dbus-daemon
if [[ -x /usr/libexec/iwd ]]; then
    copy_bin_with_libs /usr/libexec/iwd /usr/libexec/iwd
elif [[ -x /usr/sbin/iwd ]]; then
    copy_bin_with_libs /usr/sbin/iwd /usr/libexec/iwd
fi
[[ -x /usr/bin/iwctl ]] && copy_bin_with_libs /usr/bin/iwctl /usr/bin/iwctl

# Copy iwd D-Bus policy file if available on build host
for p in /usr/share/dbus-1/system.d/iwd-dbus.conf /etc/dbus-1/system.d/iwd-dbus.conf; do
    if [[ -f "$p" ]]; then
        cp "$p" "${STAGE}/usr/share/dbus-1/system.d/"
        break
    fi
done

# Copy e2fsprogs mkfs.ext4 / fsck.ext4 only if present & compact, plus blkid if util-linux available
[[ -x /sbin/blkid ]] && copy_bin_with_libs /sbin/blkid /usr/sbin/blkid

# 7. Install compiled kernel modules
if [[ -d "${MOD_OUT}/lib/modules" ]]; then
    cp -a "${MOD_OUT}/lib/modules" "${STAGE}/lib/"
fi

# 8. Install curated laptop Wi-Fi & Ethernet firmware (budgeted to stay well under 50 MB ISO)
mkdir -p "${STAGE}/lib/firmware"
copy_fw_glob() {
    local pattern="$1"
    local subdir="$2"
    local src_base="/lib/firmware"
    mkdir -p "${STAGE}/lib/firmware/${subdir}"
    shopt -s nullglob
    for f in ${src_base}/${pattern}; do
        [[ -f "$f" ]] || continue
        local bn
        bn="$(basename "$f")"
        case "$bn" in
            *.xz|*.zst)
                cp -L "$f" "${STAGE}/lib/firmware/${subdir}/${bn}"
                ;;
            *)
                xz -c -6 "$f" > "${STAGE}/lib/firmware/${subdir}/${bn}.xz"
                ;;
        esac
    done
    shopt -u nullglob
}

# Selected high-coverage laptop chipsets (Intel AX200/AX201/AX210/8265/9260/7265, Realtek rtw88 + rtl_nic, MediaTek mt7921)
copy_fw_glob "iwlwifi-cc-a0-*.ucode*" ""
copy_fw_glob "iwlwifi-ty-a0-gf-a0-*.ucode*" ""
copy_fw_glob "iwlwifi-QuZ-a0-hr-b0-*.ucode*" ""
copy_fw_glob "iwlwifi-9260-th-b0-jf-b0-*.ucode*" ""
copy_fw_glob "iwlwifi-8265-*.ucode*" ""
copy_fw_glob "iwlwifi-7265D-*.ucode*" ""
copy_fw_glob "rtw88/rtw8821c_fw.bin*" "rtw88"
copy_fw_glob "rtw88/rtw8822b_fw.bin*" "rtw88"
copy_fw_glob "rtw88/rtw8822c_fw.bin*" "rtw88"
copy_fw_glob "rtw88/rtw8723d_fw.bin*" "rtw88"
copy_fw_glob "rtl_nic/rtl8168*.fw*" "rtl_nic"
copy_fw_glob "rtl_nic/rtl8125*.fw*" "rtl_nic"
copy_fw_glob "mediatek/WIFI_MT7961_patch_mcu_1_2_hdr.bin*" "mediatek"
copy_fw_glob "mediatek/WIFI_RAM_CODE_MT7961_1.bin*" "mediatek"

FW_BYTES="$(du -sb "${STAGE}/lib/firmware" | awk '{print $1}')"
echo "[rootfs] Curated firmware payload: ${FW_BYTES} bytes ($((FW_BYTES / 1024)) KB)"

# 9. Normalize CRLF -> LF on shell scripts & config files in rootfs (skip binary files!)
find "${STAGE}/etc" "${STAGE}/usr/share/udhcpc" "${STAGE}/init" \
    -type f -exec sed -i 's/\r$//' {} + 2>/dev/null || true
for script in "${STAGE}/usr/local/bin"/* "${STAGE}/usr/local/sbin"/*; do
    [[ -f "$script" ]] || continue
    # Only strip CRLF if it is a text shell script
    if file "$script" 2>/dev/null | grep -qi "text"; then
        sed -i 's/\r$//' "$script" 2>/dev/null || true
    fi
done

# 10. Create static essential device nodes (devtmpfs mounts over /dev, these are safety fallbacks)
mknod -m 600 "${STAGE}/dev/console" c 5 1 2>/dev/null || true
mknod -m 666 "${STAGE}/dev/null"    c 1 3 2>/dev/null || true

# 11. Build XZ-compressed initramfs (CRC32 check is mandatory for Linux kernel XZ decoder)
echo "[rootfs] Packing XZ-compressed initramfs..."
(
    cd "${STAGE}"
    find . -print0 | cpio --null -ov --format=newc 2>/dev/null | xz -9 --check=crc32 --threads=0 > "${INITRAMFS}"
)

ISIZE="$(stat -c%s "${INITRAMFS}")"
echo "[rootfs] Built initramfs.img: ${ISIZE} bytes ($((ISIZE / 1024)) KB)"
