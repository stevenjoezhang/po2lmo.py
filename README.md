# po2lmo

A Python tool for converting GNU gettext PO files to Lua Machine Objects (LMO) binary format.

## Overview

po2lmo is a Python implementation of the original C version po2lmo tool, maintaining the same binary format compatibility. It converts GNU gettext PO files to LMO format, which is used by various Lua applications.

## Features

- Fully compatible with the original C version's binary format
- Supports Python 3.7+
- Provides both command-line tool and Python API
- Handles escape sequences and multi-line strings
- Duplicate key detection and error handling
- Debug output support

## Installation

Install using pip:

```bash
pip install po2lmo
```

## Usage

### Command Line Tool

After installation, you can use the `po2lmo` command:

```bash
po2lmo input.po output.lmo
```

Enable debug output:

```bash
po2lmo --debug input.po output.lmo
```

### Python API

You can also use it in Python code:

```python
from po2lmo import parse_po_file, write_lmo_file

# Parse PO file
entries = parse_po_file('input.po')

# Write LMO file
write_lmo_file(entries, 'output.lmo')
```

## Development

### Install from Source

```bash
git clone https://github.com/stevenjoezhang/po2lmo.py.git
cd po2lmo
pip install -e .
```

### Run Tests

```bash
python -m pytest tests/
```

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Original Version

Original C version:
Copyright (C) 2009-2012 Jo-Philipp Wich <xm@subsignal.org>
