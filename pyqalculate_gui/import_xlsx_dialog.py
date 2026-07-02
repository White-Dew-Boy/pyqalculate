"""Import XLSX dialog for PyQalculate GUI.

Provides a dialog for importing Excel (XLSX) files as matrix/vector
variables into the calculator. Supports sheet selection, first-row
header detection, and output format selection.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from pyqalculate_gui.theme import Theme, LIGHT
from pyqalculate_gui.dialogs.base import ModalDialog
from pyqalculate_gui.calculator_service import CalculatorService
from pyqalculate_gui.i18n import _


class ImportXlsxDialog(ModalDialog):
    """Modal dialog for importing Excel files.

    Fields:
    - File path (with browse button)
    - Sheet name/index
    - Variable name (auto-populated from filename)
    - First row (spin button for header row)
    - Headers checkbox
    - Output format (matrix vs. per-column vectors)
    """

    def __init__(
        self,
        parent: tk.Widget,
        theme: Theme = LIGHT,
        calculator: CalculatorService | None = None,
    ) -> None:
        super().__init__(parent, _("Import XLSX"), size=(460, 340), theme=theme)
        self._calc = calculator
        self._file_path = ""

    def _build_content(self, parent: ttk.Frame) -> None:
        """Build the import XLSX UI."""
        # --- File path ---
        ttk.Label(parent, text=_("File:")).grid(row=0, column=0, sticky="w", pady=4)
        file_frame = ttk.Frame(parent)
        file_frame.grid(row=0, column=1, columnspan=2, sticky="ew", pady=4)
        parent.columnconfigure(1, weight=1)

        self._file_var = tk.StringVar()
        self._file_entry = ttk.Entry(file_frame, textvariable=self._file_var, width=35)
        self._file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text=_("Browse..."), command=self._browse_file).pack(
            side=tk.LEFT, padx=(4, 0)
        )

        # --- Sheet ---
        ttk.Label(parent, text=_("Sheet:")).grid(row=1, column=0, sticky="w", pady=4)
        self._sheet_var = tk.StringVar(value="0")
        ttk.Combobox(
            parent, textvariable=self._sheet_var, width=28
        ).grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)

        # --- Variable name ---
        ttk.Label(parent, text=_("Name:")).grid(row=2, column=0, sticky="w", pady=4)
        self._name_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self._name_var, width=30).grid(
            row=2, column=1, columnspan=2, sticky="ew", pady=4
        )

        # --- First row ---
        ttk.Label(parent, text=_("First row:")).grid(row=3, column=0, sticky="w", pady=4)
        self._first_row_var = tk.IntVar(value=1)
        ttk.Spinbox(
            parent, from_=1, to=10000, textvariable=self._first_row_var, width=8
        ).grid(row=3, column=1, sticky="w", pady=4)

        # --- Headers checkbox ---
        self._headers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            parent, text=_("First row contains headers"), variable=self._headers_var
        ).grid(row=4, column=0, columnspan=3, sticky="w", pady=4)

        # --- Output format ---
        ttk.Label(parent, text=_("Format:")).grid(row=5, column=0, sticky="w", pady=4)
        format_frame = ttk.Frame(parent)
        format_frame.grid(row=5, column=1, columnspan=2, sticky="ew", pady=4)

        self._format_var = tk.StringVar(value="vectors")
        ttk.Radiobutton(
            format_frame,
            text=_("Separate vectors per column"),
            variable=self._format_var,
            value="vectors",
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            format_frame,
            text=_("Single matrix variable"),
            variable=self._format_var,
            value="matrix",
        ).pack(anchor=tk.W)

    def _browse_file(self) -> None:
        """Open file chooser dialog."""
        assert self._dialog is not None
        path = filedialog.askopenfilename(
            parent=self._dialog,
            title=_("Select Excel File"),
            filetypes=[(_("Excel files"), "*.xlsx"), (_("All files"), "*.*")],
        )
        if path:
            self._file_var.set(path)
            self._file_path = path
            # Auto-populate name from filename
            name = Path(path).stem
            self._name_var.set(name)

    def _on_ok(self) -> None:
        """Validate inputs and perform the XLSX import."""
        assert self._dialog is not None
        filename = self._file_var.get().strip()
        if not filename:
            messagebox.showerror(
                _("Error"), _("Please select an Excel file."), parent=self._dialog
            )
            return

        name = self._name_var.get().strip()
        first_row = self._first_row_var.get()
        headers = self._headers_var.get()
        to_matrix = self._format_var.get() == "matrix"

        sheet_str = self._sheet_var.get().strip()
        try:
            sheet: int | str = int(sheet_str)
        except ValueError:
            sheet = sheet_str

        if self._calc is None:
            super()._on_ok()
            return

        try:
            result = self._calc.import_xlsx(
                filename=filename,
                sheet=sheet,
                headers=headers,
                first_row=first_row,
                to_matrix=to_matrix,
                name=name,
            )

            if result.is_undefined():
                messagebox.showerror(
                    _("Import Failed"),
                    _("Could not import the Excel file. Check the file path and format."),
                    parent=self._dialog,
                )
                return

            # Show success message
            if to_matrix:
                msg = _("Imported as matrix variable '{}'.").format(name)
            else:
                msg = _("Imported columns as variables with prefix '{}'.").format(name)

            messagebox.showinfo(_("Import Successful"), msg, parent=self._dialog)
            super()._on_ok()

        except ImportError:
            messagebox.showerror(
                _("Missing Dependency"),
                _("The openpyxl library is required for Excel import.\n\nInstall it with:\npip install openpyxl"),
                parent=self._dialog,
            )
            return
        except Exception as e:
            messagebox.showerror(_("Import Error"), str(e), parent=self._dialog)

    # Public API
    def get_file_path(self) -> str:
        """Get selected file path."""
        return self._file_path

    def get_name(self) -> str:
        """Get variable name."""
        return self._name_var.get().strip()

    def get_sheet(self) -> str:
        """Get sheet name or index."""
        return self._sheet_var.get().strip()

    def get_first_row(self) -> int:
        """Get first row number."""
        return self._first_row_var.get()

    def get_headers(self) -> bool:
        """Get whether first row contains headers."""
        return self._headers_var.get()

    def get_to_matrix(self) -> bool:
        """Get whether output format is matrix."""
        return self._format_var.get() == "matrix"
