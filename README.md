# 🎮 Game Library Manager

A desktop application for organizing a personal game collection
and tracking gaming progress.

Built with Python, Tkinter, and SQLite.

## Features

- Add games with title, platform, genre, status, and optional rating.
- View saved games in a table.
- Edit selected games.
- Delete games with confirmation.
- Search titles without case sensitivity.
- Filter games by status.
- Combine title search and status filtering.
- Store the collection locally in SQLite.
- Validate required fields and ratings from 0 to 10.

## Game Statuses

| Status | Meaning |
|---|---|
| Backlog | Not started yet |
| Playing | Currently playing |
| Completed | Finished |
| Dropped | Stopped playing |

## Requirements

- Python 3.8 or newer
- Tkinter
- A desktop environment that can display GUI windows

SQLite is included with Python. No packages from pip are required.

## Run the Application

From the project folder:

```bash
python3 main.py
```

On Windows with the Python launcher:

```powershell
py main.py
```

For Ubuntu, install Tkinter if it is missing:

```bash
sudo apt update
sudo apt install python3-tk
```

Check GUI support:

```bash
python3 -m tkinter
```

When using WSL, GUI application support must be available.

## Usage

1. Click **Tambah Game** to add a game.
2. Select a table row and click **Edit Game** to update it.
3. Select a table row and click **Hapus Game** to delete it.
4. Enter part of a title and click **Cari**, or press Enter.
5. Choose a status to filter the results.
6. Click **Reset** to show the entire collection.

Platform and genre can be selected or typed manually.
Ratings are optional. Decimal points and decimal commas are accepted.

Saving a new or edited game resets the filters and selects the saved row.

## Project Files

| File | Purpose |
|---|---|
| `main.py` | GUI, forms, search, and filters |
| `database.py` | SQLite storage, validation, and CRUD operations |
| `.gitignore` | Excludes local data and generated files |
| `data/games.db` | Local database, created automatically |

The database is not included in Git.
Each user starts with their own empty collection.

## Manual Verification

- Add a game and check that it appears in the table.
- Restart the application and check that the game remains.
- Edit a game and verify that the changes persist after restarting.
- Cancel deletion and verify that the game remains.
- Confirm deletion and verify that the game is removed.
- Try an empty title and an invalid rating.
- Search with different letter cases.
- Combine a title search with a status filter.
- Reset the filters and verify that all games return.

## Current Limitations

- Local storage only; no cloud synchronization.
- No automatic import from Steam or other platforms.
- No packaged executable yet.
- Search currently filters the collection in Python.

## Learning Goals

Practice desktop GUI development, SQL CRUD operations,
input validation, modular Python code, and Git version control.

## Author

Muhammad Zidane Naufal Azzam  
GitHub: [ZidaneNaufal1](https://github.com/ZidaneNaufal1)