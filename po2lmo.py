#!/usr/bin/env python3
"""
po2lmo.py - PO to LMO conversion tool (Python implementation)

Python implementation of the original C po2lmo tool for converting
GNU gettext PO files to Lua Machine Objects (LMO) binary format.

Original C version:
Copyright (C) 2009-2012 Jo-Philipp Wich <xm@subsignal.org>

Python implementation maintains the same binary format compatibility.
"""

import sys
import struct
import os
import re
import argparse
import logging
from typing import List, Tuple, Optional


class LMOEntry:
    """Represents a single LMO entry"""

    def __init__(self, key_id: int, val_id: int, offset: int, length: int):
        self.key_id = key_id
        self.val_id = val_id
        self.offset = offset
        self.length = length


def sfh_hash(data: str) -> int:
    """
    SuperFastHash implementation
    Port of the original C hash function from http://www.azillionmonkeys.com/qed/hash.html
    """
    if not data:
        return 0

    data_bytes = data.encode("utf-8")
    length = len(data_bytes)
    hash_val = length

    # Main loop - process 4 bytes at a time
    i = 0
    while length >= 4:
        # Get 16-bit values using the same byte order as C version
        # sfh_get16(d) = (d[1] << 8) + d[0] for non-i386 (most systems)
        val1 = data_bytes[i] | (data_bytes[i + 1] << 8)
        val2 = data_bytes[i + 2] | (data_bytes[i + 3] << 8)

        hash_val += val1
        tmp = (val2 << 11) ^ hash_val
        hash_val = ((hash_val << 16) ^ tmp) & 0xFFFFFFFF
        hash_val += hash_val >> 11
        hash_val &= 0xFFFFFFFF

        i += 4
        length -= 4

    # Handle remaining bytes (rem = length & 3)
    # Note: i now points to the start of remaining bytes
    if length == 3:
        val = data_bytes[i] | (data_bytes[i + 1] << 8)
        hash_val += val
        hash_val &= 0xFFFFFFFF
        hash_val ^= hash_val << 16
        hash_val &= 0xFFFFFFFF
        # C treats char as signed, so bytes >= 128 are negative and sign-extended
        third_byte = data_bytes[i + 2]
        if third_byte >= 128:
            # Sign extend: make it a negative 32-bit value
            third_byte = third_byte - 256
        hash_val ^= (third_byte << 18) & 0xFFFFFFFF
        hash_val &= 0xFFFFFFFF
        hash_val += hash_val >> 11
        hash_val &= 0xFFFFFFFF
    elif length == 2:
        val = data_bytes[i] | (data_bytes[i + 1] << 8)
        hash_val += val
        hash_val &= 0xFFFFFFFF
        hash_val ^= hash_val << 11
        hash_val &= 0xFFFFFFFF
        hash_val += hash_val >> 17
        hash_val &= 0xFFFFFFFF
    elif length == 1:
        # C treats char as signed, so bytes >= 128 are negative
        byte_val = data_bytes[i]
        if byte_val >= 128:
            # Sign extend: make it a negative value
            byte_val = byte_val - 256
        hash_val += byte_val
        hash_val &= 0xFFFFFFFF
        hash_val ^= hash_val << 10
        hash_val &= 0xFFFFFFFF
        hash_val += hash_val >> 1
        hash_val &= 0xFFFFFFFF

    # Force "avalanching" of final 127 bits
    hash_val ^= hash_val << 3
    hash_val &= 0xFFFFFFFF
    hash_val += hash_val >> 5
    hash_val &= 0xFFFFFFFF
    hash_val ^= hash_val << 4
    hash_val &= 0xFFFFFFFF
    hash_val += hash_val >> 17
    hash_val &= 0xFFFFFFFF
    hash_val ^= hash_val << 25
    hash_val &= 0xFFFFFFFF
    hash_val += hash_val >> 6
    hash_val &= 0xFFFFFFFF

    return hash_val & 0xFFFFFFFF


def extract_string(line: str) -> Optional[str]:
    """
    Extract quoted string from a PO file line
    Handles escape sequences properly
    """
    # Find the first quote
    quote_start = line.find('"')
    if quote_start == -1:
        return None

    result = []
    i = quote_start + 1
    escape = False

    while i < len(line):
        char = line[i]

        if escape:
            if char in ['"', "\\"]:
                result.append(char)
            elif char == "n":
                result.append("\n")
            elif char == "t":
                result.append("\t")
            elif char == "r":
                result.append("\r")
            else:
                result.append(char)
            escape = False
        else:
            if char == "\\":
                escape = True
            elif char == '"':
                break
            else:
                result.append(char)
        i += 1

    return "".join(result) if not escape else None


def parse_po_file(filename: str) -> List[Tuple[str, str]]:
    """
    Parse PO file and extract msgid/msgstr pairs
    Returns list of (msgid, msgstr) tuples
    """
    entries = []

    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Split into blocks separated by empty lines
    blocks = re.split(r"\n\s*\n", content)

    entry_count = 0
    for block in blocks:
        lines = block.strip().split("\n")
        if not lines:
            continue

        msgid = ""
        msgstr = ""
        in_msgid = False
        in_msgstr = False

        for line in lines:
            line = line.strip()

            # Skip comments
            if line.startswith("#") or not line:
                continue

            if line.startswith("msgid "):
                # Start of msgid
                in_msgid = True
                in_msgstr = False
                extracted = extract_string(line[6:])  # Remove 'msgid '
                if extracted is not None:
                    msgid = extracted
                continue

            elif line.startswith("msgstr "):
                # Start of msgstr
                in_msgid = False
                in_msgstr = True
                extracted = extract_string(line[7:])  # Remove 'msgstr '
                if extracted is not None:
                    msgstr = extracted
                continue

            elif line.startswith('"') and (in_msgid or in_msgstr):
                # Continuation line
                extracted = extract_string(line)
                if extracted is not None:
                    if in_msgid:
                        msgid += extracted
                    elif in_msgstr:
                        msgstr += extracted
                continue

        # Add entry if both msgid and msgstr are present and non-empty
        if msgid and msgstr:
            entry_count += 1
            logging.debug("Entry #%d:", entry_count)
            logging.debug("  msgid: %r (len=%d)", msgid, len(msgid.encode("utf-8")))
            logging.debug("  msgstr: %r (len=%d)", msgstr, len(msgstr.encode("utf-8")))
            key_hash = sfh_hash(msgid)
            val_hash = sfh_hash(msgstr)
            logging.debug("  key_hash: 0x%08x", key_hash)
            logging.debug("  val_hash: 0x%08x", val_hash)
            if key_hash == val_hash:
                logging.debug("  -> WILL BE SKIPPED (same hash)")
            else:
                logging.debug("  -> INCLUDED")
            entries.append((msgid, msgstr))

    return entries


def write_lmo_file(entries: List[Tuple[str, str]], output_filename: str) -> None:
    """
    Write entries to LMO binary format file
    """
    if not entries:
        # No entries, don't create file
        if os.path.exists(output_filename):
            os.unlink(output_filename)
        return

    lmo_entries = []
    offset = 0
    included_count = 0

    logging.debug("Processing %d entries for LMO file...", len(entries))

    with open(output_filename, "wb") as f:
        # First pass: write string data and collect index entries
        for i, (msgid, msgstr) in enumerate(entries, 1):
            key_id = sfh_hash(msgid)
            val_id = sfh_hash(msgstr)

            logging.debug("Processing entry #%d:", i)
            logging.debug("  msgid: %r", msgid)
            logging.debug("  msgstr: %r", msgstr)
            logging.debug("  key_hash: 0x%08x", key_id)
            logging.debug("  val_hash: 0x%08x", val_id)

            # Skip if key and value hash to the same value
            if key_id == val_id:
                logging.debug("  -> SKIPPED (same hash)")
                continue

            # Write the string data (padded to 4-byte boundary)
            msgstr_bytes = msgstr.encode("utf-8")
            length = len(msgstr_bytes)
            padded_length = (length + 3) & ~3  # Round up to multiple of 4

            logging.debug(
                "  offset: %d, length: %d, padded_length: %d",
                offset,
                length,
                padded_length,
            )
            logging.debug("  -> INCLUDED")

            f.write(msgstr_bytes)
            if padded_length > length:
                f.write(b"\x00" * (padded_length - length))

            # Create index entry
            entry = LMOEntry(key_id, val_id, offset, length)
            lmo_entries.append(entry)
            offset += padded_length
            included_count += 1

        logging.debug("Total entries included: %d", included_count)
        logging.debug("Total string data size: %d bytes", offset)

        # Check for duplicate key IDs
        key_to_entry = {}
        for i, entry in enumerate(lmo_entries):
            if entry.key_id in key_to_entry:
                # Found duplicate key - print error and exit
                print("ERROR: Duplicate key ID detected!", file=sys.stderr)
                print(f"Key ID: 0x{entry.key_id:08x}", file=sys.stderr)

                # Find original strings for both entries
                original_msgid = None
                current_msgid = None

                # Find the original strings by matching offset and length
                for msgid, msgstr in entries:
                    if sfh_hash(msgid) == entry.key_id:
                        if current_msgid is None:
                            current_msgid = msgid
                        elif original_msgid is None:
                            original_msgid = msgid

                if original_msgid and current_msgid:
                    print(
                        f"Original string: {repr(original_msgid)}",
                        file=sys.stderr,
                    )
                else:
                    print(
                        "Unable to retrieve original strings for duplicate key",
                        file=sys.stderr,
                    )

                print("Cannot create LMO file with duplicate keys.", file=sys.stderr)
                sys.exit(1)
            else:
                key_to_entry[entry.key_id] = i

        # Second pass: write sorted index
        logging.debug("Sorting and writing %d index entries...", len(lmo_entries))
        lmo_entries.sort(key=lambda x: x.key_id)

        for entry in lmo_entries:
            logging.debug(
                "Index entry: key_id=0x%08x, val_id=0x%08x, offset=%d, length=%d",
                entry.key_id,
                entry.val_id,
                entry.offset,
                entry.length,
            )
            f.write(struct.pack(">I", entry.key_id))
            f.write(struct.pack(">I", entry.val_id))
            f.write(struct.pack(">I", entry.offset))
            f.write(struct.pack(">I", entry.length))

        # Write offset value at the end
        if offset > 0:
            logging.debug("Index offset written: %d", offset)
            f.write(struct.pack(">I", offset))
            f.flush()
            os.fsync(f.fileno())


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Convert PO files to LMO binary format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: %(prog)s input.po output.lmo",
    )
    parser.add_argument("input_file", help="Input PO file")
    parser.add_argument("output_file", help="Output LMO file")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    # Setup logging
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG, format="[DEBUG] %(message)s", stream=sys.stderr
        )
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        # Parse PO file
        entries = parse_po_file(args.input_file)
        logging.debug(f"Parsed {len(entries)} translation entries")

        # Write LMO file
        write_lmo_file(entries, args.output_file)
        logging.debug(f"Generated LMO file: {args.output_file}")

    except FileNotFoundError:
        print(f"Error: Cannot open input file '{args.input_file}'", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(
            f"Error: Cannot write to output file '{args.output_file}'", file=sys.stderr
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
