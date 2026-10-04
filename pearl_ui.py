"""Dependency-free visual surfaces for Zimuru Style Pearl White."""
import tkinter as tk


COLORS = {
    "background": "#F7F9FC", "surface": "#FFFFFF", "raised": "#F0F4F8",
    "sidebar": "#FBFCFE", "text": "#17212B", "muted": "#526174",
    "accent": "#8CCFFF", "accent_hover": "#B1DFFF", "link": "#175CD3",
    "border": "#DEE5ED", "active": "#EAF5FF", "selected": "#DCEFFF",
    "danger": "#A42636", "danger_surface": "#FFF1F2", "danger_border": "#E8C3C8",
    "danger_hover": "#FCE3E7", "disabled": "#748191", "stripe": "#FAFCFE",
}

STATUS_LABELS = {
    "Semua": "Koleksi", "Backlog": "Belum dimainkan", "Playing": "Sedang dimainkan",
    "Completed": "Selesai", "Dropped": "Dihentikan",
}
STATUS_COLORS = {
    "Backlog": "#526174", "Playing": "#175CD3",
    "Completed": "#286343", "Dropped": "#81551B",
}
STATUS_SURFACES = {
    "Backlog": "#F0F4F8", "Playing": "#EAF5FF",
    "Completed": "#EDF6EF", "Dropped": "#FCF3E6",
}


def rounded_polygon(canvas, x1, y1, x2, y2, radius=14, **options):
    radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    points = (
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    )
    return canvas.create_polygon(points, smooth=True, splinesteps=24, **options)


class PearlPanel(tk.Canvas):
    """Rounded, opaque surface: portable fallback for browser glass materials."""
    def __init__(self, parent, color=None, border=None, radius=14, inset=14, **kwargs):
        super().__init__(parent, bg=parent.cget("bg"), highlightthickness=0, **kwargs)
        self.color = color or COLORS["surface"]
        self.border = border or COLORS["border"]
        self.radius = radius
        self.inset = inset
        self.body = tk.Frame(self, bg=self.color)
        self._window = self.create_window(inset, inset, anchor="nw", window=self.body)
        self._shape = None
        self.bind("<Configure>", self._resize)

    def _resize(self, event):
        self.itemconfigure(self._window, width=max(1, event.width - 2 * self.inset),
                           height=max(1, event.height - 2 * self.inset))
        if self._shape is not None:
            self.delete(self._shape)
        self._shape = rounded_polygon(
            self, 1, 1, max(2, event.width - 1), max(2, event.height - 1),
            self.radius, fill=self.color, outline=self.border, width=1,
        )
        self.tag_lower(self._shape)

    def set_border(self, color):
        self.border = color
        if self._shape is not None:
            self.itemconfigure(self._shape, outline=color)


def draw_cover(canvas, title, genre, family):
    """Draw original abstract cover placeholders; no downloaded game artwork."""
    width = max(1, canvas.winfo_width())
    height = max(1, canvas.winfo_height())
    if width < 10 or height < 10:
        return
    canvas.delete("all")
    genre = genre.casefold()
    if "horror" in genre or "fps" in genre:
        palette = ("#DDE6E9", "#BECED3", "#A5B9C1", "#324D59")
        canvas.configure(bg=palette[0])
        for fraction in (.17, .44, .76):
            x = width * fraction
            canvas.create_polygon(x, 0, x + 20, 0, x + 50, height, x - 10, height,
                                  fill=palette[1], outline="")
        canvas.create_oval(-width / 2, height * .6, width * 1.4, height * 1.3,
                           fill="#E9EFF1", outline="")
    elif any(word in genre for word in ("simulation", "casual", "sandbox")):
        palette = ("#E9EEE3", "#CAD7BD", "#B6C9AC", "#385039")
        canvas.configure(bg=palette[0])
        canvas.create_oval(-width * .3, height * .62, width * 1.2, height * 1.8,
                           fill=palette[1], outline="")
        canvas.create_oval(width * .25, height * .72, width * 1.7, height * 1.7,
                           fill=palette[2], outline="")
        canvas.create_oval(width - 60, 15, width - 30, 45, fill="#F8FAF0", outline="")
    else:
        palette = ("#DFEFF8", "#C7E2F2", "#B1D4EC", "#28516C")
        canvas.configure(bg=palette[0])
        canvas.create_polygon(0, height * .8, width * .35, height * .65,
                              width * .8, height, 0, height, fill=palette[1], outline="")
        canvas.create_polygon(width * .4, 0, width, 0, width, height * .35,
                              fill=palette[2], outline="")
        canvas.create_oval(width - 65, 16, width - 23, 58, outline="#FFFFFF", width=1)
    canvas.create_text(width / 2, height / 2, text=(title.upper() if len(title) <= 48 else title[:45].upper() + "..."), fill=palette[3],
                       width=max(1, width - 40), justify="center", font=(family, 15))
