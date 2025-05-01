# Note Tree Generator

A simple Python application that helps you visualize and manage the connections between your Markdown notes that use the `[[wiki-link]]` format.

## Features

- Generate a hierarchical tree view of your connected notes
- Search through your notes easily
- Copy the tree structure to clipboard
- Create ZIP files containing all connected notes
- Maintains the original order of links in your notes
- Alphabetically sorted file list

## Requirements

- Python 3.x
- Tkinter (usually comes with Python)

## How to Use

1. Run the program:
   ```
   python ntg4o.py
   ```

2. Click "Buscar" (Search) to select your notes folder
3. Select a note from the list to see its connection tree
4. Use the search bar to filter your notes
5. Use the buttons to:
   - Copy the tree structure to clipboard
   - Create a ZIP file with all connected notes

## Note Format

The program works with Markdown files (.md) that use the double-bracket wiki-link format:

```markdown
[[Note Name]]
```

It will generate a tree structure showing all the connections between your notes, maintaining the order in which links appear in your files.