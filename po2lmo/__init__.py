"""
po2lmo - PO to LMO conversion tool

A Python implementation of the po2lmo tool for converting GNU gettext PO files
to Lua Machine Objects (LMO) binary format.

This package provides both a Python API and a command-line tool for converting
PO files to the LMO format used by various Lua applications.
"""

__version__ = '1.0.0'
__author__ = 'Shuqiao Zhang'
__email__ = 'stevenjoezhang@gmail.com'

from .core import (
    LMOEntry,
    sfh_hash,
    extract_string,
    parse_po_file,
    write_lmo_file,
)

__all__ = [
    'LMOEntry',
    'sfh_hash',
    'extract_string',
    'parse_po_file',
    'write_lmo_file',
]
