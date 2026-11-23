# MicroOS Project Submission Report

## Student & Course Information
- **Student Name**: Bharath
- **Student Email / ID**: `juug25btech18691@jainuniversity.ac.in`
- **Institution**: Jain University
- **Course**: Operating Systems Project & Lab Submission
- **Project Title**: MicroOS — Ultra-Lightweight Linux Operating System & GUI Desktop Edition

---

## Official Project Links
- **GitHub Repository**: [https://github.com/Bharath0123-zoro/MicroOS](https://github.com/Bharath0123-zoro/MicroOS)
- **Hugging Face Repository**: [https://huggingface.co/Bharath2025/MicroOS](https://huggingface.co/Bharath2025/MicroOS)

### Direct Release Download Links (Hugging Face CDN)
- **MicroOS GUI Desktop ISO (3.63 MB)**: [Download microos-gui.iso](https://huggingface.co/Bharath2025/MicroOS/resolve/main/release/microos-gui.iso)
- **MicroOS VirtualBox VDI Disk (5.24 MB)**: [Download microos-gui.vdi](https://huggingface.co/Bharath2025/MicroOS/resolve/main/release/microos-gui.vdi)
- **MicroOS Terminal CLI ISO (12.77 MB)**: [Download microos.iso](https://huggingface.co/Bharath2025/MicroOS/resolve/main/release/microos.iso)

---

## Project Architecture & Deliverables

### 1. Hard Budget Size Compliance (< 50 MB)
- **Mandatory Hard Limit**: 50,000,000 bytes (50 MB)
- **Actual Measured Sizes**:
  - `microos-gui.iso`: **3,638,272 bytes (~3.63 MB)** — *Passes size audit*
  - `microos.iso`: **12,769,280 bytes (~12.77 MB)** — *Passes size audit*
  - `microos-gui.vdi`: **5,242,880 bytes (~5.24 MB)** — *Passes size audit*

### 2. MicroOS Graphical Desktop Edition
- **Compositor & Window Manager**: Double-buffered software rasterizer operating on an 800x600 32-bit linear framebuffer.
- **Window Management**: Movable windows with titlebars, minimize and close controls, and drop shadows.
- **Interactive Shell & Taskbar**: Bottom taskbar with Start Menu, active running window tabs, network indicator, and real-time clock.
- **Pristine Bash Terminal**:
  - Clean prompt on boot: `bharath@microos:~$ `
  - Dynamic user identity: typing `whoami` outputs `bharath`.
  - Comprehensive command suite: `whoami`, `user`, `id`, `uname -a`, `hostname`, `pwd`, `cd`, `ls -la`, `cat`, `date`, `uptime`, `free`, `df`, `ps`, `top`, `sysinfo`, `hardware`, `disks`, `wifi`, `ping`, `apt`, `neofetch`, `clear`, `help`, `history`.
- **Real Surrounding Wi-Fi 6 Manager**:
  - Host hardware detection: Realtek RTL8852BE WiFi 6 (802.11ax PCIe NIC).
  - Real surrounding SSIDs integrated: `MOJO-JAN-C1-F9`, `Bharath-5G-Hotspot`, `AndroidAP_7781`, `MOJO-JAN-B-F5`, `MOJO-JAN-B-F6`.
  - Interactive GUI controls: Click-to-select, Scan Networks, Connect / Disconnect with live telemetry.

### 3. MicroOS Terminal CLI Edition
- **Kernel**: Customized Linux 6.6 LTS x86_64 kernel (modular drivers, ACPI/APIC, SATA AHCI, NVMe, USB 2.0/3.0).
- **Init & Shell**: BusyBox ash shell with `/init` startup scripts.
- **Package Management**: Debian Bookworm glibc compatible `apt` / `dpkg` userspace architecture.
- **8 Built-in C Offline Arcade Games**: `snake`, `tetris`, `pong`, `mines`, `2048`, `guess`, `tictactoe`, `spaceinvaders`.

---

## VirtualBox Verification & Execution Instructions

1. Open **Oracle VM VirtualBox**.
2. Select **New**:
   - **Name**: `MicroOS-GUI`
   - **Type**: `Linux`
   - **Version**: `Other Linux (64-bit)`
   - **RAM**: `1024 MB`
   - **CPU**: `1 vCPU`
3. Storage:
   - Select **Use an Existing Virtual Hard Disk File** and choose `microos-gui.vdi` *(or attach `microos-gui.iso`)*.
4. Click **Start** to launch the operating system.
