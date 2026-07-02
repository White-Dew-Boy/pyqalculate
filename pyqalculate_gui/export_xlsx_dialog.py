"""Export XLSX dialog for PyQalculate GUI.

Provides a dialog for exporting matrix/vector data from the calculator
to Excel (.xlsx) files. Supports exporting either the current result
or a named variable, with a configurable sheet name.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable

from pyqalculate_gui.calculator_service import CalculatorService
from pyqalculate_gui.dialogs.base import ModalDialog
from pyqalculate_gui.theme import LIGHT, Theme
from pyqalculate_gui.i18n import _


class ExportXlsxDialog(ModalDialog):
    """Modal dialog for exporting data to Excel (.xlsx).

    Fields:
    - Data source (current result or named variable)
    - Variable name entry (for named variable source)
    - File path (with save-as browse button)
    - Sheet name (default "Sheet1")
    """

    def __init__(
        self,
        parent: tk.Widget,
        theme: Theme = LIGHT,
        calculator: CalculatorService | None = None,
        get_last_result: Callable[[], object | None] | None = None,
    ) -> None:
        super().__init__(parent, _("Export XLSX"), size=(460, 290), theme=theme)
        self._calc = calculator
        self._get_last_result = get_last_result

    def _build_content(self, parent: ttk.Frame) -> None:
        """Build the dialog UI."""
        # --- Data source ---
        ttk.Label(parent, text=_("Source:")).grid(row=0, column=0, sticky="w", pady=4)
        source_frame = ttk.Frame(parent)
        source_frame.grid(row=0, column=1, columnspan=2, sticky="ew", pady=4)
        parent.columnconfigure(1, weight=1)

        self._source_var = tk.StringVar(value="variable")
        ttk.Radiobutton(
            source_frame, text=_("Named variable"),
            variable=self._source_var, value="variable",
            command=self._on_source_change,
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            source_frame, text=_("Current result"),
            variable=self._source_var, value="result",
            command=self._on_source_change,
        ).pack(anchor=tk.W)

        # --- Variable name ---
        ttk.Label(parent, text=_("Variable:")).grid(row=1, column=0, sticky="w", pady=4)
        self._var_name_var = tk.StringVar()
        self._var_name_entry = ttk.Entry(parent, textvariable=self._var_name_var, width=30)
        self._var_name_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)

        # --- File path ---
        ttk.Label(parent, text=_("File:")).grid(row=2, column=0, sticky="w", pady=4)
        file_frame = ttk.Frame(parent)
        file_frame.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)

        self._file_var = tk.StringVar()
        self._file_entry = ttk.Entry(file_frame, textvariable=self._file_var, width=35)
        self._file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text=_("Browse..."), command=self._browse_file).pack(
            side=tk.LEFT, padx=(4, 0),
        )

        # --- Sheet name ---
        ttk.Label(parent, text=_("Sheet name:")).grid(row=3, column=0, sticky="w", pady=4)
        self._sheet_name_var = tk.StringVar(value="Sheet1")
        ttk.Entry(
            parent, textvariable=self._sheet_name_var, width=30,
        ).grid(row=3, column=1, columnspan=2, sticky="ew", pady=4)

    # ------------------------------------------------------------------
    # UI callbacks
    # ------------------------------------------------------------------

    def _on_source_change(self) -> None:
        """Toggle variable name entry based on source selection."""
        if self._source_var.get() == "variable":
            self._var_name_entry.config(state="normal")
        else:
            self._var_name_entry.config(state="disabled")

    def _browse_file(self) -> None:
        """Open save-file dialog."""
        path = filedialog.asksaveasfilename(
            parent=self._dialog,  # type: ignore[arg-type]
            title=_("Save XLSX File"),
            defaultextension=".xlsx",
            filetypes=[(_("Excel files"), "*.xlsx"), (_("All files"), "*.*")],
        )
        if path:
            self._file_var.set(path)

    # ------------------------------------------------------------------
    # Override ModalDialog hooks
    # ------------------------------------------------------------------

    def _on_ok(self) -> None:
        """Validate inputs and perform the XLSX export."""
        filename = self._file_var.get().strip()
        if not filename:
            messagebox.showerror(
                _("Error"), _("Please specify an output file."),
                parent=self._dialog,  # type: ignore[arg-type]
            )
            return

        sheet_name = self._sheet_name_var.get().strip() or "Sheet1"

        # Resolve the data source
        mstruct = None

        if self._source_var.get() == "variable":
            var_name = self._var_name_var.get().strip()
            if not var_name:
                messagebox.showerror(
                    _("Error"), _("Please enter a variable name."),
                    parent=self._dialog,  # type: ignore[arg-type]
                )
                return
            if self._calc is None:
                messagebox.showerror(
                    _("Error"), _("No calculator available."),
                    parent=self._dialog,  # type: ignore[arg-type]
                )
                return
            var = self._calc.get_variable(var_name)
            if var is None:
                messagebox.showerror(
                    _("Error"), _("Variable '{}' not found.").format(var_name),
                    parent=self._dialog,  # type: ignore[arg-type]
                )
                return
            from pyqalculate.variable import KnownVariable

            if isinstance(var, KnownVariable):
                mstruct = var.get()
        else:
            if self._get_last_result is not None:
                mstruct = self._get_last_result()

        if mstruct is None or self._calc is None:
            messagebox.showerror(
                _("Error"), _("No data to export."),
                parent=self._dialog,  # type: ignore[arg-type]
            )
            return

        try:
            success = self._calc.export_xlsx(mstruct, filename, sheet_name=sheet_name)
            if success:
                messagebox.showinfo(
                    _("Export Successful"),
                    _("Data exported to {}").format(filename),
                    parent=self._dialog,  # type: ignore[arg-type]
                )
                super()._on_ok()
            else:
                messagebox.showerror(
                    _("Export Failed"),
                    _("Could not write the XLSX file."),
                    parent=self._dialog,  # type: ignore[arg-type]
                )
        except ImportError:
            messagebox.showerror(
                _("Missing Dependency"),
                _("The openpyxl library is required for Excel export.\n\n"
                  "Install it with:\npip install openpyxl"),
                parent=self._dialog,  # type: ignore[arg-type]
            )
        except Exception as e:
            messagebox.showerror(
                _("Export Error"), str(e),
                parent=self._dialog,  # type: ignore[arg-type]
            )
