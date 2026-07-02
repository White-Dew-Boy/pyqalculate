"""Curve Fitting dialog for linear, quadratic, and cubic regression.

Provides a modal dialog where users enter X/Y data points, select a fit
type, compute the regression via the Calculator service, and visualise
the result with a matplotlib scatter+fit plot.
"""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk

from pyqalculate_gui.calculator_service import CalculatorService
from pyqalculate_gui.dialogs.base import ModalDialog
from pyqalculate_gui.event_bus import EventBus
from pyqalculate_gui.i18n import _
from pyqalculate_gui.theme import LIGHT, Theme

_FIT_TYPE_MAP: dict[str, str] = {
    "Linear": "linearfit",
    "Quadratic": "quadraticfit",
    "Cubic": "cubicfit",
}

_DEGREE_MAP: dict[str, int] = {
    "Linear": 1,
    "Quadratic": 2,
    "Cubic": 3,
}


class CurveFitDialog(ModalDialog):
    """Modal dialog for curve fitting — linear, quadratic, cubic."""

    def __init__(
        self,
        parent: tk.Widget,
        theme: Theme = LIGHT,
        event_bus: EventBus | None = None,
        calculator: CalculatorService | None = None,
    ) -> None:
        super().__init__(
            parent,
            title=_("Curve Fitting"),
            size=(750, 680),
            resizable=(True, True),
            theme=theme,
            show_ok=False,
        )
        self._event_bus = event_bus
        self._calculator = calculator
        self._fit_type = tk.StringVar(value="Linear")

        # Lazy matplotlib imports
        self._FigureCanvasTkAgg: type | None = None
        self._NavigationToolbar2Tk: type | None = None

        # Widget references — populated by _build_content
        self._x_text: tk.Text | None = None
        self._y_text: tk.Text | None = None
        self._result_label: ttk.Label | None = None
        self._plot_frame: ttk.Frame | None = None

        # Matplotlib state
        self._canvas: object | None = None

        # Stored result string for "Insert to Expression"
        self._result_text: str = ""

    # ------------------------------------------------------------------
    # Content (ModalDialog contract)
    # ------------------------------------------------------------------

    def _build_content(self, parent: ttk.Frame) -> None:
        """Build the dialog body."""
        # --- Data input frame ---
        data_frame = ttk.LabelFrame(parent, text=_("Data"), padding=5)
        data_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(data_frame, text=_("X values:")).pack(anchor=tk.W)
        self._x_text = tk.Text(
            data_frame,
            height=2,
            width=60,
            font=self._theme.info_font,
            bg=self._theme.entry_bg,
            fg=self._theme.fg,
        )
        self._x_text.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(data_frame, text=_("Y values:")).pack(anchor=tk.W)
        self._y_text = tk.Text(
            data_frame,
            height=2,
            width=60,
            font=self._theme.info_font,
            bg=self._theme.entry_bg,
            fg=self._theme.fg,
        )
        self._y_text.pack(fill=tk.X)

        # --- Fit type frame ---
        fit_frame = ttk.LabelFrame(parent, text=_("Fit Type"), padding=5)
        fit_frame.pack(fill=tk.X, pady=(0, 10))

        for fit_type_key in ("Linear", "Quadratic", "Cubic"):
            ttk.Radiobutton(
                fit_frame,
                text=_(fit_type_key),
                value=fit_type_key,
                variable=self._fit_type,
            ).pack(side=tk.LEFT, padx=10)

        # --- Action buttons ---
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            action_frame, text=_("Fit"), command=self._on_fit,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            action_frame, text=_("Clear"), command=self._on_clear,
        ).pack(side=tk.LEFT)

        # --- Result area ---
        self._result_label = ttk.Label(
            parent,
            text="",
            wraplength=600,
            font=self._theme.info_font,
        )
        self._result_label.pack(fill=tk.X, pady=(0, 10))

        # --- Plot canvas frame ---
        self._plot_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        self._plot_frame.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Extra buttons
    # ------------------------------------------------------------------

    def _add_extra_buttons(self, btn_frame: ttk.Frame) -> None:
        """Add "Insert to Expression" button to the bottom bar."""
        ttk.Button(
            btn_frame, text=_("Insert to Expression"),
            command=self._on_insert,
        ).pack(side=tk.RIGHT, padx=5)

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_number_list(text: str) -> list[float]:
        """Parse comma- and/or space-separated text into a list of floats.

        Returns an empty list for blank input.  Raises ``ValueError``
        when any token cannot be converted to float.
        """
        if not text.strip():
            return []
        parts = re.split(r"[,\s]+", text.strip())
        return [float(p) for p in parts if p]

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_fit(self) -> None:
        """Parse inputs, compute the regression, and render the plot."""
        x_text = self._x_text.get("1.0", "end-1c") if self._x_text else ""
        y_text = self._y_text.get("1.0", "end-1c") if self._y_text else ""

        # --- Parse ---
        try:
            x = self._parse_number_list(x_text)
            y = self._parse_number_list(y_text)
        except ValueError:
            if self._result_label is not None:
                self._result_label.config(
                    text=_("Error: Invalid numbers in input."))
            return

        if not y:
            if self._result_label is not None:
                self._result_label.config(
                    text=_("Error: No Y values provided."))
            return

        # Auto-generate X if needed
        if not x:
            x = list(range(1, len(y) + 1))

        # --- Compute via CalculatorService ---
        fit_type = self._fit_type.get()
        func_name = _FIT_TYPE_MAP.get(fit_type, "linearfit")

        x_str = ", ".join(str(v) for v in x)
        y_str = ", ".join(str(v) for v in y)
        expression = f"{func_name}([{x_str}], [{y_str}])"

        if self._calculator is None:
            if self._result_label is not None:
                self._result_label.config(
                    text=_("Error: No calculator service."))
            return

        result = self._calculator.calculate(expression)

        if result.error:
            self._result_text = ""
            if self._result_label is not None:
                self._result_label.config(
                    text=_("Error: {}").format(result.error))
        else:
            self._result_text = result.result
            if self._result_label is not None:
                self._result_label.config(text=result.result)

        # --- Render plot ---
        self._render_plot(x, y)

    def _on_clear(self) -> None:
        """Clear all inputs and the plot."""
        if self._x_text is not None:
            self._x_text.delete("1.0", tk.END)
        if self._y_text is not None:
            self._y_text.delete("1.0", tk.END)
        if self._result_label is not None:
            self._result_label.config(text="")
        self._result_text = ""
        self._clear_canvas()

    def _on_insert(self) -> None:
        """Emit the current result string to the expression via the event
        bus."""
        if self._result_text and self._event_bus is not None:
            self._event_bus.emit("keypad_insert", self._result_text)

    # ------------------------------------------------------------------
    # Matplotlib helpers
    # ------------------------------------------------------------------

    def _init_matplotlib(self) -> None:
        """Lazy-import matplotlib tkinter classes."""
        if self._FigureCanvasTkAgg is not None:
            return
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.backends._backend_tk import NavigationToolbar2Tk

            self._FigureCanvasTkAgg = FigureCanvasTkAgg
            self._NavigationToolbar2Tk = NavigationToolbar2Tk
        except ImportError:
            if self._result_label is not None:
                self._result_label.config(
                    text=_(
                        "matplotlib is required for plotting.\n"
                        "Install with: pip install matplotlib",
                    ),
                )

    def _render_plot(self, x: list[float], y: list[float]) -> None:
        """Render a scatter plot with the fitted polynomial overlaid."""
        self._init_matplotlib()
        if self._FigureCanvasTkAgg is None or self._NavigationToolbar2Tk is None:
            return

        import matplotlib.pyplot as plt
        import numpy as np

        # Clear previous canvas
        self._clear_canvas()

        x_arr = np.array(x)
        y_arr = np.array(y)

        fit_type = self._fit_type.get()
        degree = _DEGREE_MAP.get(fit_type, 1)

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor(self._theme.entry_bg)

        # Scatter the data points
        ax.scatter(x_arr, y_arr, color="blue", label=_("Data"), s=30)

        # Overlay the fit line (numpy polyfit for visualisation)
        try:
            if len(x_arr) > degree:
                coeffs = np.polyfit(x_arr, y_arr, degree)
                x_fine = np.linspace(x_arr.min(), x_arr.max(), 200)
                y_fine = np.polyval(coeffs, x_fine)
                ax.plot(
                    x_fine, y_fine, "r-", linewidth=1.5,
                    label=_(fit_type),
                )
        except (np.linalg.LinAlgError, ValueError):
            pass  # polyfit failed; keep the scatter-only view

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, linestyle="--")
        fig.tight_layout()

        # Embed in tkinter
        canvas = self._FigureCanvasTkAgg(fig, master=self._plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas = canvas

    def _clear_canvas(self) -> None:
        """Destroy the embedded matplotlib canvas if it exists."""
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
