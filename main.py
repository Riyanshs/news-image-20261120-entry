#!/usr/bin/env python3
"""Deliver the finished front page for news-image-20261120.

Copies the bundled entry.png into the grading output directory after
checking it is a genuine PNG or JPEG inside the competition limits
(at most 1 MiB, exactly 1024x1024). Pure standard library, no network,
fully deterministic: two runs write identical bytes.
"""

import os
import shutil
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
DEST_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DEST = os.path.join(DEST_DIR, "entry.png")

LIMIT_BYTES = 1024 * 1024
LIMIT_SIDE = 1024


def die(msg):
    print("error: " + msg, file=sys.stderr)
    sys.exit(1)


def png_dimensions(blob):
    """Return (width, height) for a PNG blob, or None if not a PNG."""
    if blob[:8] != b"\x89PNG\r\n\x1a\n" or len(blob) < 33:
        return None
    width = int.from_bytes(blob[16:20], "big")
    height = int.from_bytes(blob[20:24], "big")
    return width, height


def jpeg_dimensions(blob):
    """Return (width, height) for a JPEG blob, or None if not a JPEG."""
    if blob[:2] != b"\xff\xd8":
        return None
    pos = 2
    while pos + 9 < len(blob):
        if blob[pos] != 0xFF:
            return None
        marker = blob[pos + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height = int.from_bytes(blob[pos + 5:pos + 7], "big")
            width = int.from_bytes(blob[pos + 7:pos + 9], "big")
            return width, height
        size = int.from_bytes(blob[pos + 2:pos + 4], "big")
        if size < 2:
            return None
        pos += 2 + size
    return None


def main():
    try:
        with open(SRC, "rb") as fh:
            blob = fh.read()
    except OSError as exc:
        die("cannot read entry.png: " + str(exc))

    if not blob:
        die("entry.png is empty")
    if len(blob) > LIMIT_BYTES:
        die("entry.png is %d bytes, over the 1 MiB limit" % len(blob))

    size = png_dimensions(blob) or jpeg_dimensions(blob)
    if size is None:
        die("entry.png is neither a PNG nor a JPEG")
    if size != (LIMIT_SIDE, LIMIT_SIDE):
        die("entry.png is %dx%d, must be exactly 1024x1024" % size)

    os.makedirs(DEST_DIR, exist_ok=True)
    shutil.copyfile(SRC, DEST)
    print("wrote %s (%dx%d, %d bytes)" % (DEST, size[0], size[1], len(blob)))


if __name__ == "__main__":
    main()
