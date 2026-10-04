import math
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "data" / "games.db"

STATUSES = ("Backlog", "Playing", "Completed", "Dropped")


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(length(trim(title)) > 0),
                platform TEXT NOT NULL,
                genre TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Backlog'
                    CHECK(status IN (
                        'Backlog', 'Playing', 'Completed', 'Dropped'
                    )),
                rating REAL CHECK(rating BETWEEN 0 AND 10)
            )
        """)


def validate_game(title, platform, genre, status, rating_text):
    title = title.strip()
    platform = platform.strip()
    genre = genre.strip()
    rating_text = rating_text.strip()

    if not title:
        raise ValueError("Judul game wajib diisi.")

    if not platform:
        raise ValueError("Platform wajib diisi.")

    if not genre:
        raise ValueError("Genre wajib diisi.")

    if status not in STATUSES:
        raise ValueError("Pilih status game yang tersedia.")

    rating = None

    if rating_text:
        try:
            rating = float(rating_text.replace(",", "."))
        except ValueError:
            raise ValueError(
                "Rating harus berupa angka, misalnya 8 atau 8.5."
            ) from None

        if not math.isfinite(rating) or not 0 <= rating <= 10:
            raise ValueError("Rating harus berada antara 0 dan 10.")

    return title, platform, genre, status, rating


def get_games():
    with sqlite3.connect(DB_PATH) as connection:
        return connection.execute("""
            SELECT id, title, platform, genre, status, rating
            FROM games
            ORDER BY title COLLATE NOCASE, id
        """).fetchall()


def get_game(game_id):
    with sqlite3.connect(DB_PATH) as connection:
        return connection.execute("""
            SELECT id, title, platform, genre, status, rating
            FROM games
            WHERE id = ?
        """, (game_id,)).fetchone()


def add_game(title, platform, genre, status, rating_text):
    values = validate_game(
        title, platform, genre, status, rating_text
    )

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute("""
            INSERT INTO games (title, platform, genre, status, rating)
            VALUES (?, ?, ?, ?, ?)
        """, values)

        return cursor.lastrowid


def update_game(game_id, title, platform, genre, status, rating_text):
    values = validate_game(
        title, platform, genre, status, rating_text
    )

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute("""
            UPDATE games
            SET title = ?, platform = ?, genre = ?, status = ?, rating = ?
            WHERE id = ?
        """, (*values, game_id))

        if cursor.rowcount == 0:
            raise ValueError(
                "Game sudah tidak ditemukan. Muat ulang koleksi."
            )


def delete_game(game_id):
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute("""
            DELETE FROM games
            WHERE id = ?
        """, (game_id,))

        if cursor.rowcount == 0:
            raise ValueError(
                "Game sudah tidak ditemukan. Muat ulang koleksi."
            )


if __name__ == "__main__":
    initialize_database()
    print(f"Database siap: {DB_PATH}")
    print(f"Jumlah game: {len(get_games())}")