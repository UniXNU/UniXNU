#!/usr/bin/env python3
"""Boot an ESP directory in QEMU (AArch64 virt + AAVMF) and check the log.

The ESP is exposed read-only through QEMU's vvfat driver, so nothing on the
host is modified. The serial console is captured to a log; when UniXNU
logs "menu: shown", a screenshot is taken over QMP and optional keys are
sent to the emulated USB keyboard. Each --expect is a regular expression
that must match the (ANSI-stripped) serial log. Exit status 0 = all matched.
"""

import argparse
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from pathlib import Path

FIRMWARE_CANDIDATES = [
    ("/usr/share/edk2/aarch64/QEMU_EFI.fd", "/usr/share/edk2/aarch64/QEMU_VARS.fd"),
    ("/usr/share/AAVMF/AAVMF_CODE.fd", "/usr/share/AAVMF/AAVMF_VARS.fd"),
    ("/usr/share/qemu-efi-aarch64/QEMU_EFI.fd", None),
    ("/usr/share/edk2/aarch64/QEMU_CODE.fd", "/usr/share/edk2/aarch64/QEMU_VARS.fd"),
]

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b[()][A-Za-z0-9]")


def find_firmware(code):
    if code:
        return Path(code), None
    qemu = shutil.which("qemu-system-aarch64")
    if qemu:
        share = Path(qemu).resolve().parent.parent / "share" / "qemu"
        firmware = share / "edk2-aarch64-code.fd"
        variables = share / "edk2-arm-vars.fd"
        if firmware.is_file():
            return firmware, (variables if variables.is_file() else None)
    for c, v in FIRMWARE_CANDIDATES:
        if Path(c).is_file():
            return Path(c), (Path(v) if v and Path(v).is_file() else None)
    sys.exit("error: no AAVMF firmware found; pass --firmware")


class Qmp:
    def __init__(self, path, timeout=10.0):
        deadline = time.time() + timeout
        while True:
            try:
                self.sock = socket.socket(socket.AF_UNIX)
                self.sock.connect(path)
                break
            except OSError:
                if time.time() > deadline:
                    raise
                time.sleep(0.1)
        self.file = self.sock.makefile("rw")
        self.file.readline()
        self.command("qmp_capabilities")

    def command(self, name, **arguments):
        msg = {"execute": name}
        if arguments:
            msg["arguments"] = arguments
        self.file.write(json.dumps(msg) + "\n")
        self.file.flush()
        while True:
            reply = json.loads(self.file.readline())
            if "return" in reply or "error" in reply:
                return reply


def ppm_to_png(ppm: Path, png: Path) -> None:
    data = ppm.read_bytes()
    # Comments and whitespace separate header tokens, but raster bytes must
    # never be stripped: every byte value is valid in an RGB channel.
    separator = rb"(?:[ \t\r\n\v\f]|#[^\r\n]*(?:\r\n|[\r\n]))+"
    header = re.match(rb"P6" + separator + rb"([0-9]+)" + separator
                      + rb"([0-9]+)" + separator + rb"([0-9]+)[ \t\r\n\v\f]", data)
    if header is None:
        raise ValueError("invalid binary PPM header")
    width, height, maxval = map(int, header.groups())
    if width < 1 or height < 1 or maxval != 255:
        raise ValueError("PPM requires positive dimensions and maxval 255")
    pixels = data[header.end():]
    if len(pixels) != width * height * 3:
        raise ValueError("PPM raster length does not match dimensions")
    raw = b"".join(b"\x00" + pixels[y * width * 3:(y + 1) * width * 3] for y in range(height))

    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    png.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("esp", type=Path, help="ESP directory")
    parser.add_argument("--firmware", help="AAVMF code image (default: first found)")
    parser.add_argument("--log", type=Path, required=True, help="serial log output")
    parser.add_argument("--screenshot", type=Path, help="PNG of the menu")
    parser.add_argument("--keys", default="", help="comma-separated QEMU qcodes sent after the menu shows")
    parser.add_argument("--expect", action="append", default=[], help="regex that must match the log")
    parser.add_argument("--reject", action="append", default=[], help="regex that must not match the log")
    parser.add_argument("--no-gop", action="store_true", help="no display device (text console only)")
    parser.add_argument("--display-size", metavar="WxH",
                        help="use a virtio-gpu display of this size instead of ramfb (for example 1080x2400)")
    parser.add_argument("--disk", action="append", default=[], type=Path, help="extra raw disk image (read-only)")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--cpus", type=int, default=2, help="number of virtual CPUs (default: 2)")
    parser.add_argument("--finish-on-expect", action="store_true",
                        help="finish two seconds after all expected patterns match")
    parser.add_argument("--menu-marker", default=r"UNIXNU: menu: shown")
    args = parser.parse_args()
    if args.cpus < 1:
        parser.error("--cpus must be positive")
    display = None
    if args.display_size:
        match = re.fullmatch(r"([0-9]+)x([0-9]+)", args.display_size)
        if not match or not all(0 < int(v) <= 8192 for v in match.groups()):
            parser.error("--display-size must be WxH with both sides in 1..8192")
        if args.no_gop:
            parser.error("--display-size conflicts with --no-gop")
        display = tuple(int(v) for v in match.groups())
    if args.finish_on_expect and not args.expect:
        parser.error("--finish-on-expect requires --expect")

    qemu = shutil.which("qemu-system-aarch64")
    if not qemu:
        sys.exit("error: qemu-system-aarch64 not found")
    code, vars_template = find_firmware(args.firmware)

    work = Path(tempfile.mkdtemp(prefix="unixnu-qemu-"))
    qmp_path = work / "qmp.sock"
    args.log.parent.mkdir(parents=True, exist_ok=True)
    if args.log.exists():
        args.log.unlink()

    cmd = [
        qemu, "-M", "virt", "-cpu", "cortex-a72", "-m", "1024", "-smp", str(args.cpus),
        "-drive", f"if=pflash,format=raw,readonly=on,file={code}",
    ]
    if vars_template:
        vars_copy = work / "vars.fd"
        shutil.copy(vars_template, vars_copy)
        cmd += ["-drive", f"if=pflash,format=raw,file={vars_copy}"]
    cmd += [
        "-drive", f"if=none,id=esp,format=raw,readonly=on,file=fat:{args.esp.resolve()}",
        "-device", "virtio-blk-pci,drive=esp",
    ]
    for index, disk in enumerate(args.disk):
        cmd += [
            "-drive", f"if=none,id=disk{index},format=raw,readonly=on,file={disk.resolve()}",
            "-device", f"virtio-blk-pci,drive=disk{index}",
        ]
    if display:
        cmd += ["-device", f"virtio-gpu-pci,xres={display[0]},yres={display[1]}"]
    elif not args.no_gop:
        cmd += ["-device", "ramfb"]
    cmd += [
        "-device", "qemu-xhci", "-device", "usb-kbd",
        "-nic", "none", "-display", "none", "-no-reboot",
        "-serial", f"file:{args.log}",
        "-qmp", f"unix:{qmp_path},server=on,wait=off",
    ]
    print("qemu:", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    qmp = None
    menu_seen = False
    expectations_since = None
    expectations_complete = False
    deadline = time.time() + args.timeout
    try:
        qmp = Qmp(str(qmp_path))
        while proc.poll() is None and time.time() < deadline:
            text = args.log.read_text(errors="replace") if args.log.exists() else ""
            if args.finish_on_expect:
                clean_text = ANSI.sub("", text)
                if all(re.search(pattern, clean_text) for pattern in args.expect):
                    if expectations_since is None:
                        expectations_since = time.time()
                    elif time.time() - expectations_since >= 2.0:
                        expectations_complete = True
                        break
            if not menu_seen and re.search(args.menu_marker, text):
                menu_seen = True
                time.sleep(0.6)
                if args.screenshot:
                    ppm = work / "screen.ppm"
                    reply = qmp.command("screendump", filename=str(ppm))
                    if "error" in reply:
                        print("screendump failed:", reply["error"])
                    else:
                        args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                        ppm_to_png(ppm, args.screenshot)
                        print("screenshot:", args.screenshot)
                for key in filter(None, args.keys.split(",")):
                    qmp.command("send-key", keys=[{"type": "qcode", "data": key.strip()}])
                    time.sleep(0.3)
            time.sleep(0.2)
    finally:
        if proc.poll() is None:
            print("expectations complete: stopping QEMU" if expectations_complete else "timeout: stopping QEMU")
            if qmp:
                try:
                    qmp.command("quit")
                except OSError:
                    pass
            try:
                proc.wait(5)
            except subprocess.TimeoutExpired:
                proc.kill()
        out = proc.stdout.read().decode(errors="replace") if proc.stdout else ""
        if out.strip():
            print("qemu output:", out.strip())
        shutil.rmtree(work, ignore_errors=True)

    log = ANSI.sub("", args.log.read_text(errors="replace")) if args.log.exists() else ""
    clean = args.log.with_suffix(".clean.log")
    clean.write_text(log)

    failed = 0
    for pattern in args.expect:
        ok = re.search(pattern, log) is not None
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  expect  {pattern}")
    for pattern in args.reject:
        ok = re.search(pattern, log) is None
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  reject  {pattern}")
    print(f"log: {clean}")
    print("SMOKE", "PASS" if failed == 0 else f"FAIL ({failed})")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
