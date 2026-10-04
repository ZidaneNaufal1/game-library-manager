import sqlite3
import tkinter as tk
from tkinter import font, messagebox, ttk

from database import (
    STATUSES, add_game, delete_game, get_game, get_games,
    initialize_database, update_game,
)
from pearl_ui import (
    COLORS, STATUS_COLORS, STATUS_LABELS, STATUS_SURFACES, PearlPanel, draw_cover,
)


# Zimuru Style v1.1 — Pearl White. Shared surfaces live in pearl_ui.py.
SPACE = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "xxl": 32}
PLATFORMS = ("PC", "PlayStation", "Xbox", "Nintendo Switch", "Mobile")
GENRES = (
    "Action", "Adventure", "RPG", "FPS", "Horror", "Simulation", "Strategy",
    "Puzzle", "Platformer", "Sandbox", "Sports", "Racing",
)


class GameLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Library · Zimuru Pearl White")
        height = max(620, min(820, self.root.winfo_screenheight() - 70))
        self.root.geometry(f"1180x{height}")
        self.root.minsize(900, 620)
        self.root.configure(bg=COLORS["surface"])
        available_fonts = {name.casefold(): name for name in font.families()}
        self.font_family = next(
            (available_fonts[name.casefold()] for name in (
                "Inter", "Segoe UI", "Noto Sans", "DejaVu Sans", "Arial",
                "Nimbus Sans L", "Helvetica",
            ) if name.casefold() in available_fonts), "TkDefaultFont",
        )
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Semua")
        self.view_var = tk.StringVar(value="Kartu")
        self.summary_var = tk.StringVar()
        self.footer_var = tk.StringVar()
        self.empty_var = tk.StringVar()
        self.heading_var = tk.StringVar(value="Koleksi game.")
        self.nav_items = {}
        self.nav_counts = {status: tk.StringVar(value="0") for status in STATUS_LABELS}
        self.visible_games = []
        self.card_panels = {}
        self._search_job = None
        self._layout_job = None
        self._card_columns = 0
        self.configure_styles()
        self.build_ui()
        self.search_var.trace_add("write", self.schedule_search)
        self.root.bind("<MouseWheel>", self.scroll_cards, add="+")
        self.root.bind("<Button-4>", self.scroll_cards, add="+")
        self.root.bind("<Button-5>", self.scroll_cards, add="+")
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
            focuscolor=COLORS["link"],
        )
        style.map(
            "TButton",
            background=[
                ("disabled", COLORS["surface"]),
                ("active", COLORS["active"]),
            ],
            foreground=[
                ("disabled", COLORS["disabled"]),
                ("active", COLORS["text"]),
            ],
            bordercolor=[
                ("focus", COLORS["link"]),
                ("active", COLORS["border"]),
            ],
        )

        style.configure(
            "Primary.TButton",
            background=COLORS["accent"],
            foreground=COLORS["text"],
            bordercolor=COLORS["accent"],
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"],
            font=(self.font_family, 11, "bold"),
            focuscolor=COLORS["link"],
        )
        style.map(
            "Primary.TButton",
            background=[("active", COLORS["accent_hover"])],
            foreground=[("active", COLORS["text"])],
            bordercolor=[
                ("focus", COLORS["link"]),
                ("active", COLORS["accent_hover"]),
            ],
        )

        style.configure(
            "Danger.TButton",
            background=COLORS["danger_surface"],
            foreground=COLORS["danger"],
            bordercolor=COLORS["danger_border"],
            focuscolor=COLORS["danger"],
        )
        style.map(
            "Danger.TButton",
            background=[
                ("disabled", COLORS["surface"]),
                ("active", COLORS["danger_hover"]),
            ],
            foreground=[
                ("disabled", COLORS["disabled"]),
                ("active", COLORS["danger"]),
            ],
            bordercolor=[
                ("focus", COLORS["danger"]),
                ("active", COLORS["danger_border"]),
            ],
        )

        style.configure(
            "TEntry",
            padding=10,
            fieldbackground=COLORS["background"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["background"],
            darkcolor=COLORS["background"],
        )
        style.map(
            "TEntry",
            bordercolor=[("focus", COLORS["link"])],
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
            bordercolor=[("focus", COLORS["link"])],
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
            background=COLORS["surface"],
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
        top = tk.Frame(self.root, bg=COLORS["surface"])
        top.pack(fill="x")
        brand = tk.Frame(top, bg=COLORS["surface"])
        brand.pack(side="left", padx=28, pady=18)
        self.label(brand, "zimuru", 22, bold=True).pack(side="left")
        self.label(brand, ".", 22, COLORS["link"], True).pack(side="left")
        self.label(top, "YOUR PERSONAL GAME LIBRARY", 9, COLORS["muted"]).pack(
            side="right", padx=32,
        )
        tk.Frame(self.root, height=1, bg=COLORS["border"]).pack(fill="x")

        shell = tk.Frame(self.root, bg=COLORS["surface"])
        shell.pack(fill="both", expand=True)
        sidebar = tk.Frame(shell, bg=COLORS["sidebar"], width=188)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self.label(sidebar, "LIBRARY", 9, COLORS["muted"]).pack(
            anchor="w", padx=24, pady=(30, 14),
        )
        for status, title in STATUS_LABELS.items():
            item = tk.Frame(sidebar, bg=COLORS["sidebar"])
            item.pack(fill="x", padx=12, pady=4)
            indicator = tk.Frame(item, width=2, bg=COLORS["sidebar"])
            indicator.pack(side="left", fill="y")
            count = tk.Label(item, textvariable=self.nav_counts[status],
                             bg=COLORS["sidebar"], fg=COLORS["muted"],
                             font=(self.font_family, 9), padx=8)
            count.pack(side="right", fill="y")
            button = tk.Button(
                item, text=title, command=lambda value=status: self.select_status(value),
                font=(self.font_family, 10), anchor="w", padx=10, pady=12,
                bg=COLORS["sidebar"], fg=COLORS["muted"],
                activebackground=COLORS["active"], activeforeground=COLORS["text"],
                relief="flat", borderwidth=0, highlightthickness=1,
                highlightbackground=COLORS["sidebar"], highlightcolor=COLORS["link"],
                cursor="hand2",
            )
            button.pack(side="left", fill="x", expand=True)
            self.nav_items[status] = (indicator, button, count, item)
        profile = tk.Frame(sidebar, bg=COLORS["sidebar"])
        profile.pack(side="bottom", fill="x", padx=24, pady=24)
        tk.Frame(profile, height=1, bg=COLORS["border"]).pack(fill="x", pady=(0, 16))
        self.label(profile, "Koleksi pribadi", 10).pack(anchor="w")
        self.label(profile, "Disimpan di perangkat ini", 8, COLORS["muted"]).pack(anchor="w")
        tk.Frame(shell, width=1, bg=COLORS["border"]).pack(side="left", fill="y")

        page = tk.Frame(shell, bg=COLORS["surface"])
        page.pack(side="left", fill="both", expand=True, padx=32, pady=28)
        header = tk.Frame(page, bg=COLORS["surface"])
        header.pack(fill="x", pady=(0, 24))
        heading = tk.Frame(header, bg=COLORS["surface"])
        heading.pack(side="left")
        tk.Label(heading, textvariable=self.heading_var, bg=COLORS["surface"],
                 fg=COLORS["text"], font=(self.font_family, 25)).pack(anchor="w")
        self.label(heading, "Semua petualangan, satu tempat.", 10, COLORS["muted"]).pack(
            anchor="w", pady=(5, 0),
        )
        ttk.Button(header, text="+  Tambah game", style="Primary.TButton",
                   command=self.open_game_form).pack(side="right")

        toolbar = PearlPanel(page, height=96, inset=14)
        toolbar.pack(fill="x", pady=(0, 22))
        toolbar.body.columnconfigure(0, weight=1)
        self.label(toolbar.body, "Cari dalam koleksi", 9, COLORS["muted"]).grid(
            row=0, column=0, sticky="w", pady=(0, 6),
        )
        self.label(toolbar.body, "Status", 9, COLORS["muted"]).grid(
            row=0, column=1, sticky="w", padx=(14, 0), pady=(0, 6),
        )
        self.search_entry = ttk.Entry(toolbar.body, textvariable=self.search_var)
        self.search_entry.grid(row=1, column=0, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.refresh_table())
        status_filter = ttk.Combobox(toolbar.body, textvariable=self.status_var,
                                    values=("Semua", *STATUSES), state="readonly", width=12)
        status_filter.grid(row=1, column=1, padx=(14, 10))
        status_filter.bind("<<ComboboxSelected>>", lambda event: self.refresh_table())
        ttk.Button(toolbar.body, text="Reset", command=self.reset_filters).grid(row=1, column=2)

        collection_bar = tk.Frame(page, bg=COLORS["surface"])
        collection_bar.pack(fill="x", pady=(0, 14))
        tk.Label(collection_bar, textvariable=self.summary_var, bg=COLORS["surface"],
                 fg=COLORS["muted"], font=(self.font_family, 10)).pack(side="left")
        self.delete_button = ttk.Button(collection_bar, text="Hapus", style="Danger.TButton",
                                        command=self.delete_selected, state="disabled")
        self.delete_button.pack(side="right", padx=(8, 0))
        self.edit_button = ttk.Button(collection_bar, text="Edit", command=self.edit_selected,
                                      state="disabled")
        self.edit_button.pack(side="right", padx=(14, 0))
        self.view_buttons = {}
        for name in ("Tabel", "Kartu"):
            button = tk.Button(
                collection_bar, text=name, font=(self.font_family, 10), padx=12, pady=9,
                command=lambda value=name: self.set_view(value), relief="flat", borderwidth=0,
                highlightthickness=1, highlightbackground=COLORS["surface"],
                highlightcolor=COLORS["link"], bg=COLORS["surface"], fg=COLORS["muted"],
                activebackground=COLORS["active"], activeforeground=COLORS["text"], cursor="hand2",
            )
            button.pack(side="right")
            self.view_buttons[name] = button

        self.content = tk.Frame(page, bg=COLORS["surface"])
        self.content.pack(fill="both", expand=True)
        self.cards_area = tk.Frame(self.content, bg=COLORS["surface"])
        self.cards_canvas = tk.Canvas(self.cards_area, bg=COLORS["surface"],
                                      highlightthickness=0, height=1)
        self.cards_scrollbar = ttk.Scrollbar(self.cards_area, orient="vertical",
                                             command=self.cards_canvas.yview)
        self.cards_canvas.configure(yscrollcommand=self.cards_scrollbar.set)
        self.cards_scrollbar.pack(side="right", fill="y")
        self.cards_canvas.pack(side="left", fill="both", expand=True)
        self.cards_body = tk.Frame(self.cards_canvas, bg=COLORS["surface"])
        self.cards_window = self.cards_canvas.create_window(
            0, 0, anchor="nw", window=self.cards_body,
        )
        self.cards_canvas.bind("<Configure>", self.resize_cards)
        self.cards_body.bind("<Configure>", self.update_scroll_region)

        self.table_area = tk.Frame(self.content, bg=COLORS["surface"])
        columns = ("title", "platform", "genre", "status", "rating")
        self.table = ttk.Treeview(self.table_area, columns=columns, show="headings",
                                 selectmode="browse", style="Library.Treeview")
        for column, heading_text, width in (
            ("title", "Judul game", 240), ("platform", "Platform", 110),
            ("genre", "Genre", 110), ("status", "Status", 120), ("rating", "Rating", 80),
        ):
            self.table.heading(column, text=heading_text, anchor="w")
            self.table.column(column, width=width, minwidth=70, anchor="w")
        self.table.column("title", minwidth=160)
        self.table.column("rating", anchor="center")
        self.table.heading("rating", anchor="center")
        for status, color in STATUS_COLORS.items():
            self.table.tag_configure(status, foreground=color)
        self.table.tag_configure("even", background=COLORS["surface"])
        self.table.tag_configure("odd", background=COLORS["stripe"])
        scrollbar = ttk.Scrollbar(self.table_area, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", lambda event: self.update_actions())
        self.table.bind("<Double-1>", self.on_double_click)
        self.empty_label = tk.Label(self.content, textvariable=self.empty_var,
                                    bg=COLORS["surface"], fg=COLORS["muted"],
                                    font=(self.font_family, 11), justify="center")
        self.set_view("Kartu")

        tk.Frame(page, height=1, bg=COLORS["border"]).pack(fill="x", pady=(18, 14))
        footer = tk.Frame(page, bg=COLORS["surface"])
        footer.pack(fill="x")
        tk.Label(footer, textvariable=self.footer_var, bg=COLORS["surface"],
                 fg=COLORS["muted"], font=(self.font_family, 9)).pack(side="left")
        ttk.Button(footer, text="Muat ulang", command=self.refresh_table).pack(side="right")
        self.label(page, "ZIMURU STYLE  /  PEARL WHITE", 8, COLORS["muted"]).pack(
            anchor="w", pady=(10, 0),
        )

    def set_view(self, name):
        self.view_var.set(name)
        for value, button in self.view_buttons.items():
            active = value == name
            button.configure(bg=COLORS["active"] if active else COLORS["surface"],
                             fg=COLORS["text"] if active else COLORS["muted"])
        self.cards_area.pack_forget()
        self.table_area.pack_forget()
        area = self.cards_area if name == "Kartu" else self.table_area
        area.pack(fill="both", expand=True)
        if name == "Kartu":
            self.render_cards()

    def resize_cards(self, event):
        self.cards_canvas.itemconfigure(self.cards_window, width=event.width)
        columns = max(1, min(4, (event.width + 18) // 258))
        if columns != self._card_columns:
            if self._layout_job is not None:
                self.root.after_cancel(self._layout_job)
            self._layout_job = self.root.after(60, self.render_cards)

    def update_scroll_region(self, event=None):
        self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))

    def scroll_cards(self, event):
        if not self.cards_area.winfo_ismapped():
            return
        widget = event.widget
        while widget != self.cards_area:
            if not widget.winfo_parent():
                return
            widget = widget.nametowidget(widget.winfo_parent())
        if self.cards_body.winfo_height() <= self.cards_canvas.winfo_height():
            return
        steps = -1 if getattr(event, "num", None) == 4 else 1
        if getattr(event, "delta", 0):
            steps = -1 if event.delta > 0 else 1
        self.cards_canvas.yview_scroll(steps * 3, "units")
        return "break"

    def render_cards(self):
        if self._layout_job is not None:
            self.root.after_cancel(self._layout_job)
            self._layout_job = None
        for child in self.cards_body.winfo_children():
            child.destroy()
        self.card_panels.clear()
        width = max(260, self.cards_canvas.winfo_width())
        columns = max(1, min(4, (width + 18) // 258))
        self._card_columns = columns
        for column in range(4):
            self.cards_body.columnconfigure(column, weight=1 if column < columns else 0,
                                            uniform="cards" if column < columns else "")
        selected = self.table.selection()
        for index, game in enumerate(self.visible_games):
            game_id, title, platform, genre, status, rating = game
            panel = PearlPanel(self.cards_body, height=300, width=240, inset=12)
            panel.grid(row=index // columns, column=index % columns, sticky="ew",
                       padx=(0, 18 if index % columns < columns - 1 else 0), pady=(0, 18))
            self.card_panels[str(game_id)] = panel
            if str(game_id) in selected:
                panel.set_border(COLORS["link"])
            cover = tk.Canvas(panel.body, height=130, bg=COLORS["active"],
                              highlightthickness=0, cursor="hand2")
            cover.pack(fill="x")
            cover.bind("<Configure>", lambda event, c=cover, t=title, g=genre:
                       draw_cover(c, t, g, self.font_family))
            display_title = title if len(title) <= 56 else title[:53] + "..."
            title_label = self.label(panel.body, display_title, 11, bold=True)
            title_label.configure(anchor="w", justify="left")
            title_label.pack(fill="x", pady=(12, 2))
            panel.body.bind("<Configure>", lambda event, label=title_label:
                            label.configure(wraplength=max(40, event.width - 4)))
            metadata = f"{platform}  ·  {genre}"
            if len(metadata) > 48:
                metadata = metadata[:45] + "..."
            meta = self.label(panel.body, metadata, 9, COLORS["muted"])
            meta.configure(anchor="w")
            meta.pack(fill="x", pady=(0, 9))
            meta.bind("<Configure>", lambda event, label=meta:
                      label.configure(wraplength=max(40, event.width - 4)))
            details = tk.Frame(panel.body, bg=COLORS["surface"])
            details.pack(fill="x")
            tk.Label(details, text=STATUS_LABELS.get(status, status),
                     bg=STATUS_SURFACES.get(status, COLORS["raised"]),
                     fg=STATUS_COLORS.get(status, COLORS["muted"]),
                     padx=7, pady=3, font=(self.font_family, 8)).pack(side="left")
            rating_text = "- / 10" if rating is None else f"{rating:g} / 10"
            self.label(details, rating_text, 8, COLORS["muted"]).pack(side="right")
            action = tk.Button(
                panel.body, text="Edit detail", font=(self.font_family, 9),
                command=lambda value=game_id: self.edit_card(value),
                bg=COLORS["surface"], fg=COLORS["link"], activebackground=COLORS["active"],
                activeforeground=COLORS["link"], relief="flat", borderwidth=0,
                highlightthickness=1, highlightbackground=COLORS["surface"],
                highlightcolor=COLORS["link"], anchor="w", padx=0, pady=7, cursor="hand2",
            )
            action.pack(side="bottom", anchor="w")
            for widget in (panel, panel.body, cover, title_label, meta):
                widget.bind("<Button-1>", lambda event, value=game_id: self.select_card(value))
        self.update_scroll_region()

    def select_card(self, game_id):
        self.table.selection_set(str(game_id))
        self.table.focus(str(game_id))
        self.update_actions()

    def edit_card(self, game_id):
        self.select_card(game_id)
        self.edit_selected()

    def schedule_search(self, *args):
        if self._search_job is not None:
            self.root.after_cancel(self._search_job)
        self._search_job = self.root.after(200, self.refresh_table)

    def update_navigation(self):
        selected = self.status_var.get()
        for status, (indicator, button, count, item) in self.nav_items.items():
            active = status == selected
            background = COLORS["active"] if active else COLORS["sidebar"]
            indicator.configure(bg=COLORS["link"] if active else COLORS["sidebar"])
            item.configure(bg=background)
            count.configure(bg=background)
            button.configure(bg=background, fg=COLORS["text"] if active else COLORS["muted"],
                             highlightbackground=background)
        self.heading_var.set({
            "Semua": "Koleksi game.", "Backlog": "Petualangan berikutnya.",
            "Playing": "Sedang dimainkan.", "Completed": "Sudah ditamatkan.",
            "Dropped": "Game yang dihentikan.",
        }.get(selected, "Koleksi game."))

    def update_actions(self):
        selection = self.table.selection()
        state = "!disabled" if selection else "disabled"
        self.edit_button.state([state])
        self.delete_button.state([state])
        for game_id, panel in self.card_panels.items():
            panel.set_border(COLORS["link"] if game_id in selection else COLORS["border"])

    def select_status(self, status):
        self.status_var.set(status)
        self.refresh_table()
        self.cards_canvas.yview_moveto(0)

    def reset_filters(self):
        self.search_var.set("")
        self.status_var.set("Semua")
        self.refresh_table()
        self.cards_canvas.yview_moveto(0)

    def refresh_table(self, select_id=None):
        if self._search_job is not None:
            self.root.after_cancel(self._search_job)
            self._search_job = None
        self.update_navigation()
        try:
            all_games = get_games()
        except sqlite3.Error as error:
            messagebox.showerror("Gagal membaca koleksi", str(error), parent=self.root)
            return
        keyword = self.search_var.get().strip().casefold()
        status = self.status_var.get()
        games = [game for game in all_games if keyword in game[1].casefold()
                 and (status == "Semua" or game[4] == status)]
        previous = self.table.selection()
        selected_id = str(select_id) if select_id is not None else (previous[0] if previous else None)
        for item in self.table.get_children():
            self.table.delete(item)
        for index, game in enumerate(games):
            game_id, title, platform, genre, game_status, rating = game
            self.table.insert("", "end", iid=str(game_id), values=(
                title, platform, genre, game_status, "-" if rating is None else f"{rating:g}/10",
            ), tags=("even" if index % 2 == 0 else "odd", game_status))
        if selected_id is not None and self.table.exists(selected_id):
            self.table.selection_set(selected_id)
            self.table.focus(selected_id)
            self.table.see(selected_id)
        self.visible_games = games
        self.render_cards()
        self.summary_var.set(f"{len(games)} game")
        self.footer_var.set(f"Menampilkan {len(games)} dari {len(all_games)} game")
        for nav_status, variable in self.nav_counts.items():
            variable.set(str(len(all_games) if nav_status == "Semua" else
                             sum(game[4] == nav_status for game in all_games)))
        if games:
            self.empty_label.place_forget()
        else:
            self.empty_var.set(
                "Koleksimu masih kosong.\nTambahkan game pertama untuk memulai."
                if not all_games else "Tidak ada hasil yang cocok.\nCoba judul lain atau reset filter."
            )
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
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