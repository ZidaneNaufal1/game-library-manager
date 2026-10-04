"""GUI integration checks. Run with a display or xvfb-run on Linux."""
import os
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

import database
from main import GameLibraryApp


@unittest.skipUnless(os.environ.get("DISPLAY") or os.name == "nt", "Requires a GUI display")
class PearlWhiteIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database_patch = patch.object(database, "DB_PATH", Path(self.temp.name) / "games.db")
        self.database_patch.start()
        database.initialize_database()
        self.ids = [database.add_game(*values) for values in (
            ("Vague Echoes", "PC", "Horror", "Playing", "8.5"),
            ("Skyward Run", "PC", "Platformer", "Backlog", ""),
            ("Cozy Fields", "PC", "Simulation", "Completed", "9"),
        )]
        self.root = tk.Tk()
        self.errors = []
        self.root.report_callback_exception = lambda *error: self.errors.append(error)
        self.app = GameLibraryApp(self.root)
        self.pump()

    def tearDown(self):
        self.root.destroy()
        self.database_patch.stop()
        self.temp.cleanup()
        self.assertEqual(self.errors, [], "Unexpected Tk callback failure")

    def pump(self):
        self.root.after(100, self.root.quit)
        self.root.mainloop()
        self.root.update()

    def form(self):
        dialogs = [child for child in self.root.winfo_children() if isinstance(child, tk.Toplevel)]
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        body = dialog.winfo_children()[0]
        fields = [child for child in body.winfo_children() if isinstance(child, (ttk.Entry, ttk.Combobox))]
        buttons = body.winfo_children()[-1].winfo_children()
        return dialog, fields, buttons

    def test_card_table_selection_and_empty_collection(self):
        self.assertEqual(len(self.app.card_panels), 3)
        self.assertTrue(self.app.edit_button.instate(["disabled"]))
        self.app.select_card(self.ids[0])
        self.assertEqual(self.app.selected_game()[1], "Vague Echoes")
        self.assertTrue(self.app.edit_button.instate(["!disabled"]))
        self.app.set_view("Tabel")
        self.pump()
        self.assertTrue(self.app.table.winfo_ismapped())
        self.assertEqual(self.app.table.selection(), (str(self.ids[0]),))
        self.app.set_view("Kartu")
        for game_id in self.ids:
            database.delete_game(game_id)
        self.app.refresh_table()
        self.pump()
        self.assertEqual(len(self.app.card_panels), 0)
        self.assertTrue(self.app.edit_button.instate(["disabled"]))
        self.assertTrue(self.app.empty_label.winfo_ismapped())

    def test_search_combines_with_status_and_reset(self):
        self.app.search_var.set("VAGUE")
        self.app.select_status("Playing")
        self.assertEqual([g[1] for g in self.app.visible_games], ["Vague Echoes"])
        self.assertEqual(self.app.nav_counts["Semua"].get(), "3")
        self.app.select_status("Completed")
        self.pump()
        self.assertEqual(self.app.visible_games, [])
        self.assertTrue(self.app.empty_label.winfo_ismapped())
        self.app.reset_filters()
        self.pump()
        self.assertEqual(len(self.app.card_panels), 3)
        self.assertFalse(self.app.empty_label.winfo_ismapped())

    def test_add_form_validation_save_and_database_reopen(self):
        self.app.open_game_form()
        dialog, fields, buttons = self.form()
        with patch("main.messagebox.showwarning") as warning:
            buttons[1].invoke()
            warning.assert_called_once()
        self.assertTrue(dialog.winfo_exists())
        for field, value in zip(fields, ("New Game", "PC", "Puzzle", "Backlog", "7,5")):
            self.root.setvar(field.cget("textvariable"), value)
        buttons[1].invoke()
        self.pump()
        self.assertEqual(len(database.get_games()), 4)
        saved = self.app.selected_game()
        self.assertEqual(saved[1:], ("New Game", "PC", "Puzzle", "Backlog", 7.5))
        # Each database read opens a new SQLite connection.
        self.assertEqual(database.get_game(saved[0]), saved)
        self.assertEqual(self.app.status_var.get(), "Semua")

    def test_edit_form_save_and_cancel(self):
        self.app.edit_card(self.ids[0])
        dialog, fields, buttons = self.form()
        self.root.setvar(fields[0].cget("textvariable"), "Echoes Updated")
        self.root.setvar(fields[3].cget("textvariable"), "Completed")
        buttons[1].invoke()
        self.pump()
        self.assertEqual(database.get_game(self.ids[0])[1], "Echoes Updated")
        self.assertEqual(database.get_game(self.ids[0])[4], "Completed")
        self.app.edit_card(self.ids[0])
        dialog, fields, buttons = self.form()
        self.root.setvar(fields[0].cget("textvariable"), "Should not save")
        buttons[0].invoke()
        self.assertEqual(database.get_game(self.ids[0])[1], "Echoes Updated")

    def test_deletion_cancel_then_confirm(self):
        self.app.select_card(self.ids[0])
        with patch("main.messagebox.askyesno", return_value=False):
            self.app.delete_selected()
        self.assertIsNotNone(database.get_game(self.ids[0]))
        with patch("main.messagebox.askyesno", return_value=True):
            self.app.delete_selected()
        self.pump()
        self.assertIsNone(database.get_game(self.ids[0]))
        self.assertEqual(len(self.app.card_panels), 2)
        self.assertTrue(self.app.delete_button.instate(["disabled"]))

    def test_resize_reflows_without_losing_data_and_footer(self):
        self.root.geometry("1180x820")
        self.pump()
        self.assertEqual(self.app._card_columns, 3)
        self.root.geometry("900x620")
        self.pump()
        self.assertEqual(self.app._card_columns, 2)
        for widget in (self.app.search_entry, self.app.edit_button, self.app.delete_button):
            self.assertGreater(widget.winfo_width(), 1)
            self.assertGreaterEqual(widget.winfo_rootx(), self.root.winfo_rootx())
            self.assertLessEqual(widget.winfo_rootx() + widget.winfo_width(),
                                 self.root.winfo_rootx() + self.root.winfo_width())
        footer = next(child for child in self.app.content.master.winfo_children()
                      if isinstance(child, tk.Frame) and any(
                          isinstance(w, tk.Label) and str(w.cget("textvariable")) == str(self.app.footer_var)
                          for w in child.winfo_children()))
        self.assertLessEqual(footer.winfo_rooty() + footer.winfo_height(),
                             self.root.winfo_rooty() + self.root.winfo_height())
        self.assertEqual(len(database.get_games()), 3)
        self.app.set_view("Tabel")
        self.pump()
        self.assertEqual(len(self.app.table.get_children()), 3)


if __name__ == "__main__":
    unittest.main()
