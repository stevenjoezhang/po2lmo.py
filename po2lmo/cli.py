"""
Command line interface for po2lmo
"""

import sys
import argparse
import logging
from .core import parse_po_file, write_lmo_file


def main():
    """Main function for command line interface"""
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
