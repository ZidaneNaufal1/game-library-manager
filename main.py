import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from database import (
    STATUSES,
    add_game,
    delete_game,
    get_game,
    get_games,
    initialize_database,
    update_game,
)


BACKGROUND = "#e0f2fe"
TEXT_COLOR = "#075985"

PLATFORMS = (
    "PC",
    "PlayStation",
    "Xbox",
    "Nintendo Switch",
    "Mobile",
)

GENRES = (
    "Action",
    "Adventure",
    "RPG",
    "FPS",
    "Horror",
    "Simulation",
    "Strategy",
    "Puzzle",
    "Platformer",
    "Sandbox",
    "Sports",
    "Racing",
)


def main():
    window = tk.Tk()
    window.withdraw()

    try:
        initialize_database()
    except (sqlite3.Error, OSError) as error:
        messagebox.showerror(
            "Database bermasalah",
            f"Database tidak bisa disiapkan:\n{error}",
            parent=window,
        )
        window.destroy()
        return

    window.title("Game Library Manager")
    window.geometry("900x550")
    window.minsize(700, 400)
    window.configure(bg=BACKGROUND)

    header = tk.Frame(window, bg=BACKGROUND)
    header.pack(fill="x", padx=24, pady=(24, 16))

    tk.Label(
        header,
        text="GAME LIBRARY MANAGER",
        font=("Arial", 22, "bold"),
        bg=BACKGROUND,
        fg="#0c4a6e",
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Kelola koleksi game dan backlog pribadimu.",
        font=("Arial", 11),
        bg=BACKGROUND,
        fg=TEXT_COLOR,
    ).pack(anchor="w", pady=(8, 0))

    toolbar = tk.Frame(window, bg=BACKGROUND)
    toolbar.pack(fill="x", padx=24, pady=(0, 12))

    table_frame = ttk.Frame(window)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=24,
        pady=(0, 16),
    )

    columns = ("title", "platform", "genre", "status", "rating")

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse",
    )

    headings = ("Judul", "Platform", "Genre", "Status", "Rating")

    for column, heading in zip(columns, headings):
        table.heading(column, text=heading)
        table.column(column, width=130, minwidth=80)

    table.column("title", width=240)

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview,
    )
    table.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    table.pack(side="left", fill="both", expand=True)

    footer_text = tk.StringVar(value="Memuat koleksi...")

    tk.Label(
        window,
        textvariable=footer_text,
        bg=BACKGROUND,
        fg=TEXT_COLOR,
        font=("Arial", 10),
    ).pack(padx=24, pady=(0, 20))

    def refresh_table(select_id=None):
        try:
            games = get_games()
        except sqlite3.Error as error:
            messagebox.showerror(
                "Gagal membaca koleksi",
                f"Data game tidak bisa dibaca:\n{error}",
                parent=window,
            )
            return

        for item in table.get_children():
            table.delete(item)

        for game in games:
            game_id, title, platform, genre, status, rating = game
            rating_display = "-" if rating is None else f"{rating:g}/10"

            table.insert(
                "",
                "end",
                iid=str(game_id),
                values=(
                    title,
                    platform,
                    genre,
                    status,
                    rating_display,
                ),
            )

        if games:
            footer_text.set(
                f"Total koleksi: {len(games)} game. "
                "Pilih baris untuk mengedit atau menghapus."
            )
        else:
            footer_text.set(
                "Koleksi masih kosong. Klik Tambah Game untuk memulai."
            )

        if select_id is not None and table.exists(str(select_id)):
            table.selection_set(str(select_id))
            table.focus(str(select_id))
            table.see(str(select_id))

    def get_selected_game():
        selection = table.selection()

        if not selection:
            messagebox.showinfo(
                "Pilih game",
                "Klik satu baris game pada tabel terlebih dahulu.",
                parent=window,
            )
            return None

        game_id = int(selection[0])

        try:
            game = get_game(game_id)
        except sqlite3.Error as error:
            messagebox.showerror(
                "Gagal membaca game",
                f"Data game tidak bisa dibaca:\n{error}",
                parent=window,
            )
            return None

        if game is None:
            messagebox.showwarning(
                "Game tidak ditemukan",
                "Game sudah tidak tersedia. Koleksi akan dimuat ulang.",
                parent=window,
            )
            refresh_table()

        return game

    def open_game_form(game=None):
        editing = game is not None

        dialog = tk.Toplevel(window)
        dialog.title("Edit Game" if editing else "Tambah Game")
        dialog.resizable(False, False)
        dialog.transient(window)

        form = ttk.Frame(dialog, padding=24)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        ttk.Label(
            form,
            text="Edit data game" if editing else "Tambah game ke koleksi",
            font=("Arial", 14, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 20),
        )

        if editing:
            game_id, title, platform, genre, status, rating = game
            rating_text = "" if rating is None else f"{rating:g}"
        else:
            game_id = None
            title = ""
            platform = "PC"
            genre = ""
            status = "Backlog"
            rating_text = ""

        title_var = tk.StringVar(value=title)
        platform_var = tk.StringVar(value=platform)
        genre_var = tk.StringVar(value=genre)
        status_var = tk.StringVar(value=status)
        rating_var = tk.StringVar(value=rating_text)

        labels = (
            "Judul *",
            "Platform *",
            "Genre *",
            "Status *",
            "Rating (0–10)",
        )

        for row, label in enumerate(labels, start=1):
            ttk.Label(form, text=label).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 16),
                pady=8,
            )

        title_entry = ttk.Entry(
            form, textvariable=title_var, width=32
        )
        title_entry.grid(row=1, column=1, sticky="ew", pady=8)

        ttk.Combobox(
            form,
            textvariable=platform_var,
            values=PLATFORMS,
            width=30,
        ).grid(row=2, column=1, sticky="ew", pady=8)

        ttk.Combobox(
            form,
            textvariable=genre_var,
            values=GENRES,
            width=30,
        ).grid(row=3, column=1, sticky="ew", pady=8)

        ttk.Combobox(
            form,
            textvariable=status_var,
            values=STATUSES,
            state="readonly",
            width=30,
        ).grid(row=4, column=1, sticky="ew", pady=8)

        ttk.Entry(
            form, textvariable=rating_var, width=32
        ).grid(row=5, column=1, sticky="ew", pady=8)

        ttk.Label(
            form,
            text="* Wajib diisi. Rating boleh kosong.",
        ).grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(12, 16),
        )

        def save_game():
            values = (
                title_var.get(),
                platform_var.get(),
                genre_var.get(),
                status_var.get(),
                rating_var.get(),
            )

            try:
                if editing:
                    update_game(game_id, *values)
                    saved_id = game_id
                else:
                    saved_id = add_game(*values)
            except ValueError as error:
                messagebox.showwarning(
                    "Periksa input",
                    str(error),
                    parent=dialog,
                )
                return
            except sqlite3.Error as error:
                messagebox.showerror(
                    "Gagal menyimpan",
                    f"Game tidak bisa disimpan:\n{error}",
                    parent=dialog,
                )
                return

            dialog.destroy()
            refresh_table(select_id=saved_id)

        buttons = ttk.Frame(form)
        buttons.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="e",
        )

        ttk.Button(
            buttons,
            text="Batal",
            command=dialog.destroy,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            buttons,
            text="Simpan",
            command=save_game,
        ).pack(side="left")

        dialog.bind("<Escape>", lambda event: dialog.destroy())
        dialog.grab_set()
        title_entry.focus_set()

    def edit_selected_game():
        game = get_selected_game()

        if game is not None:
            open_game_form(game)

    def delete_selected_game():
        game = get_selected_game()

        if game is None:
            return

        game_id, title, *_ = game

        confirmed = messagebox.askyesno(
            "Hapus game?",
            f'Hapus "{title}" dari koleksi?\n\n'
            "Data yang dihapus tidak bisa dikembalikan dari aplikasi.",
            parent=window,
        )

        if not confirmed:
            return

        try:
            delete_game(game_id)
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror(
                "Gagal menghapus",
                str(error),
                parent=window,
            )
            return

        refresh_table()

    ttk.Button(
        toolbar,
        text="+ Tambah Game",
        command=open_game_form,
    ).pack(side="left")

    ttk.Button(
        toolbar,
        text="Edit Game",
        command=edit_selected_game,
    ).pack(side="left", padx=(8, 0))

    ttk.Button(
        toolbar,
        text="Hapus Game",
        command=delete_selected_game,
    ).pack(side="left", padx=(8, 0))

    ttk.Button(
        toolbar,
        text="Muat Ulang",
        command=refresh_table,
    ).pack(side="left", padx=(8, 0))

    refresh_table()
    window.deiconify()
    window.mainloop()


if __name__ == "__main__":
    main()