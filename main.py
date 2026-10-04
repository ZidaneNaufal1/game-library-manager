import sqlite3
import tkinter as tk
from tkinter import font, messagebox, ttk

from database import (
    STATUSES,
    add_game,
    delete_game,
    get_game,
    get_games,
    initialize_database,
    update_game,
)


# Zimuru Style v1.0 — shared design tokens
COLORS = {
    "background": "#080D14",
    "surface": "#111923",
    "raised": "#182330",
    "text": "#F3F7FC",
    "muted": "#A7B6C8",
    "accent": "#8CCFFF",
    "accent_hover": "#B1DFFF",
    "border": "#29313B",
    "active": "#172B3E",
    "selected": "#23445E",
    "danger": "#FFB4B4",
    "danger_surface": "#302029",
}

SPACE = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
}

PLATFORMS = (
    "PC", "PlayStation", "Xbox", "Nintendo Switch", "Mobile"
)

GENRES = (
    "Action", "Adventure", "RPG", "FPS", "Horror",
    "Simulation", "Strategy", "Puzzle", "Platformer",
    "Sandbox", "Sports", "Racing",
)

STATUS_COLORS = {
    "Backlog": "#A7B6C8",
    "Playing": "#8CCFFF",
    "Completed": "#A7E0C0",
    "Dropped": "#E6C18A",
}


class GameLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Library · Zimuru")
        self.root.geometry("1180x740")
        self.root.minsize(960, 600)
        self.root.configure(bg=COLORS["background"])

        available_fonts = set(font.families())
        self.font_family = next(
            (
                name for name in (
                    "Inter", "Segoe UI", "Noto Sans",
                    "DejaVu Sans", "Arial"
                )
                if name in available_fonts
            ),
            "TkDefaultFont",
        )

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Semua")
        self.summary_var = tk.StringVar()
        self.footer_var = tk.StringVar()
        self.empty_var = tk.StringVar()

        self.nav_items = {}
        self.configure_styles()
        self.build_ui()
        self.refresh_table()

    def configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            ".",
            font=(self.font_family, 11),
            background=COLORS["surface"],
            foreground=COLORS["text"],
        )

        style.configure(
            "TButton",
            padding=(SPACE["lg"], 10),
            background=COLORS["raised"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["raised"],
            darkcolor=COLORS["raised"],
            relief="flat",
            focusthickness=1,
            focuscolor=COLORS["accent"],
        )
        style.map(
            "TButton",
            background=[
                ("disabled", COLORS["surface"]),
                ("active", COLORS["active"]),
            ],
            foreground=[
                ("disabled", "#6E7C8D"),
                ("active", COLORS["text"]),
            ],
            bordercolor=[
                ("focus", COLORS["accent"]),
                ("active", "#476175"),
            ],
        )

        style.configure(
            "Primary.TButton",
            background=COLORS["accent"],
            foreground=COLORS["background"],
            bordercolor=COLORS["accent"],
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"],
            font=(self.font_family, 11, "bold"),
            focuscolor=COLORS["background"],
        )
        style.map(
            "Primary.TButton",
            background=[("active", COLORS["accent_hover"])],
            foreground=[("active", COLORS["background"])],
            bordercolor=[
                ("focus", COLORS["text"]),
                ("active", COLORS["accent_hover"]),
            ],
        )

        style.configure(
            "Danger.TButton",
            background=COLORS["danger_surface"],
            foreground=COLORS["danger"],
            bordercolor="#573843",
            focuscolor=COLORS["danger"],
        )
        style.map(
            "Danger.TButton",
            background=[
                ("disabled", COLORS["surface"]),
                ("active", "#452A34"),
            ],
            foreground=[
                ("disabled", "#6E7C8D"),
                ("active", COLORS["danger"]),
            ],
            bordercolor=[
                ("focus", COLORS["danger"]),
                ("active", "#80505D"),
            ],
        )

        style.configure(
            "TEntry",
            padding=10,
            fieldbackground=COLORS["background"],
            foreground=COLORS["text"],
            insertcolor=COLORS["accent"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["background"],
            darkcolor=COLORS["background"],
        )
        style.map(
            "TEntry",
            bordercolor=[("focus", COLORS["accent"])],
        )

        style.configure(
            "TCombobox",
            padding=9,
            fieldbackground=COLORS["background"],
            background=COLORS["raised"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["muted"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["background"],
            darkcolor=COLORS["background"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", COLORS["background"]),
            ],
            foreground=[("readonly", COLORS["text"])],
            bordercolor=[("focus", COLORS["accent"])],
            selectbackground=[("readonly", COLORS["active"])],
            selectforeground=[("readonly", COLORS["text"])],
        )

        self.root.option_add(
            "*TCombobox*Listbox.background", COLORS["raised"]
        )
        self.root.option_add(
            "*TCombobox*Listbox.foreground", COLORS["text"]
        )
        self.root.option_add(
            "*TCombobox*Listbox.selectBackground", COLORS["selected"]
        )
        self.root.option_add(
            "*TCombobox*Listbox.selectForeground", COLORS["text"]
        )

        style.configure(
            "Library.Treeview",
            background=COLORS["surface"],
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            rowheight=48,
            borderwidth=0,
            font=(self.font_family, 11),
        )
        style.map(
            "Library.Treeview",
            background=[("selected", COLORS["selected"])],
            foreground=[("selected", COLORS["text"])],
        )

        style.configure(
            "Library.Treeview.Heading",
            background=COLORS["raised"],
            foreground=COLORS["muted"],
            padding=(SPACE["md"], SPACE["lg"]),
            font=(self.font_family, 10, "bold"),
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "Library.Treeview.Heading",
            background=[("active", COLORS["active"])],
        )

        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["border"],
            troughcolor=COLORS["surface"],
            arrowcolor=COLORS["muted"],
            borderwidth=0,
            arrowsize=12,
        )

    def label(self, parent, text, size=11, color=None, bold=False):
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=color or COLORS["text"],
            font=(
                self.font_family,
                size,
                "bold" if bold else "normal",
            ),
        )

    def build_ui(self):
        sidebar = tk.Frame(
            self.root,
            bg=COLORS["surface"],
            width=190,
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=COLORS["surface"])
        brand.pack(fill="x", padx=SPACE["xl"], pady=SPACE["xxl"])

        self.label(
            brand, "ZIMURU", 16, COLORS["accent"], True
        ).pack(anchor="w")

        self.label(
            brand, "Game Library", 10, COLORS["muted"]
        ).pack(anchor="w", pady=(SPACE["xs"], 0))

        tk.Frame(
            sidebar, bg=COLORS["border"], height=1
        ).pack(fill="x", padx=SPACE["xl"], pady=(0, SPACE["xl"]))

        for status, title in (
            ("Semua", "Semua game"),
            ("Backlog", "Backlog"),
            ("Playing", "Playing"),
            ("Completed", "Completed"),
            ("Dropped", "Dropped"),
        ):
            item = tk.Frame(sidebar, bg=COLORS["surface"])
            item.pack(fill="x", pady=SPACE["xs"])

            indicator = tk.Frame(
                item, width=2, bg=COLORS["surface"]
            )
            indicator.pack(side="left", fill="y")

            button = tk.Button(
                item,
                text=title,
                command=lambda value=status: self.select_status(value),
                font=(self.font_family, 11),
                anchor="w",
                padx=22,
                pady=12,
                bg=COLORS["surface"],
                fg=COLORS["muted"],
                activebackground=COLORS["active"],
                activeforeground=COLORS["accent"],
                relief="flat",
                borderwidth=0,
                highlightthickness=1,
                highlightbackground=COLORS["surface"],
                highlightcolor=COLORS["accent"],
                cursor="hand2",
            )
            button.pack(side="left", fill="x", expand=True)
            self.nav_items[status] = (indicator, button)

        self.label(
            sidebar,
            "Koleksi pribadi\nDisimpan lokal",
            9,
            COLORS["muted"],
        ).pack(side="bottom", anchor="w", padx=24, pady=24)

        page = tk.Frame(self.root, bg=COLORS["background"])
        page.pack(
            side="left",
            fill="both",
            expand=True,
            padx=SPACE["xxl"],
            pady=SPACE["xxl"],
        )

        header = tk.Frame(page, bg=COLORS["background"])
        header.pack(fill="x", pady=(0, SPACE["xl"]))

        heading = tk.Frame(header, bg=COLORS["background"])
        heading.pack(side="left")

        self.label(
            heading, "Koleksi game", 25, bold=True
        ).pack(anchor="w")

        tk.Label(
            heading,
            textvariable=self.summary_var,
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=(self.font_family, 11),
        ).pack(anchor="w", pady=(SPACE["sm"], 0))

        ttk.Button(
            header,
            text="+  Tambah Game",
            style="Primary.TButton",
            command=self.open_game_form,
        ).pack(side="right")

        filters = tk.Frame(
            page,
            bg=COLORS["raised"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        filters.pack(fill="x", pady=(0, SPACE["xl"]))
        filters.columnconfigure(0, weight=1)

        self.label(
            filters, "Cari judul", 9, COLORS["muted"]
        ).grid(
            row=0, column=0, sticky="w",
            padx=SPACE["lg"], pady=(SPACE["md"], SPACE["sm"]),
        )

        self.label(
            filters, "Status", 9, COLORS["muted"]
        ).grid(
            row=0, column=1, sticky="w",
            padx=(0, SPACE["md"]),
            pady=(SPACE["md"], SPACE["sm"]),
        )

        search_entry = ttk.Entry(
            filters, textvariable=self.search_var
        )
        search_entry.grid(
            row=1, column=0, sticky="ew",
            padx=SPACE["lg"], pady=(0, SPACE["lg"]),
        )
        search_entry.bind(
            "<Return>", lambda event: self.refresh_table()
        )

        status_filter = ttk.Combobox(
            filters,
            textvariable=self.status_var,
            values=("Semua", *STATUSES),
            state="readonly",
            width=12,
        )
        status_filter.grid(
            row=1, column=1,
            padx=(0, SPACE["md"]), pady=(0, SPACE["lg"]),
        )
        status_filter.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_table(),
        )

        ttk.Button(
            filters, text="Cari", command=self.refresh_table
        ).grid(
            row=1, column=2,
            padx=(0, SPACE["sm"]), pady=(0, SPACE["lg"]),
        )

        ttk.Button(
            filters, text="Reset", command=self.reset_filters
        ).grid(
            row=1, column=3,
            padx=(0, SPACE["lg"]), pady=(0, SPACE["lg"]),
        )

        panel = tk.Frame(
            page,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        panel.pack(fill="both", expand=True)

        panel_header = tk.Frame(panel, bg=COLORS["surface"])
        panel_header.pack(
            fill="x", padx=SPACE["xl"], pady=SPACE["lg"]
        )

        self.label(
            panel_header, "Library", 13, bold=True
        ).pack(side="left")

        self.edit_button = ttk.Button(
            panel_header,
            text="Edit",
            command=self.edit_selected,
            state="disabled",
        )
        self.edit_button.pack(side="right", padx=(0, SPACE["md"]))

        self.delete_button = ttk.Button(
            panel_header,
            text="Hapus",
            style="Danger.TButton",
            command=self.delete_selected,
            state="disabled",
        )
        self.delete_button.pack(side="right", padx=(SPACE["lg"], 0))

        table_area = tk.Frame(panel, bg=COLORS["surface"])
        table_area.pack(
            fill="both", expand=True,
            padx=SPACE["lg"], pady=(0, SPACE["md"]),
        )

        columns = ("title", "platform", "genre", "status", "rating")
        self.table = ttk.Treeview(
            table_area,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Library.Treeview",
        )

        for column, heading, width in (
            ("title", "Judul game", 250),
            ("platform", "Platform", 110),
            ("genre", "Genre", 110),
            ("status", "Status", 120),
            ("rating", "Rating", 80),
        ):
            self.table.heading(column, text=heading, anchor="w")
            self.table.column(
                column, width=width, minwidth=70, anchor="w"
            )

        self.table.column("title", minwidth=160)
        self.table.column("rating", anchor="center")
        self.table.heading("rating", anchor="center")

        for status, color in STATUS_COLORS.items():
            self.table.tag_configure(status, foreground=color)

        self.table.tag_configure(
            "even", background=COLORS["surface"]
        )
        self.table.tag_configure(
            "odd", background="#141E29"
        )

        scrollbar = ttk.Scrollbar(
            table_area,
            orient="vertical",
            command=self.table.yview,
        )
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)

        self.table.bind(
            "<<TreeviewSelect>>", lambda event: self.update_actions()
        )
        self.table.bind("<Double-1>", self.on_double_click)

        self.empty_label = tk.Label(
            table_area,
            textvariable=self.empty_var,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(self.font_family, 11),
            justify="center",
        )

        bottom = tk.Frame(panel, bg=COLORS["surface"])
        bottom.pack(
            fill="x", padx=SPACE["xl"], pady=(0, SPACE["lg"])
        )

        tk.Label(
            bottom,
            textvariable=self.footer_var,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(self.font_family, 9),
        ).pack(side="left")

        ttk.Button(
            bottom,
            text="Muat ulang",
            command=self.refresh_table,
        ).pack(side="right")

        self.label(
            page,
            "Klik dua kali pada game untuk mengedit.",
            9,
            COLORS["muted"],
        ).pack(anchor="w", pady=(SPACE["lg"], 0))

    def update_navigation(self):
        selected = self.status_var.get()

        for status, (indicator, button) in self.nav_items.items():
            active = status == selected
            background = (
                COLORS["active"] if active else COLORS["surface"]
            )
            indicator.configure(
                bg=COLORS["accent"] if active else COLORS["surface"]
            )
            button.configure(
                bg=background,
                fg=COLORS["accent"] if active else COLORS["muted"],
                highlightbackground=background,
            )

    def update_actions(self):
        state = "!disabled" if self.table.selection() else "disabled"
        self.edit_button.state([state])
        self.delete_button.state([state])

    def select_status(self, status):
        self.status_var.set(status)
        self.refresh_table()

    def reset_filters(self):
        self.search_var.set("")
        self.status_var.set("Semua")
        self.refresh_table()

    def refresh_table(self, select_id=None):
        self.update_navigation()

        try:
            all_games = get_games()
        except sqlite3.Error as error:
            messagebox.showerror(
                "Gagal membaca koleksi",
                str(error),
                parent=self.root,
            )
            return

        keyword = self.search_var.get().strip().casefold()
        status = self.status_var.get()

        games = [
            game for game in all_games
            if keyword in game[1].casefold()
            and (status == "Semua" or game[4] == status)
        ]

        for item in self.table.get_children():
            self.table.delete(item)

        for index, game in enumerate(games):
            game_id, title, platform, genre, game_status, rating = game

            self.table.insert(
                "",
                "end",
                iid=str(game_id),
                values=(
                    title,
                    platform,
                    genre,
                    game_status,
                    "-" if rating is None else f"{rating:g}/10",
                ),
                tags=(
                    "even" if index % 2 == 0 else "odd",
                    game_status,
                ),
            )

        self.summary_var.set(f"{len(all_games)} game dalam koleksi")
        self.footer_var.set(
            f"Menampilkan {len(games)} dari {len(all_games)} game"
        )

        if games:
            self.empty_label.place_forget()
        else:
            self.empty_var.set(
                "Koleksimu masih kosong.\nTambahkan game pertama untuk memulai."
                if not all_games
                else "Tidak ada hasil yang cocok.\nCoba judul lain atau reset filter."
            )
            self.empty_label.place(
                relx=0.5, rely=0.5, anchor="center"
            )

        if select_id is not None and self.table.exists(str(select_id)):
            self.table.selection_set(str(select_id))
            self.table.focus(str(select_id))
            self.table.see(str(select_id))

        self.update_actions()

    def selected_game(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showinfo(
                "Pilih game",
                "Pilih satu baris game terlebih dahulu.",
                parent=self.root,
            )
            return None

        try:
            game = get_game(int(selected[0]))
        except sqlite3.Error as error:
            messagebox.showerror(
                "Gagal membaca game", str(error), parent=self.root
            )
            return None

        if game is None:
            messagebox.showwarning(
                "Game tidak ditemukan",
                "Koleksi akan dimuat ulang.",
                parent=self.root,
            )
            self.refresh_table()

        return game

    def on_double_click(self, event):
        row = self.table.identify_row(event.y)

        if row:
            self.table.selection_set(row)
            self.edit_selected()

    def edit_selected(self):
        game = self.selected_game()

        if game is not None:
            self.open_game_form(game)

    def delete_selected(self):
        game = self.selected_game()

        if game is None:
            return

        game_id, title, *_ = game

        if not messagebox.askyesno(
            "Hapus game?",
            f'Hapus "{title}" dari koleksi?\n\n'
            "Data yang dihapus tidak bisa dikembalikan dari aplikasi.",
            parent=self.root,
        ):
            return

        try:
            delete_game(game_id)
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror(
                "Gagal menghapus", str(error), parent=self.root
            )
            return

        self.refresh_table()

    def open_game_form(self, game=None):
        editing = game is not None

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Game" if editing else "Tambah Game")
        dialog.configure(bg=COLORS["surface"])
        dialog.resizable(False, False)
        dialog.transient(self.root)

        form = tk.Frame(dialog, bg=COLORS["surface"])
        form.pack(
            fill="both", expand=True,
            padx=SPACE["xxl"], pady=SPACE["xl"],
        )
        form.columnconfigure(0, weight=1)

        self.label(
            form,
            "Edit game" if editing else "Tambah game",
            21,
            bold=True,
        ).grid(row=0, column=0, sticky="w")

        self.label(
            form,
            "Detail koleksi pribadi.",
            10,
            COLORS["muted"],
        ).grid(
            row=1, column=0, sticky="w", pady=(SPACE["sm"], SPACE["xl"])
        )

        if editing:
            game_id, title, platform, genre, status, rating = game
            defaults = (
                title, platform, genre, status,
                "" if rating is None else f"{rating:g}",
            )
        else:
            game_id = None
            defaults = ("", "PC", "", "Backlog", "")

        variables = [
            tk.StringVar(value=value) for value in defaults
        ]

        labels = (
            "Judul game *", "Platform *", "Genre *",
            "Status *", "Rating",
        )
        first_entry = None

        for index, (label, variable) in enumerate(zip(labels, variables)):
            row = 2 + index * 2

            self.label(
                form, label, 10, COLORS["muted"]
            ).grid(
                row=row, column=0, sticky="w", pady=(0, SPACE["sm"])
            )

            if index in (1, 2, 3):
                options = {
                    1: PLATFORMS,
                    2: GENRES,
                    3: STATUSES,
                }
                widget = ttk.Combobox(
                    form,
                    textvariable=variable,
                    values=options[index],
                    state="readonly" if index == 3 else "normal",
                    width=35,
                )
            else:
                widget = ttk.Entry(
                    form, textvariable=variable, width=37
                )

            widget.grid(
                row=row + 1, column=0, sticky="ew",
                pady=(0, SPACE["lg"]),
            )

            if index == 0:
                first_entry = widget

        self.label(
            form,
            "* Wajib diisi. Rating 0–10, boleh kosong.",
            9,
            COLORS["muted"],
        ).grid(
            row=12, column=0, sticky="w", pady=(0, SPACE["xl"])
        )

        def save():
            values = [variable.get() for variable in variables]

            try:
                if editing:
                    update_game(game_id, *values)
                    saved_id = game_id
                else:
                    saved_id = add_game(*values)
            except ValueError as error:
                messagebox.showwarning(
                    "Periksa input", str(error), parent=dialog
                )
                return
            except sqlite3.Error as error:
                messagebox.showerror(
                    "Gagal menyimpan", str(error), parent=dialog
                )
                return

            dialog.destroy()
            self.search_var.set("")
            self.status_var.set("Semua")
            self.refresh_table(select_id=saved_id)

        buttons = tk.Frame(form, bg=COLORS["surface"])
        buttons.grid(row=13, column=0, sticky="e")

        ttk.Button(
            buttons, text="Batal", command=dialog.destroy
        ).pack(side="left", padx=(0, SPACE["md"]))

        ttk.Button(
            buttons,
            text="Simpan Game",
            style="Primary.TButton",
            command=save,
        ).pack(side="left")

        dialog.bind("<Escape>", lambda event: dialog.destroy())
        dialog.update_idletasks()

        x = self.root.winfo_rootx() + (
            self.root.winfo_width() - dialog.winfo_width()
        ) // 2
        y = self.root.winfo_rooty() + (
            self.root.winfo_height() - dialog.winfo_height()
        ) // 2

        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")
        dialog.grab_set()
        first_entry.focus_set()


def main():
    root = tk.Tk()
    root.withdraw()

    try:
        initialize_database()
    except (sqlite3.Error, OSError) as error:
        messagebox.showerror(
            "Database bermasalah",
            f"Database tidak bisa disiapkan:\n{error}",
            parent=root,
        )
        root.destroy()
        return

    GameLibraryApp(root)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()