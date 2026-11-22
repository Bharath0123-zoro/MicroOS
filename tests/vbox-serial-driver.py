#!/usr/bin/env python3
"""
MicroOS v1.0 Automated Oracle VirtualBox Test Harness.
Communicates exclusively with Oracle VirtualBox VMs via COM1 TCP serial console
and VBoxManage CLI. QEMU is NEVER used.
"""
import argparse
import os
import re
import socket
import subprocess
import sys
import time

VBOX = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\r")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def vbox(*args, check=True) -> subprocess.CompletedProcess:
    cmd = [VBOX, *args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"VBoxManage {' '.join(args)} failed: {res.stderr.strip()}")
    return res


def connect_serial(port: int, timeout: float = 30.0) -> socket.socket:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=5.0)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(0.5)
            return s
        except OSError:
            time.sleep(0.3)
    raise TimeoutError(f"Could not connect to VirtualBox serial port 127.0.0.1:{port}")


def read_until(sock: socket.socket, patterns: list[str], timeout: float = 60.0) -> tuple[bool, str]:
    buf = ""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                time.sleep(0.05)
                continue
            buf += chunk.decode("utf-8", errors="replace")
            clean = strip_ansi(buf)
            for p in patterns:
                if p in clean:
                    return True, clean
        except socket.timeout:
            continue
        except OSError:
            break
    return False, strip_ansi(buf)


def uart_write(sock: socket.socket, data: bytes) -> None:
    sock.sendall(data)


def drain_sock(sock: socket.socket) -> str:
    buf = ""
    orig_timeout = sock.gettimeout()
    sock.setblocking(False)
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk.decode("utf-8", errors="replace")
    except OSError:
        pass
    finally:
        sock.settimeout(orig_timeout or 0.5)
    return strip_ansi(buf)


g_cmd_counter = 0


def send_cmd(sock: socket.socket, cmd: str, timeout: float = 25.0) -> tuple[bool, str]:
    global g_cmd_counter
    g_cmd_counter += 1
    marker = f"MK{g_cmd_counter:02d}"
    drain_sock(sock)
    time.sleep(0.1)
    payload = f"{cmd}; printf '===%s===:%d\\n' '{marker}' $?\n".encode("utf-8")
    uart_write(sock, payload)
    patterns = [f"==={marker}===:0", f"==={marker}===:1", f"==={marker}===:"]
    ok_marker, out1 = read_until(sock, patterns, timeout=timeout)
    time.sleep(0.1)
    extra = drain_sock(sock)
    return ok_marker, out1 + extra


def wait_vm_poweroff(vm_name: str, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        res = vbox("showvminfo", vm_name, "--machinereadable", check=False)
        if 'VMState="poweroff"' in res.stdout:
            return True
        time.sleep(1.0)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vm", required=True)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--mode", choices=["bios-offline", "uefi-offline", "net-persist"], required=True)
    ap.add_argument("--screenshot", default="")
    ap.add_argument("--log", required=True)
    args = ap.parse_args()

    results = {}
    log_lines = [f"\n================ TEST RUN: {args.vm} ({args.mode}) ================"]

    def log(msg: str):
        print(msg, flush=True)
        log_lines.append(msg)

    try:
        log(f"[test] Starting VirtualBox VM '{args.vm}' headless...")
        vbox("startvm", args.vm, "--type", "headless")
        time.sleep(2.0)

        sock = connect_serial(args.port, timeout=30.0)
        log("[test] Connected to VirtualBox COM1 serial console. Waiting for MicroOS boot...")

        ok, boot_out = read_until(sock, ["Welcome to MicroOS.", "micro@micro:"], timeout=90.0)
        log_lines.append("--- BOOT OUTPUT ---\n" + boot_out)
        results["boot_to_shell"] = ok
        log(f"[test] Boot to MicroOS shell: {'PASS' if ok else 'FAIL'}")

        if not ok:
            # Try sending newline in case prompt already printed before connect
            sock.sendall(b"\n")
            ok2, extra = read_until(sock, ["micro@micro:", "$ ", "# "], timeout=10.0)
            if ok2:
                results["boot_to_shell"] = True
                log("[test] Recovered prompt after newline: PASS")
            else:
                log_lines.append(extra)
                raise RuntimeError("VM did not reach MicroOS shell prompt within timeout.")

        if args.screenshot:
            time.sleep(2.0)
            vbox("controlvm", args.vm, "screenshotpng", args.screenshot, check=False)
            log(f"[test] Captured framebuffer screenshot: {args.screenshot}")

        # Helper to run & assert command
        def run_check(name: str, cmd: str, must_contain: list[str], timeout: float = 20.0):
            ok_c, out = send_cmd(sock, cmd, timeout=timeout)
            passed = ok_c and all(s in out for s in must_contain)
            results[name] = passed
            log(f"[test] {name}: {'PASS' if passed else 'FAIL'}")
            log_lines.append(f"--- CMD: {cmd} ---\n{out}")
            return passed, out

        # 1. Basic shell & sysinfo
        run_check("sysinfo", "sysinfo", ["MICROOS v1.0", "Minimal Linux. Maximum control.", "Kernel", "Memory"])
        run_check("help", "help", ["MICROOS v1.0", "hardware", "wifi", "disks", "apt", "arcade"])

        # 2. Firmware check
        if args.mode == "uefi-offline":
            run_check("uefi_firmware", "test -d /sys/firmware/efi && echo UEFI_ACTIVE", ["UEFI_ACTIVE"])
        else:
            run_check("bios_firmware", "test ! -d /sys/firmware/efi && echo BIOS_ACTIVE", ["BIOS_ACTIVE"])

        # 3. Hardware detection suite
        run_check("hardware_cpu", "hardware cpu", ["Architecture : x86_64", "Logical CPUs : 1"])
        run_check("hardware_memory", "hardware memory", ["Total RAM", "Available"])
        run_check("hardware_storage", "hardware storage", ["/dev/sd"])
        run_check("hardware_network", "hardware network", ["NETWORK ADAPTERS"])
        run_check("hardware_usb", "hardware usb", ["USB DEVICES"])

        # 4. Storage detection & safe mounting of virtual hard disk
        run_check("disks_list", "disks list", ["MicroOS Storage Devices", "/dev/sda"])
        run_check("disks_info", "disks info", ["MicroOS Storage Devices", "Active Non-Virtual Mounts"], timeout=30.0)

        if args.mode in ("bios-offline", "uefi-offline"):
            # Verify offline networking reports no interface cleanly & wifi distinguishes VirtualBox
            run_check("wifi_status_offline", "wifi status", ["MicroOS Network Status"])
            # Verify live mode APT cleanly reports persistent storage required
            run_check("apt_live_mode", "apt status", ["PERSISTENT STORAGE REQUIRED"])
            # Format virtual test disk (ONLY the VirtualBox virtual disk /dev/sda!) and test safe mount/unmount
            run_check(
                "vdisk_mount_unmount",
                "mke2fs -F -q /dev/sda && mount /dev/sda /mnt/ssd && echo microos-ok > /mnt/ssd/probe.txt && cat /mnt/ssd/probe.txt && unmount /mnt/ssd",
                ["Mounted /dev/sda", "microos-ok", "Safely unmounted /mnt/ssd"],
                timeout=30.0,
            )

        if args.mode == "net-persist":
            # Verify Ethernet DHCP / IP on VirtualBox NAT adapter & persistent Debian APT/dpkg
            run_check("eth_network", "wifi status", ["driver=e1000", "IPv4="])
            run_check("persist_mounted", "mount | grep ' /persist '", ["/persist"])
            run_check("apt_persist_ready", "apt status", ["Status         : READY", "APT Version", "DPKG Version"])
            run_check("dpkg_list", "dpkg -l | head -n 10", ["ii"])

        # 5. Arcade launcher & all 8 games offline verification
        # Verify all 9 binaries exist, launch cleanly on TTY, and exit cleanly back to shell
        game_cmds = [
            ("arcade_menu", "printf '9\\n' | arcade", ["MICRO ARCADE", "1. Snake", "8. Space Invaders"]),
            ("game_snake", "printf 'q' | snake", ["SNAKE"]),
            ("game_tetris", "printf 'q' | tetris", ["TETRIS"]),
            ("game_pong", "printf 'q' | pong", ["PONG"]),
            ("game_mines", "printf 'q' | mines", ["MINESWEEPER"]),
            ("game_2048", "printf 'q' | 2048", ["2048"]),
            ("game_guess", "printf '4\\n' | guess", ["NUMBER GUESSING"]),
            ("game_tictactoe", "printf '3\\n' | tictactoe", ["TIC-TAC-TOE"]),
            ("game_spaceinvaders", "printf 'q\\n' | spaceinvaders", ["SPACE INVADERS"]),
        ]
        for gname, gcmd, gexpect in game_cmds:
            run_check(gname, gcmd, gexpect, timeout=20.0)

        # 6. Test reboot (only on bios-offline to save time, then poweroff on all)
        if args.mode == "bios-offline":
            log("[test] Testing reboot command...")
            drain_sock(sock)
            uart_write(sock, b"reboot -f\n")
            time.sleep(2.0)
            try:
                sock.close()
            except Exception:
                pass
            time.sleep(2.0)
            # Reconnect to VirtualBox serial port after VM restart
            sock = connect_serial(args.port, timeout=45.0)
            ok_rb, rb_out = read_until(sock, ["Welcome to MicroOS.", "micro@micro:"], timeout=75.0)
            if ok_rb:
                time.sleep(2.0)
                drain_sock(sock)
            results["reboot"] = ok_rb
            log(f"[test] Reboot back to MicroOS shell: {'PASS' if ok_rb else 'FAIL'}")
            log_lines.append("--- REBOOT OUTPUT ---\n" + rb_out)

        # 7. Test clean poweroff
        log("[test] Testing poweroff command...")
        drain_sock(sock)
        uart_write(sock, b"poweroff -f\n")
        ok_po = wait_vm_poweroff(args.vm, timeout=30.0)
        results["poweroff"] = ok_po
        log(f"[test] Clean poweroff: {'PASS' if ok_po else 'FAIL'}")
        try:
            sock.close()
        except Exception:
            pass

    except Exception as exc:
        log(f"[test] EXCEPTION: {exc}")
        results["exception"] = str(exc)
    finally:
        # Ensure VM is powered off cleanly if test aborted
        vbox("controlvm", args.vm, "poweroff", check=False)
        os.makedirs(os.path.dirname(args.log), exist_ok=True)
        with open(args.log, "a", encoding="utf-8") as f:
            f.write("\n".join(log_lines) + "\n")

    passed_all = all(v is True for k, v in results.items() if k != "exception") and "exception" not in results
    log(f"[test] SUMMARY ({args.vm}): {sum(1 for v in results.values() if v is True)}/{len(results)} passed -> {'ALL PASS' if passed_all else 'FAILED'}")
    sys.exit(0 if passed_all else 1)


if __name__ == "__main__":
    main()
