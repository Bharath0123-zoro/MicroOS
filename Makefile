# MicroOS v1.0 Top-Level Build System
SHELL := /bin/bash
ROOT_DIR := $(CURDIR)
BUILD_DIR := $(ROOT_DIR)/build
RELEASE_DIR := $(ROOT_DIR)/release
LOGS_DIR := $(ROOT_DIR)/logs
ISO_PATH := $(RELEASE_DIR)/microos.iso

.PHONY: all clean check-env kernel busybox arcade rootfs iso verify-size checksum release help

all: check-env kernel busybox arcade rootfs iso verify-size checksum

help:
	@echo "MicroOS v1.0 Build Targets:"
	@echo "  make all          - Build kernel, BusyBox, arcade, rootfs, ISO, verify < 50MB, checksum"
	@echo "  make kernel       - Build custom x86_64 Linux kernel and loadable modules"
	@echo "  make busybox      - Build minimal BusyBox userspace"
	@echo "  make arcade       - Compile Micro Arcade launcher and all 8 C terminal games"
	@echo "  make rootfs       - Assemble rootfs, networking, hardware, storage, APT, initramfs"
	@echo "  make iso          - Generate hybrid BIOS+UEFI bootable ISO via GRUB + xorriso"
	@echo "  make verify-size  - Enforce 50,000,000-byte hard ISO size ceiling"
	@echo "  make checksum     - Generate SHA256 checksum and build-info.txt"
	@echo "  make clean        - Clean intermediate staging directories"

check-env:
	@bash $(ROOT_DIR)/scripts/check-env.sh

kernel:
	@bash $(ROOT_DIR)/kernel/build-kernel.sh 2>&1 | tee -a $(LOGS_DIR)/build.log

busybox:
	@bash $(ROOT_DIR)/rootfs/build-busybox.sh 2>&1 | tee -a $(LOGS_DIR)/build.log

arcade:
	@bash $(ROOT_DIR)/arcade/build-arcade.sh 2>&1 | tee -a $(LOGS_DIR)/build.log

rootfs: busybox arcade
	@bash $(ROOT_DIR)/rootfs/build-rootfs.sh 2>&1 | tee -a $(LOGS_DIR)/build.log

iso: kernel rootfs
	@bash $(ROOT_DIR)/scripts/build-iso.sh 2>&1 | tee -a $(LOGS_DIR)/build.log

verify-size:
	@bash $(ROOT_DIR)/scripts/check-iso-size.sh $(ISO_PATH) 2>&1 | tee -a $(LOGS_DIR)/optimization.log

checksum:
	@bash $(ROOT_DIR)/scripts/generate-release-meta.sh 2>&1 | tee -a $(LOGS_DIR)/build.log

clean:
	rm -rf $(BUILD_DIR)/rootfs-stage $(BUILD_DIR)/iso-stage $(BUILD_DIR)/initramfs.img
