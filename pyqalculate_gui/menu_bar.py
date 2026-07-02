"""Menu bar widget for the PyQalculate GUI."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from pyqalculate_gui.event_bus import (
    CLEAR_ALL,
    COPY_RESULT,
    EXPORT_CSV,
    EXPORT_XLSX,
    IMPORT_CSV,
    IMPORT_XLSX,
    OPEN_HELP_DOC,
    OPEN_HISTORY_WINDOW,
    OPEN_NUMBER_BASES,
    OPEN_PLOT,
    OPEN_PREFERENCES,
    OPEN_UNIT_CONVERSION,
    EventBus,
)
from pyqalculate_gui.i18n import _
from pyqalculate_gui.theme import LIGHT, Theme


class MenuBar:
    """Application menu bar wired to the event bus."""

    def __init__(
        self,
        parent: tk.Tk,
        theme: Theme = LIGHT,
        event_bus: EventBus | None = None,
    ) -> None:
        self._parent = parent
        self._theme = theme
        self._event_bus = event_bus
        self._exact_var = tk.BooleanVar(value=False)
        self._build_menu()

    # -- construction --------------------------------------------------------

    def _build_menu(self) -> None:
        menubar = tk.Menu(self._parent)
        self._parent.config(menu=menubar)

        self._build_file_menu(menubar)
        self._build_edit_menu(menubar)
        self._build_mode_menu(menubar)
        self._build_tools_menu(menubar)
        self._build_help_menu(menubar)
        self._bind_shortcuts()

    def _build_file_menu(self, menubar: tk.Menu) -> None:
        menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("File"), menu=menu)
        menu.add_command(label=_("Import CSV..."), command=self._emit(IMPORT_CSV))
        menu.add_command(label=_("Export CSV..."), command=self._emit(EXPORT_CSV))
        menu.add_command(label=_("Import XLSX..."), command=self._emit(IMPORT_XLSX))
        menu.add_command(label=_("Export XLSX..."), command=self._emit(EXPORT_XLSX))
        menu.add_separator()
        menu.add_command(label=_("Preferences..."), command=self._emit(OPEN_PREFERENCES))
        menu.add_command(label=_("Exit"), command=self._parent.quit)

    def _build_edit_menu(self, menubar: tk.Menu) -> None:
        menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Edit"), menu=menu)
        menu.add_command(
            label=_("Copy Result"), command=self._emit(COPY_RESULT), accelerator="Ctrl+C"
        )
        menu.add_command(label=_("Clear Expression"), command=self._emit(CLEAR_ALL))
        menu.add_command(
            label=_("Clear All"), command=self._emit(CLEAR_ALL), accelerator="Ctrl+L"
        )

    def _build_mode_menu(self, menubar: tk.Menu) -> None:
        menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Mode"), menu=menu)
        menu.add_checkbutton(label=_("Exact Mode"), variable=self._exact_var)
        menu.add_separator()
        menu.add_command(label=_("Functions..."), command=self._emit("open_manage_functions"))
        menu.add_command(label=_("Variables..."), command=self._emit("open_manage_variables"))
        menu.add_command(label=_("Units..."), command=self._emit("open_manage_units"))

    def _build_tools_menu(self, menubar: tk.Menu) -> None:
        menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Tools"), menu=menu)
        menu.add_command(label=_("Plot..."), command=self._emit(OPEN_PLOT))
        menu.add_command(label=_("Number Bases..."), command=self._emit(OPEN_NUMBER_BASES))
        menu.add_command(label=_("Unit Conversion..."), command=self._emit(OPEN_UNIT_CONVERSION))
        menu.add_command(label=_("History..."), command=self._emit(OPEN_HISTORY_WINDOW))

    def _build_help_menu(self, menubar: tk.Menu) -> None:
        menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Help"), menu=menu)
        menu.add_command(label=_("Help Documentation"), command=self._emit(OPEN_HELP_DOC))
        menu.add_separator()
        menu.add_command(label=_("About"), command=self._show_about)

    def _bind_shortcuts(self) -> None:
        self._parent.bind("<Control-l>", lambda _: self._emit(CLEAR_ALL)())
        self._parent.bind("<Control-c>", lambda _: self._emit(COPY_RESULT)())
        self._parent.bind("<Control-p>", lambda _: self._emit(OPEN_PLOT)())

    # -- helpers -------------------------------------------------------------

    def _emit(self, event: str):  # noqa: ANN202
        """Return a callable that emits *event* on the bus."""

        def handler() -> None:
            if self._event_bus is not None:
                self._event_bus.emit(event)

        return handler

    def _show_about(self) -> None:
        messagebox.showinfo(_("About"), _("PyQalculate v3.0\nPure Python calculator"))

    # -- public API ----------------------------------------------------------

    def get_exact_mode_var(self) -> tk.BooleanVar:
        """Return the BooleanVar backing the exact-mode checkbutton."""
        return self._exact_var
