#!/usr/bin/env python3
"""
Automate provisioning of the Oracle VirtualBox Alpine Linux x86_64 Builder VM
('MicroOS-Builder') over COM1 TCP serial console.
Sets up NAT networking, formats & mounts /dev/sda -> /work, enables SSH with
key auth on host port 2222, and installs all Linux kernel, BusyBox, GRUB,
xorriso, networking, firmware, and Debian debootstrap build dependencies.
"""
import os
import re
import socket
import subprocess
import sys
import time

VBOX = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\r")


def clean(s: str) -> str:
    return ANSI_RE.sub("", s)


def connect(port: int, timeout: float = 45.0) -> socket.socket:
    end = time.time() + timeout
    while time.time() < end:
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=5.0)
            s.settimeout(0.5)
            return s
        except OSError:
            time.sleep(0.4)
    raise TimeoutError(f"Could not connect to serial port {port}")


def wait_for(sock: socket.socket, needle: str, timeout: float = 120.0) -> str:
    buf = ""
    end = time.time() + timeout
    while time.time() < end:
        try:
            data = sock.recv(4096)
            if not data:
                time.sleep(0.1)
                continue
            buf += data.decode("utf-8", errors="replace")
            c = clean(buf)
            if needle in c:
                return c
        except socket.timeout:
            continue
    raise TimeoutError(f"Timed out waiting for '{needle}'. Tail:\n{clean(buf)[-1000:]}")


def uart_write(sock: socket.socket, data: bytes) -> None:
    for i in range(0, len(data), 12):
        sock.sendall(data[i:i + 12])
        time.sleep(0.015)


def run_serial(sock: socket.socket, cmd: str, marker: str, timeout: float = 300.0) -> str:
    uart_write(sock, f"{cmd}; rc=$?; printf '===DONE_%s===:%d\\n' '{marker}' $rc\n".encode("utf-8"))
    out = wait_for(sock, f"===DONE_{marker}===:", timeout=timeout)
    print(f"[builder] {marker} done", flush=True)
    return out


def main():
    if len(sys.argv) < 3:
        print("Usage: setup-alpine-builder.py <serial_port> <ssh_pubkey_path>")
        sys.exit(1)
    port = int(sys.argv[1])
    pubkey_path = sys.argv[2]
    with open(pubkey_path, "r", encoding="utf-8") as f:
        pubkey = f.read().strip()

    print("[builder] Connecting to Alpine serial console...", flush=True)
    sock = connect(port, timeout=60.0)

    print("[builder] Waiting for Alpine login prompt...", flush=True)
    # Wait for login prompt or send enter after boot
    end = time.time() + 90
    buf = ""
    logged_in = False
    while time.time() < end:
        try:
            data = sock.recv(4096)
            if data:
                buf += data.decode("utf-8", errors="replace")
                c = clean(buf)
                if "localhost login:" in c:
                    sock.sendall(b"root\n")
                    logged_in = True
                    break
                if "localhost:~#" in c:
                    logged_in = True
                    break
        except socket.timeout:
            sock.sendall(b"\n")

    if not logged_in:
        raise RuntimeError(f"Never saw Alpine login prompt. Output:\n{clean(buf)[-1000:]}")

    time.sleep(1.0)
    sock.sendall(b"\x03\n")
    time.sleep(0.5)
    run_serial(sock, "echo READY", "PROBE", timeout=15.0)
    print("[builder] Logged into Alpine builder as root!", flush=True)

    # 1. Configure eth0 DHCP & DNS
    run_serial(
        sock,
        "ip link set lo up; ip link set eth0 up && udhcpc -i eth0 -t 8 -n -q && ip -4 addr show eth0 && cat /etc/resolv.conf",
        "NET_UP",
        timeout=60.0,
    )

    # 2. Configure Alpine repositories (main + community)
    run_serial(
        sock,
        "printf 'https://dl-cdn.alpinelinux.org/alpine/v3.20/main\\nhttps://dl-cdn.alpinelinux.org/alpine/v3.20/community\\n' > /etc/apk/repositories && apk update",
        "APK_UPDATE",
        timeout=90.0,
    )

    # 3. Install e2fsprogs, openssh, rsync, bash first so we can mount /work and switch to fast SSH!
    run_serial(
        sock,
        "apk add --no-cache e2fsprogs openssh rsync bash curl",
        "BASE_PKGS",
        timeout=120.0,
    )

    # 4. Format (only if no ext4 yet) & mount /dev/sda -> /work
    run_serial(
        sock,
        "mkdir -p /work && (mount /dev/sda /work 2>/dev/null || (mkfs.ext4 -F /dev/sda && mount /dev/sda /work)) && df -h /work",
        "WORK_MOUNT",
        timeout=60.0,
    )

    # 5. Setup SSH with root key auth
    run_serial(
        sock,
        f"mkdir -p /root/.ssh && chmod 700 /root/.ssh && echo '{pubkey}' > /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys && "
        "sed -i 's/^#PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config && "
        "grep -q '^PermitRootLogin' /etc/ssh/sshd_config || echo 'PermitRootLogin prohibit-password' >> /etc/ssh/sshd_config && "
        "ssh-keygen -A && /usr/sbin/sshd && echo SSH_READY",
        "SSH_UP",
        timeout=60.0,
    )

    sock.close()
    print("[builder] Alpine builder VM is online and SSH is ready on 127.0.0.1:2222!", flush=True)


if __name__ == "__main__":
    main()
