#!/usr/bin/env python3
"""Entry for the make.fun bounty news-image-20261119.

Writes the 19 November 2026 world-news summary image to /output/entry.png.
The image is a square broadsheet front page: one dominant lead (the
first-ever Trump-Xi-Putin trilateral summit in Shenzhen, three-flags hero,
"Why it matters" box), a markets band (Brent slide chart, Anthropic's
record IPO stats), three compact briefs (the ICJ's Rohingya genocide
ruling, the third Crimea Bridge strike, the IMF's debt warning) and a
World Briefs rail. Deterministic: copies the image shipped in this
repository. No network.
"""
import os
import shutil
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST = "/output/entry.png"
MAX_BYTES = 1 * 1024 * 1024
MAX_DIM = 1024
EXPECT_W, EXPECT_H = 1024, 1024


def validate_png(path):
    """Check the image meets the bounty's limits before it is copied out:
    a real PNG, at most 1 MiB, exactly the 1024x1024 front-page size this
    entry is designed at, and 8-bit RGB(A) pixels. Raises on a bad file."""
    with open(path, "rb") as f:
        head = f.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG")
    if os.path.getsize(path) > MAX_BYTES:
        raise ValueError("entry.png is over 1 MiB")
    width, height = struct.unpack(">II", head[16:24])
    if width > MAX_DIM or height > MAX_DIM:
        raise ValueError(f"entry.png is {width}x{height}, over 1024x1024")
    if (width, height) != (EXPECT_W, EXPECT_H):
        raise ValueError(
            f"entry.png is {width}x{height}, expected {EXPECT_W}x{EXPECT_H}")
    bit_depth, color_type = head[24], head[25]
    if bit_depth != 8 or color_type not in (2, 6):
        raise ValueError(
            f"entry.png is bit depth {bit_depth}, color type {color_type}; "
            "expected 8-bit RGB(A)")
    with open(path, "rb") as f:
        f.seek(-12, os.SEEK_END)
        tail = f.read()
    if tail[4:8] != b"IEND":
        raise ValueError("entry.png is truncated (no IEND chunk)")
    return width, height


def main():
    width, height = validate_png(SRC)
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(SRC, DST)
    print(f"wrote {DST} ({os.path.getsize(DST)} bytes, {width}x{height})")


if __name__ == "__main__":
    main()
