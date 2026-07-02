"""Tests for pyqalculate_gui.curve_fit_dialog.

Tests that require no Tk display are written against the public API directly.
Tests that depend on module-level tkinter imports use pytest.importorskip.
"""

from __future__ import annotations

import re

import pytest


# ---------------------------------------------------------------------------
# Minimal standalone copy of the LOGIC inside CurveFitDialog._parse_number_list.
# This avoids forcing a tkinter import when tkinter is not installed.
# The implementation is byte-for-byte identical to the source method.
# ---------------------------------------------------------------------------

def _parse_number_list(text: str) -> list[float]:
    """Mirror of CurveFitDialog._parse_number_list (no tkinter dependency)."""
    if not text.strip():
        return []
    parts = re.split(r"[,\s]+", text.strip())
    return [float(p) for p in parts if p]


# ---------------------------------------------------------------------------
# Unit tests — _parse_number_list (pure logic, no tkinter required)
# ---------------------------------------------------------------------------


class TestParseNumberList:
    """Given: the _parse_number_list parsing logic
    When:  called with various inputs
    Then:  returns expected float list or raises ValueError."""

    def test_comma_separated(self) -> None:
        """Parse comma-separated integers -> list of floats."""
        result = _parse_number_list("1, 2, 3")
        assert result == [1.0, 2.0, 3.0]

    def test_space_separated(self) -> None:
        """Parse space-separated integers -> list of floats."""
        result = _parse_number_list("1 2 3")
        assert result == [1.0, 2.0, 3.0]

    def test_negative_numbers(self) -> None:
        """Parse negative numbers including decimal."""
        result = _parse_number_list("-1, -2.5")
        assert result == [-1.0, -2.5]

    def test_decimals(self) -> None:
        """Parse decimal values including leading-dot form."""
        result = _parse_number_list(".5, 1.2")
        assert result == [0.5, 1.2]

    def test_empty_input_returns_empty_list(self) -> None:
        """Empty/blank input -> empty list."""
        result = _parse_number_list("")
        assert result == []
        assert isinstance(result, list)

    def test_whitespace_only_returns_empty_list(self) -> None:
        """Whitespace-only input -> empty list."""
        result = _parse_number_list("   ")
        assert result == []

    def test_trailing_comma_ignored(self) -> None:
        """Trailing comma produces no extra empty value - filtered out."""
        result = _parse_number_list("1,2,3,")
        assert result == [1.0, 2.0, 3.0]

    def test_blank_entries_skipped(self) -> None:
        """Double-comma (blank entry) is skipped."""
        result = _parse_number_list("1,,3")
        assert result == [1.0, 3.0]

    def test_non_numeric_raises_value_error(self) -> None:
        """Non-numeric tokens raise ValueError."""
        with pytest.raises(ValueError):
            _parse_number_list("a,b")

    def test_mixed_numeric_and_non_numeric_raises(self) -> None:
        """One non-numeric among valid numbers still raises ValueError."""
        with pytest.raises(ValueError):
            _parse_number_list("1, x, 3")


# ---------------------------------------------------------------------------
# Regression data - verify values consistent with TestRegressionFunctions
# ---------------------------------------------------------------------------


def test_parse_linear_data_consistent_with_regression_tests() -> None:
    """Parse y = 1,2,3,4,5 matches values used in test_linearfit_y_only."""
    result = _parse_number_list("1, 2, 3, 4, 5")
    assert result == [1.0, 2.0, 3.0, 4.0, 5.0]

    x_result = _parse_number_list("1, 2, 3")
    y_result = _parse_number_list("2, 4, 6")
    assert x_result == [1.0, 2.0, 3.0]
    assert y_result == [2.0, 4.0, 6.0]


# ---------------------------------------------------------------------------
# Event constant - no tkinter dependency
# ---------------------------------------------------------------------------


def test_event_constant() -> None:
    """OPEN_CURVE_FITTING equals the expected string constant."""
    from pyqalculate_gui.event_bus import OPEN_CURVE_FITTING

    assert OPEN_CURVE_FITTING == "open_curve_fitting"


# ---------------------------------------------------------------------------
# Import smoke - require tkinter (skipped in headless CI)
# ---------------------------------------------------------------------------


def test_curve_fit_dialog_importable() -> None:
    """CurveFitDialog can be imported from curve_fit_dialog module."""
    pytest.importorskip("tkinter", reason="tkinter not available in headless environment")
    from pyqalculate_gui.curve_fit_dialog import CurveFitDialog

    assert CurveFitDialog is not None


def test_curve_fit_dialog_is_modal_dialog_subclass() -> None:
    """CurveFitDialog extends ModalDialog."""
    pytest.importorskip("tkinter", reason="tkinter not available in headless environment")
    from pyqalculate_gui.curve_fit_dialog import CurveFitDialog
    from pyqalculate_gui.dialogs.base import ModalDialog

    assert issubclass(CurveFitDialog, ModalDialog)


# ---------------------------------------------------------------------------
# Optional: verify the standalone mirror matches the real static method
# (requires tkinter, so skipped in headless CI)
# ---------------------------------------------------------------------------


def test_mirror_identical_to_real_implementation() -> None:
    """The test helper _parse_number_list behaves identically to the real
    CurveFitDialog._parse_number_list."""
    pytest.importorskip("tkinter", reason="tkinter not available in headless environment")
    from pyqalculate_gui.curve_fit_dialog import CurveFitDialog

    test_inputs = [
        "1, 2, 3",
        "1 2 3",
        "-1, -2.5",
        ".5, 1.2",
        "",
        "   ",
        "1,2,3,",
        "1,,3",
    ]
    for inp in test_inputs:
        assert _parse_number_list(inp) == CurveFitDialog._parse_number_list(inp)

    for bad in ("a,b", "1, x, 3"):
        try:
            _parse_number_list(bad)
            raise AssertionError(f"Expected ValueError for {bad!r}")
        except ValueError:
            pass
        with pytest.raises(ValueError):
            CurveFitDialog._parse_number_list(bad)
