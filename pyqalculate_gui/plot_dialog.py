"""Plot dialog for PyQalculate GUI.

Provides a tkinter dialog for plotting mathematical expressions using
matplotlib. Supports multiple expressions, zoom/pan via NavigationToolbar,
and saving to PNG or SVG.

Uses the ModalDialog base class for consistent dialog lifecycle.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import TYPE_CHECKING, Any

from pyqalculate_gui.dialogs.base import ModalDialog
from pyqalculate_gui.theme import LIGHT, Theme
from pyqalculate_gui.i18n import _

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Color palette for multi-expression plots
# ---------------------------------------------------------------------------
_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


class PlotDialog(ModalDialog):
    """Modal plot dialog for PyQalculate.

    Opens a top-level window with:
    - Expression list (add / remove multiple expressions)
    - Embedded matplotlib canvas with NavigationToolbar (zoom, pan, save)
    - Save-as button (PNG / SVG)
    """

    def __init__(self, parent: tk.Widget, theme: Theme = LIGHT) -> None:  # type: ignore[override]
        super().__init__(parent, _("Plot"), size=(900, 680), resizable=(True, True), theme=theme)
        self._expressions: list[str] = []
        self._canvas: Any = None
        self._toolbar: Any = None
        self._fig: Any = None
        self._ax: Any = None

        # Lazy-imported matplotlib classes
        self._FigureCanvasTkAgg: Any = None
        self._NavigationToolbar2Tk: Any = None

    # ------------------------------------------------------------------
    # Override show() to replace OK/Cancel with Plot-specific buttons
    # ------------------------------------------------------------------

    def show(self, expression: str = "") -> None:
        """Open the plot dialog modally.

        Args:
            expression: Optional expression to pre-fill.
        """
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title(self._title)
        self._dialog.geometry(f"{self._size[0]}x{self._size[1]}")
        self._dialog.resizable(*self._resizable)
        self._dialog.transient(self._parent)  # type: ignore[arg-type]
        self._dialog.grab_set()
        self._dialog.configure(bg=self._theme.bg)

        # Content area
        content = ttk.Frame(self._dialog, padding=10)
        content.pack(fill=tk.BOTH, expand=True)
        self._build_content(content)

        # Custom button row (replace base class OK/Cancel)
        btn_frame = ttk.Frame(self._dialog, padding=(10, 0, 10, 10))
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text=_("Plot"), command=self._on_plot).pack(
            side=tk.LEFT, padx=(0, 4),
        )
        ttk.Button(btn_frame, text=_("Save PNG"), command=self._on_save_png).pack(
            side=tk.LEFT, padx=(0, 4),
        )
        ttk.Button(btn_frame, text=_("Save SVG"), command=self._on_save_svg).pack(
            side=tk.LEFT, padx=(0, 4),
        )
        ttk.Button(btn_frame, text=_("Clear"), command=self._on_clear).pack(
            side=tk.LEFT, padx=(0, 4),
        )
        ttk.Button(btn_frame, text=_("Close"), command=self._on_cancel).pack(
            side=tk.RIGHT,
        )

        self._dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Centre on parent
        self._dialog.update_idletasks()
        x = (
            self._parent.winfo_x()
            + (self._parent.winfo_width() - self._dialog.winfo_width()) // 2
        )
        y = (
            self._parent.winfo_y()
            + (self._parent.winfo_height() - self._dialog.winfo_height()) // 2
        )
        self._dialog.geometry(f"+{x}+{y}")

        # Pre-fill expression
        if expression:
            self._add_expression(expression)

        # Lazy-import matplotlib classes
        self._init_matplotlib()

        # Block until closed
        self._parent.wait_window(self._dialog)

    # ------------------------------------------------------------------
    # Content building (ModalDialog contract)
    # ------------------------------------------------------------------

    def _build_content(self, parent: ttk.Frame) -> None:
        """Build the plot dialog UI."""
        parent.columnconfigure(0, weight=0)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(1, weight=1)

        # ---- Left panel: controls ----
        ctrl = ttk.Frame(parent, padding=4)
        ctrl.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8))
        self._build_controls(ctrl)

        # ---- Right panel: canvas ----
        canvas_parent = ttk.Frame(parent)
        canvas_parent.grid(row=0, column=1, sticky="nsew")
        canvas_parent.columnconfigure(0, weight=1)
        canvas_parent.rowconfigure(1, weight=1)

        self._toolbar_frame = ttk.Frame(canvas_parent)
        self._toolbar_frame.grid(row=0, column=0, sticky="ew")

        self._canvas_frame = ttk.Frame(canvas_parent)
        self._canvas_frame.grid(row=1, column=0, sticky="nsew")

        # Placeholder
        self._placeholder = ttk.Label(
            self._canvas_frame,
            text=_("Add expressions and click Plot"),
            anchor=tk.CENTER,
            foreground=self._theme.separator_fg,
        )
        self._placeholder.pack(expand=True)

    def _build_controls(self, parent: ttk.Frame) -> None:
        """Build the left-side control panel."""
        row = 0

        # -- Expression list --
        ttk.Label(parent, text=_("Expressions"), font=("", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 4),
        )
        row += 1

        list_frame = ttk.Frame(parent)
        list_frame.grid(row=row, column=0, columnspan=2, sticky="ew")
        list_frame.columnconfigure(0, weight=1)

        self._expr_listbox = tk.Listbox(list_frame, height=5, width=30)
        self._expr_listbox.grid(row=0, column=0, sticky="ew")
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self._expr_listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._expr_listbox.config(yscrollcommand=sb.set)
        row += 1

        # Add / Remove / Edit buttons
        btn_row = ttk.Frame(parent)
        btn_row.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        ttk.Button(btn_row, text=_("Add"), width=6, command=self._on_add).pack(
            side=tk.LEFT, padx=(0, 4),
        )
        ttk.Button(btn_row, text=_("Remove"), width=6, command=self._on_remove).pack(
            side=tk.LEFT, padx=(0, 4),
        )
        ttk.Button(btn_row, text=_("Edit"), width=6, command=self._on_edit).pack(
            side=tk.LEFT,
        )
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=8,
        )
        row += 1

        # -- X Range --
        ttk.Label(parent, text=_("X Range"), font=("", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 4),
        )
        row += 1

        ttk.Label(parent, text=_("Min:")).grid(row=row, column=0, sticky="w")
        self._x_min_var = tk.StringVar(value="-10")
        ttk.Entry(parent, textvariable=self._x_min_var, width=12).grid(
            row=row, column=1, sticky="ew", padx=(4, 0),
        )
        row += 1

        ttk.Label(parent, text=_("Max:")).grid(row=row, column=0, sticky="w")
        self._x_max_var = tk.StringVar(value="10")
        ttk.Entry(parent, textvariable=self._x_max_var, width=12).grid(
            row=row, column=1, sticky="ew", padx=(4, 0),
        )
        row += 1

        ttk.Label(parent, text=_("Points:")).grid(row=row, column=0, sticky="w")
        self._points_var = tk.StringVar(value="1000")
        ttk.Entry(parent, textvariable=self._points_var, width=12).grid(
            row=row, column=1, sticky="ew", padx=(4, 0),
        )
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=8,
        )
        row += 1

        # -- Style --
        ttk.Label(parent, text=_("Style"), font=("", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 4),
        )
        row += 1

        ttk.Label(parent, text=_("Line style:")).grid(row=row, column=0, sticky="w")
        self._style_var = tk.StringVar(value=_("lines"))
        style_combo = ttk.Combobox(
            parent,
            textvariable=self._style_var,
            values=[_("lines"), _("scatter"), _("bar"), _("histogram"), _("points+lines"), _("dots"), _("steps")],
            state="readonly",
            width=14,
        )
        style_combo.grid(row=row, column=1, sticky="ew", padx=(4, 0))
        row += 1

        ttk.Label(parent, text=_("Line width:")).grid(row=row, column=0, sticky="w")
        self._linewidth_var = tk.StringVar(value="1.5")
        ttk.Entry(parent, textvariable=self._linewidth_var, width=12).grid(
            row=row, column=1, sticky="ew", padx=(4, 0),
        )
        row += 1

        # Grid toggle
        self._grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text=_("Show grid"), variable=self._grid_var).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(4, 0),
        )
        row += 1

        # Legend toggle
        self._legend_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text=_("Show legend"), variable=self._legend_var).grid(
            row=row, column=0, columnspan=2, sticky="w",
        )
        row += 1

        # Plot title
        ttk.Label(parent, text=_("Title:")).grid(row=row, column=0, sticky="w", pady=(4, 0))
        self._title_var = tk.StringVar(value="")
        ttk.Entry(parent, textvariable=self._title_var, width=16).grid(
            row=row, column=1, sticky="ew", padx=(4, 0), pady=(4, 0),
        )

    # ------------------------------------------------------------------
    # Matplotlib integration
    # ------------------------------------------------------------------

    def _init_matplotlib(self) -> None:
        """Import and store matplotlib tkinter classes (lazy)."""
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.backends._backend_tk import NavigationToolbar2Tk

            self._FigureCanvasTkAgg = FigureCanvasTkAgg
            self._NavigationToolbar2Tk = NavigationToolbar2Tk
        except ImportError:
            if self._dialog is not None:
                messagebox.showerror(
                    _("Missing Dependency"),
                    _("matplotlib is required for plotting.\n"
                    "Install with:  pip install matplotlib"),
                    parent=self._dialog,
                )

    def _render_plot(self) -> None:
        """Evaluate all expressions and render the matplotlib figure."""
        if self._FigureCanvasTkAgg is None or self._NavigationToolbar2Tk is None:
            return

        # Parse range
        try:
            x_min = float(self._x_min_var.get())
            x_max = float(self._x_max_var.get())
            num_points = max(100, int(self._points_var.get()))
        except ValueError:
            if self._dialog is not None:
                messagebox.showerror(
                    _("Invalid Range"),
                    _("X min, max, and points must be valid numbers."),
                    parent=self._dialog,
                )
            return

        if x_min >= x_max:
            if self._dialog is not None:
                messagebox.showerror(
                    _("Invalid Range"),
                    _("X min must be less than X max."),
                    parent=self._dialog,
                )
            return

        # Collect non-empty expressions
        exprs = [e for e in self._expressions if e.strip()]
        if not exprs:
            if self._dialog is not None:
                messagebox.showwarning(
                    _("No Expressions"),
                    _("Add at least one expression to plot."),
                    parent=self._dialog,
                )
            return

        # Build plot style map for line-based styles
        style_map = {
            "lines": "-",
            "points+lines": "o-",
            "dots": ".",
        }
        
        # Evaluate expressions
        from pyqalculate.plot import _eval_expression
        import numpy as np

        x_arr = np.linspace(x_min, x_max, num_points)

        # Destroy old canvas / toolbar
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        if self._toolbar is not None:
            self._toolbar.destroy()
            self._toolbar = None
        self._placeholder.pack_forget()

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor(self._theme.entry_bg)

        selected_style = self._style_var.get()
        # Map translated values back to English internal keys
        _style_reverse = {
            _("lines"): "lines",
            _("scatter"): "scatter",
            _("bar"): "bar",
            _("histogram"): "histogram",
            _("points+lines"): "points+lines",
            _("dots"): "dots",
            _("steps"): "steps",
        }
        selected_style = _style_reverse.get(selected_style, selected_style)
        
        for i, expr in enumerate(exprs):
            y = np.array([_eval_expression(expr, xi) for xi in x_arr])
            color = _COLORS[i % len(_COLORS)]
            
            if selected_style == "scatter":
                ax.scatter(x_arr, y, color=color, label=expr, s=20)
            elif selected_style == "bar":
                # Filter NaN for bar
                mask = ~np.isnan(y)
                x_f, y_f = x_arr[mask], y[mask]
                if len(x_f) > 0:
                    w = (x_f[1] - x_f[0]) * 0.8 if len(x_f) > 1 else 0.8
                    ax.bar(x_f, y_f, width=w, color=color, label=expr)
            elif selected_style == "histogram":
                # Filter NaN for histogram
                mask = ~np.isnan(y)
                y_f = y[mask]
                if len(y_f) > 0:
                    ax.hist(y_f, bins="auto", color=color, label=expr, alpha=0.7)
            elif selected_style == "steps":
                ax.step(x_arr, y, where="post", linewidth=1.5, color=color, label=expr)
            else:
                # lines, points+lines, dots use format strings
                draw_style = style_map.get(selected_style, "-")
                ax.plot(x_arr, y, draw_style, linewidth=1.5, color=color, label=expr)

        title = self._title_var.get().strip()
        if title:
            ax.set_title(title, fontsize=11)
        ax.set_xlabel("x")
        ax.set_ylabel(", ".join(exprs) if len(exprs) == 1 else "y")

        if self._grid_var.get():
            ax.grid(True, alpha=0.3, linestyle="--")

        if self._legend_var.get():
            ax.legend(fontsize=9, loc="best")

        fig.tight_layout()

        # Embed in tkinter
        canvas = self._FigureCanvasTkAgg(fig, master=self._canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = self._NavigationToolbar2Tk(canvas, self._toolbar_frame)
        toolbar.update()

        self._fig = fig
        self._ax = ax
        self._canvas = canvas
        self._toolbar = toolbar

    # ------------------------------------------------------------------
    # Expression list management
    # ------------------------------------------------------------------

    def _add_expression(self, expr: str) -> None:
        """Add an expression to the list."""
        self._expressions.append(expr)
        self._expr_listbox.insert(tk.END, expr if expr else _("(empty)"))

    def _sync_listbox(self) -> None:
        """Rebuild the listbox from the internal expression list."""
        self._expr_listbox.delete(0, tk.END)
        for e in self._expressions:
            self._expr_listbox.insert(tk.END, e if e else _("(empty)"))

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_plot(self) -> None:
        """Handle Plot button click."""
        self._render_plot()

    def _on_add(self) -> None:
        """Open a simple entry popup to add an expression."""
        self._prompt_expression(_("Add Expression"))

    def _on_remove(self) -> None:
        """Remove the selected expression."""
        sel = self._expr_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(self._expressions):
            del self._expressions[idx]
            self._sync_listbox()

    def _on_edit(self) -> None:
        """Edit the selected expression."""
        sel = self._expr_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(self._expressions):
            self._prompt_expression(_("Edit Expression"), idx=idx)

    def _prompt_expression(self, title: str, idx: int | None = None) -> None:
        """Show a simple dialog to enter/edit an expression."""
        if self._dialog is None:
            return

        popup = tk.Toplevel(self._dialog)
        popup.title(title)
        popup.geometry("360x100")
        popup.transient(self._dialog)
        popup.grab_set()
        popup.resizable(False, False)
        popup.configure(bg=self._theme.bg)

        ttk.Label(popup, text=_("Expression:")).grid(
            row=0, column=0, padx=8, pady=(12, 4), sticky="w",
        )
        init_val = self._expressions[idx] if idx is not None and 0 <= idx < len(self._expressions) else ""
        var = tk.StringVar(value=init_val)
        entry = ttk.Entry(popup, textvariable=var, width=30)
        entry.grid(row=0, column=1, padx=(0, 8), pady=(12, 4), sticky="ew")
        entry.select_range(0, tk.END)
        entry.focus_set()
        popup.columnconfigure(1, weight=1)

        def _confirm() -> None:
            val = var.get().strip()
            if idx is not None:
                self._expressions[idx] = val
            else:
                self._expressions.append(val)
            self._sync_listbox()
            popup.destroy()

        popup.bind("<Return>", lambda _: _confirm())

        ttk.Button(popup, text=_("OK"), command=_confirm, width=8).grid(
            row=1, column=0, columnspan=2, pady=8,
        )

    # ---- Save ----

    def _on_save_png(self) -> None:
        """Save the current figure as PNG."""
        self._save_figure("png")

    def _on_save_svg(self) -> None:
        """Save the current figure as SVG."""
        self._save_figure("svg")

    def _save_figure(self, fmt: str) -> None:
        """Save figure to file via file dialog."""
        if self._fig is None:
            if self._dialog is not None:
                messagebox.showinfo(
                    _("No Plot"),
                    _("Nothing to save. Click Plot first."),
                    parent=self._dialog,
                )
            return

        ftypes = {
            "png": [("PNG Image", "*.png"), ("All Files", "*.*")],
            "svg": [("SVG Vector", "*.svg"), ("All Files", "*.*")],
        }
        path = filedialog.asksaveasfilename(
            parent=self._dialog,
            title=_("Save Plot as {}").format(fmt.upper()),
            defaultextension=f".{fmt}",
            filetypes=ftypes.get(fmt, [("All Files", "*.*")]),
        )
        if not path:
            return

        try:
            self._fig.savefig(path, dpi=150, bbox_inches="tight", format=fmt)
            if self._dialog is not None:
                messagebox.showinfo(
                    _("Saved"),
                    _("Plot saved to:\n{}").format(path),
                    parent=self._dialog,
                )
        except Exception as exc:
            if self._dialog is not None:
                messagebox.showerror(
                    _("Save Error"),
                    _("Failed to save:\n{}").format(exc),
                    parent=self._dialog,
                )

    # ---- Clear ----

    def _on_clear(self) -> None:
        """Clear all expressions and the plot."""
        self._expressions.clear()
        self._sync_listbox()
        if self._fig is not None:
            import matplotlib.pyplot as plt

            plt.close(self._fig)
            self._fig = None
            self._ax = None
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        if self._toolbar is not None:
            self._toolbar.destroy()
            self._toolbar = None
        self._placeholder.pack(expand=True)

    # ---- Close (override base to clean up matplotlib) ----

    def _on_cancel(self) -> None:
        """Clean up matplotlib resources and close."""
        import matplotlib.pyplot as plt

        if self._fig is not None:
            plt.close(self._fig)
            self._fig = None
            self._ax = None
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        if self._toolbar is not None:
            self._toolbar.destroy()
            self._toolbar = None
        super()._on_cancel()
