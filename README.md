# ClipLogger

A clipboard monitoring tool that logs text and file operations with storage type detection.

## Features

- Monitor clipboard for text and file operations
- Detect file paste operations across all drives
- Categorize storage types (internal, external, network, optical)
- Real-time file system monitoring
- Comprehensive logging with timestamps

## Installation

1. Install dependencies:

```bash
poetry install
```

## Usage

Run the clipboard logger:

```bash
poetry run python cliplogger/main.py
```

Or activate the Poetry shell and run:

```bash
poetry shell
python cliplog.py
```

## Requirements

- Windows OS
- Python 3.8+
- Administrator privileges (for file system monitoring)

## Dependencies

- pywin32: Windows API access
- watchdog: File system monitoring
- psutil: System information
- wmi: Windows Management Instrumentation
