# Note Tree Generator

A simple Python tool to visualize and manage connections between Markdown notes using `[[wiki-links]]`.

## Features

- Generate hierarchical trees of connected notes
- Search and filter notes easily
- Copy tree structure to clipboard
- Create ZIP backups of connected notes
- Preserve original link order
- Alphabetically sorted file list

## Requirements

- Python 3.x (with Tkinter)

## Installation

### Windows
1. Install Python:
   - Download from [Python.org](https://www.python.org/downloads/)
   - Run installer and check "Add Python to PATH"
   - Click "Install Now"

2. Get Note Tree Generator:
   - Download and extract ZIP from this repository
   - Open Command Prompt (Win + R, type `cmd`, press Enter)
   ```cmd
   cd path\to\extracted\folder
   python ntg4o.py
   ```

### Linux
1. Install Python (if not installed):
   ```bash
   sudo apt install python3 python3-tk
   ```

2. Run the program:
   ```bash
   python3 ntg4o.py
   ```

## Quick Start

1. Launch the program
2. Click "Search" to select your notes folder
3. Select any note to view its connections
4. Use available actions:
   - **Copy**: Get tree structure to clipboard
   - **ZIP**: Create backup with all connected notes

## Note Format

Uses standard Markdown files (.md) with wiki-style links:

```markdown
[[Note Name]]
```

Example structure:
```markdown
# Topic
1. [[First Note]]
   1. [[Sub Note A]]
   2. [[Sub Note B]]
2. [[Second Note]]
```