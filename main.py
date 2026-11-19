#!/usr/bin/env python3
"""Validate the shipped broadsheet PNG and place it in the output directory.

The entry for make.fun's "Sum up 19 November's world news in one image"
bounty is a single pre-composed image: a square newspaper front page that
sums up 19 November 2026's world news. This program does not regenerate the
page. It checks that the image on disk is exactly the image the entry
promises -- a genuine PNG, no larger than 1 MiB, 1024 by 1024 pixels,
8-bit colour with or without an alpha channel, and properly terminated --
and then copies those exact bytes to the grader's output directory.

Layout of the checks, in order:

1. The file exists next to this script and fits the size budget.
2. The first eight bytes are the PNG signature.
3. The first chunk is IHDR, 13 bytes long, and reports 1024x1024,
   bit depth 8, colour type 2 (RGB) or 6 (RGBA).
4. The chunk stream is walked to its end and an IEND chunk is found,
   so the file is not truncated mid-image.
5. The validated bytes are copied unchanged to ``entry.png`` inside the
   output directory (``MAKEFUN_OUTPUT_DIR`` when set, ``/output``
   otherwise).

Any failed check aborts with a message on stderr and a non-zero exit
status, and nothing is written. A successful run prints the output path
and the image's SHA-256 so two runs can be compared byte for byte.
"""

import hashlib
import os
import struct
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
EXPECTED_BIT_DEPTH = 8
ALLOWED_COLOUR_TYPES = (2, 6)  # truecolour, truecolour with alpha
IHDR_LENGTH = 13


def fail(message):
    """Report a validation failure and stop before writing anything."""
    print("entry validation failed: " + message, file=sys.stderr)
    sys.exit(1)


def read_chunks(data):
    """Yield (kind, payload) for every chunk in a PNG byte string.

    Each chunk is a 4-byte big-endian length, a 4-byte type, the payload,
    and a 4-byte CRC. Walking the stream this way proves the file ends
    with an IEND chunk instead of stopping halfway through the image
    data, which a bare header check would miss.
    """
    offset = len(PNG_SIGNATURE)
    while offset < len(data):
        if offset + 8 > len(data):
            fail("truncated chunk header at offset %d" % offset)
        length, kind = struct.unpack(">I4s", data[offset:offset + 8])
        payload_start = offset + 8
        payload_end = payload_start + length
        if payload_end + 4 > len(data):
            fail("chunk %r overruns the end of the file" % kind.decode("latin-1"))
        yield kind, data[payload_start:payload_end]
        offset = payload_end + 4


def validate_png(data):
    """Check the raw bytes against every property the entry promises."""
    if len(data) > MAX_BYTES:
        fail("file is %d bytes, over the %d-byte limit" % (len(data), MAX_BYTES))
    if data[: len(PNG_SIGNATURE)] != PNG_SIGNATURE:
        fail("first bytes are not the PNG signature")
    if len(data) < len(PNG_SIGNATURE) + 8 + IHDR_LENGTH + 4:
        fail("file is too short to hold an IHDR chunk")

    chunks = list(read_chunks(data))
    first_kind, first_payload = chunks[0]
    if first_kind != b"IHDR":
        fail("first chunk is %r, expected IHDR" % first_kind.decode("latin-1"))
    if len(first_payload) != IHDR_LENGTH:
        fail("IHDR is %d bytes, expected %d" % (len(first_payload), IHDR_LENGTH))

    width, height, bit_depth, colour_type = struct.unpack(
        ">IIBB", first_payload[:10])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        fail("image is %dx%d, expected %dx%d"
             % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT))
    if bit_depth != EXPECTED_BIT_DEPTH:
        fail("bit depth is %d, expected %d" % (bit_depth, EXPECTED_BIT_DEPTH))
    if colour_type not in ALLOWED_COLOUR_TYPES:
        fail("colour type %d is neither RGB (2) nor RGBA (6)" % colour_type)
    if chunks[-1][0] != b"IEND":
        fail("last chunk is %r, expected IEND"
             % chunks[-1][0].decode("latin-1"))
    return width, height, bit_depth, colour_type


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        fail("no entry.png beside main.py (%s)" % source)
    with open(source, "rb") as handle:
        data = handle.read()

    width, height, bit_depth, colour_type = validate_png(data)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, "entry.png")
    with open(destination, "wb") as handle:
        handle.write(data)

    digest = hashlib.sha256(data).hexdigest()
    colour_name = "RGBA" if colour_type == 6 else "RGB"
    print("wrote %s (%dx%d, %d-bit %s, %d bytes, sha256 %s)"
          % (destination, width, height, bit_depth, colour_name,
             len(data), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
