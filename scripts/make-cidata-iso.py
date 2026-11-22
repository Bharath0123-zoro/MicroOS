#!/usr/bin/env python3
"""
Minimal pure-Python ISO9660 (Level 1 + Joliet/RockRidge-free compatible)
NoCloud 'cidata' seed image builder for cloud-init on Debian 12.
Generates a valid ISO9660 filesystem containing /meta-data and /user-data
with Volume Identifier 'cidata' (exact case for cloud-init NoCloud detection).
"""
import os
import struct
import sys

SECTOR = 2048


def pad_sector(data: bytes) -> bytes:
    rem = len(data) % SECTOR
    return data if rem == 0 else data + b"\x00" * (SECTOR - rem)


def both16(val: int) -> bytes:
    return struct.pack("<H", val) + struct.pack(">H", val)


def both32(val: int) -> bytes:
    return struct.pack("<I", val) + struct.pack(">I", val)


def dir_record(name_bytes: bytes, lba: int, size: int, is_dir: bool) -> bytes:
    flags = 0x02 if is_dir else 0x00
    name_len = len(name_bytes)
    rec_len = 33 + name_len + (1 if (33 + name_len) % 2 == 1 else 0)
    date = bytes([126, 11, 18, 12, 0, 0, 0])  # 2026-11-18 12:00:00 UTC
    rec = bytearray()
    rec.append(rec_len)
    rec.append(0)  # ext attr len
    rec += both32(lba)
    rec += both32(size)
    rec += date
    rec.append(flags)
    rec.append(0)  # file unit size
    rec.append(0)  # interleave gap
    rec += both16(1)  # volume seq num
    rec.append(name_len)
    rec += name_bytes
    if len(rec) < rec_len:
        rec.append(0)
    return bytes(rec)


def build_iso(out_path: str, vol_id: str, files: list[tuple[str, bytes]]) -> None:
    # Layout:
    # LBA 0..15: System Area (zeros)
    # LBA 16: Primary Volume Descriptor
    # LBA 17: Volume Descriptor Set Terminator
    # LBA 18: Path Table L
    # LBA 19: Path Table M
    # LBA 20: Root Directory
    # LBA 21+: File data (each file starts at its own sector)
    # Note: cloud-init matches both uppercase/lowercase filenames on iso9660
    # and Linux mounts lowercase or maps RockRidge; ISO9660 Level 1 standard
    # names with RockRidge NM entries ensure exact lowercase 'user-data' & 'meta-data'!

    def rr_nm(real_name: str) -> bytes:
        nb = real_name.encode("ascii")
        # System Use entry: 'NM', length = 5 + len(nb), version=1, flags=0
        return b"NM" + bytes([5 + len(nb), 1, 0]) + nb

    def dir_record_rr(iso_name: bytes, lba: int, size: int, is_dir: bool, real_name: str | None = None) -> bytes:
        flags = 0x02 if is_dir else 0x00
        su = b""
        if real_name is not None:
            su = rr_nm(real_name)
        name_len = len(iso_name)
        pad_len = 1 if (name_len % 2 == 0) else 0
        rec_len = 33 + name_len + pad_len + len(su)
        if rec_len % 2 == 1:
            su += b"\x00"
            rec_len += 1
        date = bytes([126, 11, 18, 12, 0, 0, 0])
        rec = bytearray()
        rec.append(rec_len)
        rec.append(0)
        rec += both32(lba)
        rec += both32(size)
        rec += date
        rec.append(flags)
        rec.append(0)
        rec.append(0)
        rec += both16(1)
        rec.append(name_len)
        rec += iso_name
        if pad_len:
            rec.append(0)
        rec += su
        return bytes(rec)

    # Place files starting at LBA 21
    cur_lba = 21
    file_entries = []
    for fname, content in files:
        iso_name = (fname.upper().replace("-", "_") + ";1").encode("ascii")
        sectors = max(1, (len(content) + SECTOR - 1) // SECTOR)
        file_entries.append((fname, iso_name, cur_lba, len(content), pad_sector(content)))
        cur_lba += sectors

    total_sectors = cur_lba

    # Build Root Directory (LBA 20)
    # Add SP (SUSP indicator) on '.' entry so Linux iso9660 parses RockRidge NM entries!
    sp_entry = b"SP" + bytes([7, 1, 0xBE, 0xEF, 0])
    # '.' entry with SP
    dot_su = sp_entry
    dot_len = 33 + 1 + len(dot_su)
    if dot_len % 2 == 1:
        dot_su += b"\x00"
        dot_len += 1
    date = bytes([126, 11, 18, 12, 0, 0, 0])

    # Build root dir content twice to get exact size
    root_entries = bytearray()
    # Placeholder for '.' and '..'
    def make_dot(code: bytes, su: bytes, root_size: int) -> bytes:
        rec_len = 33 + 1 + len(su)
        if rec_len % 2 == 1:
            su = su + b"\x00"
            rec_len += 1
        r = bytearray([rec_len, 0])
        r += both32(20)
        r += both32(root_size)
        r += date
        r += bytes([0x02, 0, 0])
        r += both16(1)
        r += bytes([1]) + code + su
        return bytes(r)

    root_size = SECTOR
    root_entries += make_dot(b"\x00", dot_su, root_size)
    root_entries += make_dot(b"\x01", b"", root_size)
    for fname, iso_name, lba, size, _ in file_entries:
        root_entries += dir_record_rr(iso_name, lba, size, False, real_name=fname)

    root_sector = pad_sector(bytes(root_entries))
    assert len(root_sector) == SECTOR

    # Root directory record for PVD (must be 34 bytes)
    pvd_root = dir_record(b"\x00", 20, SECTOR, True)
    assert len(pvd_root) == 34

    # Path tables (LBA 18 LE, LBA 19 BE)
    pt_l = bytes([1, 0]) + struct.pack("<I", 20) + struct.pack("<H", 1) + b"\x00\x00"
    pt_m = bytes([1, 0]) + struct.pack(">I", 20) + struct.pack(">H", 1) + b"\x00\x00"

    # Primary Volume Descriptor (LBA 16)
    pvd = bytearray(SECTOR)
    pvd[0] = 1
    pvd[1:6] = b"CD001"
    pvd[6] = 1
    pvd[8:40] = b"LINUX".ljust(32, b" ")
    pvd[40:72] = vol_id.encode("ascii").ljust(32, b" ")[:32]
    pvd[80:88] = both32(total_sectors)
    pvd[120:124] = both16(1)  # volume set size
    pvd[124:128] = both16(1)  # volume seq num
    pvd[128:132] = both16(SECTOR)
    pvd[132:140] = both32(len(pt_l))
    pvd[140:144] = struct.pack("<I", 18)
    pvd[148:152] = struct.pack(">I", 19)
    pvd[156:190] = pvd_root
    pvd[190:318] = b" " * 128
    pvd[318:446] = b"MICROOS".ljust(128, b" ")
    pvd[446:574] = b"MICROOS".ljust(128, b" ")
    pvd[574:702] = b"MICROOS".ljust(128, b" ")
    pvd[702:739] = b" " * 37
    pvd[739:776] = b" " * 37
    pvd[776:813] = b" " * 37
    ts = b"2026111812000000\x00"
    pvd[813:830] = ts
    pvd[830:847] = ts
    pvd[847:864] = b"0000000000000000\x00"
    pvd[864:881] = ts
    pvd[881] = 1

    # Terminator (LBA 17)
    term = bytearray(SECTOR)
    term[0] = 255
    term[1:6] = b"CD001"
    term[6] = 1

    with open(out_path, "wb") as f:
        f.write(b"\x00" * (16 * SECTOR))
        f.write(pvd)
        f.write(term)
        f.write(pad_sector(pt_l))
        f.write(pad_sector(pt_m))
        f.write(root_sector)
        for _, _, _, _, padded in file_entries:
            f.write(padded)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: make-cidata-iso.py <out.iso> <user-data> <meta-data>")
        sys.exit(1)
    out_iso, ud_path, md_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(ud_path, "rb") as f:
        ud = f.read()
    with open(md_path, "rb") as f:
        md = f.read()
    build_iso(out_iso, "cidata", [("meta-data", md), ("user-data", ud)])
    print(f"Wrote {out_iso} ({os.path.getsize(out_iso)} bytes)")
