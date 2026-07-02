"""Plot module - function plotting for PyQalculate.

Mirrors libqalculate's Calculator::plot() functionality using matplotlib.
Supports single/multiple function plotting, data plotting, and calculator integration.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

from pyqalculate.types import (
    PlotDataParameters,
    PlotFileType,
    PlotParameters,
    PlotSmoothing,
    PlotStyle,
)

if TYPE_CHECKING:
    from pyqalculate.calculator import Calculator


# Default safe namespace for expression evaluation
_SAFE_MATH_NS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "exp": math.exp, "log": math.log, "ln": math.log, "log2": math.log2, "log10": math.log10,
    "sqrt": math.sqrt, "cbrt": lambda x: math.copysign(abs(x) ** (1/3), x),
    "pi": math.pi, "e": math.e, "tau": math.tau,
    "abs": abs, "sign": lambda x: (x > 0) - (x < 0),
    "floor": math.floor, "ceil": math.ceil,
    "factorial": math.factorial,
    "gamma": math.gamma, "lgamma": math.lgamma,
}


STYLE_DISPLAY_MAP: dict[PlotStyle, str] = {
    PlotStyle.LINES: "lines",
    PlotStyle.POINTS: "scatter",
    PlotStyle.BOXES: "bar",
    PlotStyle.HISTOGRAM: "histogram",
    PlotStyle.POINTS_LINES: "points+lines",
    PlotStyle.STEPS: "steps",
    PlotStyle.DOTS: "dots",
}


class PlotData:
    """Data for a single plot series."""

    def __init__(self) -> None:
        self.x_values: list[float] = []
        self.y_values: list[float] = []
        self.title: str = ""
        self.style: PlotStyle = PlotStyle.LINES


def _eval_expression(expression: str, x_val: float, var: str = "x") -> float:
    """Evaluate a mathematical expression at a given value.

    Uses a safe namespace with common math functions.

    Args:
        expression: The expression string (e.g., "x^2 + sin(x)").
        x_val: The value to evaluate at (assigned to *var*).
        var: The variable name to bind x_val to (default "x", use "t" for parametric).

    Returns:
        The computed value, or NaN on error.
    """
    ns = {**_SAFE_MATH_NS, var: x_val}
    # Convert ^ to ** for Python exponentiation
    expr = expression.replace("^", "**")
    try:
        result = eval(expr, {"__builtins__": {}}, ns)
        return float(result)
    except Exception:
        return float("nan")


class Plotter:
    """Function plotter using matplotlib.

    Provides plotting capabilities for mathematical functions and data,
    equivalent to libqalculate's plot functionality.

    Usage:
        plotter = Plotter(calculator)
        plotter.plot("x^2", x_min=-5, x_max=5, filename="plot.png")
        plotter.plot_multi(["sin(x)", "cos(x)"], x_min=0, x_max=6.28)
    """

    def __init__(self, calculator: Calculator | None = None) -> None:
        self._calculator = calculator
        import os
        try:
            import matplotlib
            if os.environ.get("DISPLAY") is None:
                matplotlib.use("Agg")
        except ImportError:
            pass

    def _render_with_style(self, ax, x, y, style: PlotStyle = PlotStyle.LINES, label: str = "", color: str = "") -> None:
        """Dispatch rendering to the appropriate matplotlib API based on PlotStyle."""
        import numpy as np

        kwargs: dict = {"label": label}
        if color:
            kwargs["color"] = color

        if style == PlotStyle.LINES:
            ax.plot(x, y, linewidth=1.5, **kwargs)
        elif style == PlotStyle.POINTS:
            ax.scatter(x, y, **kwargs)
        elif style == PlotStyle.BOXES:
            # Filter NaN only for bar (ax.bar errors on NaN)
            mask = ~np.isnan(y)
            x_f, y_f = x[mask], y[mask]
            if len(x_f) == 0:
                ax.text(0.5, 0.5, "All values are NaN", transform=ax.transAxes, ha="center", va="center")
                return
            w = (x_f[1] - x_f[0]) * 0.8 if len(x_f) > 1 else 0.8
            ax.bar(x_f, y_f, width=w, **kwargs)
        elif style == PlotStyle.HISTOGRAM:
            # Filter NaN for histogram
            mask = ~np.isnan(y)
            y_f = y[mask]
            if len(y_f) == 0:
                ax.text(0.5, 0.5, "All values are NaN", transform=ax.transAxes, ha="center", va="center")
                return
            ax.hist(y_f, bins="auto", **kwargs)
        elif style == PlotStyle.STEPS:
            ax.step(x, y, where="post", linewidth=1.5, **kwargs)
        elif style == PlotStyle.POINTS_LINES:
            ax.plot(x, y, "o-", linewidth=1.5, **kwargs)
        elif style == PlotStyle.DOTS:
            ax.plot(x, y, ".", linewidth=1.5, **kwargs)
        else:  # POLAR, CANDLESTICKS, etc.
            raise NotImplementedError(f"Plot style {style!r} is not yet implemented")

    def plot(
        self,
        expression: str,
        params: PlotParameters | None = None,
        x_min: float = -10.0,
        x_max: float = 10.0,
        num_points: int = 1000,
        filename: str = "",
        style: PlotStyle = PlotStyle.LINES,
    ) -> str:
        """Plot a mathematical expression.

        Args:
            expression: The expression to plot (e.g., "sin(x)", "x^2 + 1").
            params: Plot parameters (title, labels, file, etc.).
            x_min: Minimum x value.
            x_max: Maximum x value.
            num_points: Number of points to evaluate.
            filename: If provided, save to this file instead of showing.
            style: Plot style (lines, points, boxes, histogram, etc.).

        Returns:
            Path to saved file, or empty string if displayed interactively.
        """
        if params is None:
            params = PlotParameters()

        # Allow filename override
        if filename:
            params.filename = filename

        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise ImportError(
                "matplotlib is required for plotting. "
                "Install with: pip install matplotlib"
            )

        x = np.linspace(x_min, x_max, num_points)
        y = np.array([_eval_expression(expression, xi) for xi in x])

        fig, ax = plt.subplots(figsize=(10, 6))
        self._render_with_style(ax, x, y, style, label=expression)

        self._apply_axes_settings(ax, params, expression)
        ax.legend()

        return self._save_or_show(fig, params.filename)

    def plot_multi(
        self,
        expressions: Sequence[str],
        params: PlotParameters | None = None,
        x_min: float = -10.0,
        x_max: float = 10.0,
        num_points: int = 1000,
        filename: str = "",
        title: str = "",
        colors: Sequence[str] | None = None,
        styles: Sequence[PlotStyle] | None = None,
    ) -> str:
        """Plot multiple mathematical expressions on the same axes.

        Args:
            expressions: List of expressions to plot.
            params: Plot parameters.
            x_min: Minimum x value.
            x_max: Maximum x value.
            num_points: Number of points to evaluate.
            filename: If provided, save to this file.
            title: Plot title.
            colors: Optional list of colors for each expression.
            styles: Optional list of PlotStyle for each expression.

        Returns:
            Path to saved file, or empty string if displayed interactively.
        """
        if params is None:
            params = PlotParameters()
        if filename:
            params.filename = filename
        if title:
            params.title = title

        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise ImportError("matplotlib is required for plotting.")

        default_colors = ["blue", "red", "green", "orange", "purple",
                          "brown", "pink", "gray", "olive", "cyan"]
        if colors is None:
            colors = default_colors[:len(expressions)]

        x = np.linspace(x_min, x_max, num_points)
        fig, ax = plt.subplots(figsize=(10, 6))

        for i, expr in enumerate(expressions):
            y = np.array([_eval_expression(expr, xi) for xi in x])
            color = colors[i % len(colors)]
            s = styles[i] if styles else PlotStyle.LINES
            self._render_with_style(ax, x, y, s, label=expr, color=color)

        self._apply_axes_settings(ax, params, ", ".join(expressions))
        ax.legend()

        return self._save_or_show(fig, params.filename)

    def plot_data(
        self,
        x_values: list[float] | None,
        y_values: list[float],
        params: PlotParameters | None = None,
        filename: str = "",
        style: PlotStyle = PlotStyle.LINES,
    ) -> str:
        """Plot raw x/y data.

        Args:
            x_values: List of x values, or None for auto-generated indices.
            y_values: List of y values.
            params: Plot parameters.
            filename: If provided, save to this file.
            style: Plot style (lines, points, boxes, histogram, etc.).

        Returns:
            Path to saved file, or empty string if displayed interactively.
        """
        if params is None:
            params = PlotParameters()
        if filename:
            params.filename = filename

        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise ImportError("matplotlib is required for plotting.")

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.array(x_values) if x_values is not None else np.arange(len(y_values))
        y = np.array(y_values)
        self._render_with_style(ax, x, y, style, label="Data")

        self._apply_axes_settings(ax, params, "Data")
        return self._save_or_show(fig, params.filename)

    def generate_data(
        self,
        expression: str,
        x_min: float = -10.0,
        x_max: float = 10.0,
        num_points: int = 1000,
    ) -> PlotData:
        """Generate plot data without rendering.

        Useful for accessing computed data points programmatically.

        Args:
            expression: The expression to evaluate.
            x_min: Minimum x value.
            x_max: Maximum x value.
            num_points: Number of points.

        Returns:
            PlotData with x and y values.
        """
        data = PlotData()
        data.title = expression

        try:
            import numpy as np
            x_arr = np.linspace(x_min, x_max, num_points)
            data.x_values = [float(v) for v in x_arr]
        except ImportError:
            step = (x_max - x_min) / (num_points - 1)
            data.x_values = [x_min + i * step for i in range(num_points)]
        data.y_values = [_eval_expression(expression, xi) for xi in data.x_values]

        return data

    def _apply_axes_settings(
        self,
        ax,
        params: PlotParameters,
        default_ylabel: str,
    ) -> None:
        """Apply common axes settings from PlotParameters."""
        if params.title:
            ax.set_title(params.title)
        ax.set_xlabel(params.x_label or "x")
        ax.set_ylabel(params.y_label or default_ylabel)

        if params.grid:
            ax.grid(True, alpha=0.3)

        if not params.auto_x_min:
            ax.set_xlim(left=params.x_min)
        if not params.auto_x_max:
            ax.set_xlim(right=params.x_max)
        if not params.auto_y_min:
            ax.set_ylim(bottom=params.y_min)
        if not params.auto_y_max:
            ax.set_ylim(top=params.y_max)

    def plot_parametric(
        self,
        x_expr: str,
        y_expr: str,
        filename: str = "",
        t_min: float = 0.0,
        t_max: float = 6.283185307179586,
        num_points: int = 1000,
        title: str = "",
    ) -> str:
        """Plot a parametric curve x(t), y(t).

        Args:
            x_expr: Expression for x in terms of t (e.g., "(1+cos(t))*cos(t)").
            y_expr: Expression for y in terms of t (e.g., "(1+cos(t))*sin(t)").
            filename: If provided, save to this file.
            t_min: Minimum t value (default: 0).
            t_max: Maximum t value (default: 2*pi).
            num_points: Number of points to evaluate.
            title: Plot title.

        Returns:
            Path to saved file, or empty string if displayed interactively.
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise ImportError("matplotlib is required for plotting.")

        t = np.linspace(t_min, t_max, num_points)
        x_vals = np.array([_eval_expression(x_expr, ti, var="t") for ti in t])
        y_vals = np.array([_eval_expression(y_expr, ti, var="t") for ti in t])

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.plot(x_vals, y_vals, linewidth=1.5, color="blue")
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Parametric: x={x_expr}, y={y_expr}")

        return self._save_or_show(fig, filename)

    def plot_implicit(
        self,
        expr_str: str,
        filename: str = "",
        x_range: tuple[float, float] = (-5.0, 5.0),
        y_range: tuple[float, float] = (-5.0, 5.0),
        resolution: int = 400,
        title: str = "",
    ) -> str:
        """Plot an implicit function f(x,y) = 0 using contour.

        Args:
            expr_str: Expression in x and y (e.g., "x^2 + y^2 - 1").
            filename: If provided, save to this file.
            x_range: Tuple (x_min, x_max).
            y_range: Tuple (y_min, y_max).
            resolution: Grid resolution (NxN points).
            title: Plot title.

        Returns:
            Path to saved file, or empty string if displayed interactively.
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise ImportError("matplotlib is required for plotting.")

        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)

        # Evaluate the expression over the grid
        Z = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                ns = {**_SAFE_MATH_NS, "x": X[i, j], "y": Y[i, j]}
                expr = expr_str.replace("^", "**")
                try:
                    Z[i, j] = float(eval(expr, {"__builtins__": {}}, ns))
                except Exception:
                    Z[i, j] = float("nan")

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.contour(X, Y, Z, levels=[0], colors="blue", linewidths=2)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Implicit: {expr_str} = 0")

        return self._save_or_show(fig, filename)

    def plot_subplot(
        self,
        subplot_specs: list[dict],
        rows: int = 1,
        cols: int = 1,
        filename: str = "",
    ) -> str:
        """Plot multiple subplots in a single figure.

        Args:
            subplot_specs: List of dicts, each with keys:
                - ``'type'``: ``'plot'``, ``'parametric'``, or ``'implicit'``
                - ``'args'``: dict of args for that plot type
            rows: Number of subplot rows.
            cols: Number of subplot columns.
            filename: If provided, save to this file.

        Returns:
            Path to saved file, or empty string if displayed interactively.
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise ImportError("matplotlib is required for plotting.")

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
        # Flatten axes to 1D for easy indexing
        if rows == 1 and cols == 1:
            axes_flat = [axes]
        else:
            axes_flat = list(axes.flat) if hasattr(axes, "flat") else [axes]

        for i, spec in enumerate(subplot_specs):
            if i >= len(axes_flat):
                break
            ax = axes_flat[i]
            plot_type = spec.get("type", "plot")
            args = spec.get("args", {})

            if plot_type == "plot":
                expr = args.get("expression", "")
                x_min = args.get("x_min", -10.0)
                x_max = args.get("x_max", 10.0)
                num_points = args.get("num_points", 1000)
                x = np.linspace(x_min, x_max, num_points)
                y = np.array([_eval_expression(expr, xi) for xi in x])
                ax.plot(x, y, linewidth=1.5, label=expr)
                ax.set_xlabel("x")
                ax.set_ylabel(expr)
                ax.legend()
                ax.grid(True, alpha=0.3)

            elif plot_type == "parametric":
                x_expr = args.get("x_expr", "")
                y_expr = args.get("y_expr", "")
                t_min = args.get("t_min", 0.0)
                t_max = args.get("t_max", 6.283185307179586)
                num_points = args.get("num_points", 1000)
                t = np.linspace(t_min, t_max, num_points)
                x_vals = np.array(
                    [_eval_expression(x_expr, ti, var="t") for ti in t]
                )
                y_vals = np.array(
                    [_eval_expression(y_expr, ti, var="t") for ti in t]
                )
                ax.plot(x_vals, y_vals, linewidth=1.5)
                ax.set_aspect("equal")
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.grid(True, alpha=0.3)
                ax.set_title(f"x={x_expr}, y={y_expr}")

            elif plot_type == "implicit":
                expr_str = args.get("expression", "")
                x_range = args.get("x_range", (-5.0, 5.0))
                y_range = args.get("y_range", (-5.0, 5.0))
                resolution = args.get("resolution", 200)
                x = np.linspace(x_range[0], x_range[1], resolution)
                y = np.linspace(y_range[0], y_range[1], resolution)
                X, Y = np.meshgrid(x, y)
                Z = np.zeros_like(X)
                for ii in range(resolution):
                    for jj in range(resolution):
                        ns = {
                            **_SAFE_MATH_NS,
                            "x": X[ii, jj],
                            "y": Y[ii, jj],
                        }
                        e = expr_str.replace("^", "**")
                        try:
                            Z[ii, jj] = float(
                                eval(e, {"__builtins__": {}}, ns)
                            )
                        except Exception:
                            Z[ii, jj] = float("nan")
                ax.contour(X, Y, Z, levels=[0], colors="blue", linewidths=2)
                ax.set_aspect("equal")
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.grid(True, alpha=0.3)
                ax.set_title(f"{expr_str} = 0")

        plt.tight_layout()
        return self._save_or_show(fig, filename)

    @staticmethod
    def _save_or_show(fig, filename: str) -> str:
        """Save figure to file or show interactively."""
        import matplotlib.pyplot as plt

        if filename:
            try:
                fig.savefig(filename, dpi=150, bbox_inches="tight")
                return filename
            finally:
                plt.close(fig)
        else:
            plt.show()
            plt.close(fig)
            return ""
