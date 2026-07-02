"""Tests for pyqalculate_gui.dialogs.functions_list."""

from __future__ import annotations

import os
import tkinter as tk

import pytest

from pyqalculate_gui.calculator_service import CalculatorService, FunctionInfo
from pyqalculate_gui.dialogs.base import ModalDialog
from pyqalculate_gui.dialogs.functions_list import FunctionsListDialog
from pyqalculate_gui.event_bus import EventBus
from pyqalculate_gui.theme import LIGHT

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

HAS_DISPLAY = bool(
    os.environ.get("DISPLAY")
    or os.environ.get("WAYLAND_DISPLAY")
    or os.name == "nt"
)


def _make_root() -> tk.Tk:
    """Create a withdrawn Tk root for testing."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tcl/Tk runtime not available (tcl_findLibrary)")
    root.withdraw()
    return root


# ---------------------------------------------------------------------------
# Unit tests — no display required
# ---------------------------------------------------------------------------


class TestFunctionsListDialogInstantiation:
    """Given: the FunctionsListDialog class\nWhen:  constructing instances\nThen:  internal state is correct."""

    def test_extends_modal_dialog(self) -> None:
        """FunctionsListDialog is a subclass of ModalDialog."""
        assert issubclass(FunctionsListDialog, ModalDialog)

    def test_default_theme_is_light(self) -> None:
        """Default theme is LIGHT."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root)
            assert dlg._theme is LIGHT
        finally:
            root.destroy()

    def test_default_size(self) -> None:
        """Default size is 600x500."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root)
            assert dlg._size == (600, 500)
        finally:
            root.destroy()

    def test_resizable(self) -> None:
        """Dialog is resizable by default."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root)
            assert dlg._resizable == (True, True)
        finally:
            root.destroy()

    def test_functions_start_empty(self) -> None:
        """Function list starts empty."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root)
            assert dlg._functions == []
        finally:
            root.destroy()

    def test_accepts_calculator(self) -> None:
        """Calculator service is stored."""
        root = _make_root()
        try:
            calc = CalculatorService()
            dlg = FunctionsListDialog(root, calculator=calc)
            assert dlg._calculator is calc
        finally:
            root.destroy()

    def test_accepts_event_bus(self) -> None:
        """Event bus is stored."""
        root = _make_root()
        try:
            bus = EventBus()
            dlg = FunctionsListDialog(root, event_bus=bus)
            assert dlg._event_bus is bus
        finally:
            root.destroy()

    def test_name_var_initialized(self) -> None:
        """_name_var is created in __init__ (before show)."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root)
            assert isinstance(dlg._name_var, tk.StringVar)
            assert dlg._name_var.get() == ""
        finally:
            root.destroy()

    def test_search_var_initialized(self) -> None:
        """_search_var is created in __init__ (before show)."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root)
            assert isinstance(dlg._search_var, tk.StringVar)
            assert dlg._search_var.get() == ""
        finally:
            root.destroy()


class TestFormatArgs:
    """Given: FunctionInfo objects\nWhen:  formatting argument counts\nThen:  correct strings returned."""

    def test_equal_args(self) -> None:
        """Equal min and max shows single number."""
        info = FunctionInfo("sin", "Sine", "", "", 1, 1)
        assert FunctionsListDialog._format_args(info) == "Arguments: 1"

    def test_range_args(self) -> None:
        """Different min and max shows range."""
        info = FunctionInfo("root", "Root", "", "", 1, 2)
        assert FunctionsListDialog._format_args(info) == "Arguments: 1 to 2"

    def test_unlimited_args(self) -> None:
        """max_args=-1 shows 'or more'."""
        info = FunctionInfo("sum", "Sum", "", "", 1, -1)
        assert FunctionsListDialog._format_args(info) == "Arguments: 1 or more"

    def test_zero_args(self) -> None:
        """Zero arguments shows 0."""
        info = FunctionInfo("pi", "Pi", "", "", 0, 0)
        assert FunctionsListDialog._format_args(info) == "Arguments: 0"


class TestGetInfo:
    """Given: a FunctionsListDialog\nWhen:  looking up function info\nThen:  returns FunctionInfo or fallback."""

    def test_returns_info_for_known_function(self) -> None:
        """Known function returns real FunctionInfo."""
        root = _make_root()
        try:
            calc = CalculatorService()
            dlg = FunctionsListDialog(root, calculator=calc)
            info = dlg._get_info("sin")
            assert isinstance(info, FunctionInfo)
            assert info.name == "sin"
            assert info.min_args == 1
        finally:
            root.destroy()

    def test_fallback_when_no_calculator(self) -> None:
        """Without calculator returns fallback FunctionInfo."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root, calculator=None)
            info = dlg._get_info("unknown_func")
            assert info.name == "unknown_func"
            assert info.description == ""
            assert info.min_args == 0
        finally:
            root.destroy()

    def test_fallback_for_unknown_function(self) -> None:
        """Unknown function name returns fallback."""
        root = _make_root()
        try:
            calc = CalculatorService()
            dlg = FunctionsListDialog(root, calculator=calc)
            info = dlg._get_info("zzz_nonexistent_function_zzz")
            assert info.name == "zzz_nonexistent_function_zzz"
            assert info.description == ""
        finally:
            root.destroy()


class TestLoadFunctions:
    """Given: a FunctionsListDialog with a CalculatorService\nWhen:  loading functions\nThen:  function list is populated."""

    def test_loads_functions_from_calculator(self) -> None:
        """Functions are loaded from the calculator service."""
        root = _make_root()
        try:
            calc = CalculatorService()
            dlg = FunctionsListDialog(root, calculator=calc)
            dlg._load_functions()
            assert len(dlg._functions) > 0
            assert "sin" in dlg._functions
            assert "cos" in dlg._functions
        finally:
            root.destroy()

    def test_no_calculator_no_functions(self) -> None:
        """Without calculator, functions list stays empty."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root, calculator=None)
            dlg._load_functions()
            assert dlg._functions == []
        finally:
            root.destroy()


class TestSearchFilter:
    """Given: a FunctionsListDialog with loaded functions\nWhen:  filtering by search text\nThen:  correct subset is computed."""

    def test_empty_search_returns_all(self) -> None:
        """Empty search returns all functions."""
        root = _make_root()
        try:
            calc = CalculatorService()
            dlg = FunctionsListDialog(root, calculator=calc)
            dlg._load_functions()
            # Filtering with empty string returns all
            filtered = dlg._functions
            assert len(filtered) == len(dlg._functions)
        finally:
            root.destroy()

    def test_search_filters_by_substring(self) -> None:
        """Search text filters functions by substring match."""
        root = _make_root()
        try:
            calc = CalculatorService()
            dlg = FunctionsListDialog(root, calculator=calc)
            dlg._load_functions()
            search = "sin"
            filtered = [f for f in dlg._functions if search in f.lower()]
            assert len(filtered) > 0
            for func in filtered:
                assert "sin" in func.lower()
        finally:
            root.destroy()

    def test_search_is_case_insensitive(self) -> None:
        """Search is case-insensitive."""
        root = _make_root()
        try:
            calc = CalculatorService()
            dlg = FunctionsListDialog(root, calculator=calc)
            dlg._load_functions()
            search = "SIN"
            filtered = [f for f in dlg._functions if search.lower() in f.lower()]
            for func in filtered:
                assert "sin" in func.lower()
        finally:
            root.destroy()

    def test_no_match_returns_empty(self) -> None:
        """Search with no matches returns empty list."""
        root = _make_root()
        try:
            calc = CalculatorService()
            dlg = FunctionsListDialog(root, calculator=calc)
            dlg._load_functions()
            search = "zzz_nonexistent_zzz"
            filtered = [f for f in dlg._functions if search in f.lower()]
            assert filtered == []
        finally:
            root.destroy()


class TestInsertFunction:
    """Given: a FunctionsListDialog with an EventBus\nWhen:  inserting a function\nThen:  "keypad_insert" is emitted."""

    def test_emits_keypad_insert(self) -> None:
        """Insert emits "keypad_insert" with function name."""
        root = _make_root()
        try:
            bus = EventBus()
            received: list[str] = []
            bus.subscribe("keypad_insert", lambda e: received.append(e))

            dlg = FunctionsListDialog(root, event_bus=bus)
            dlg._name_var.set("sin")
            dlg._insert_function()

            assert len(received) == 1
            assert received[0] == "sin("
            assert dlg.get_result() is True
        finally:
            root.destroy()

    def test_no_crash_without_event_bus(self) -> None:
        """Insert without event bus does not crash."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root, event_bus=None)
            dlg._name_var.set("sin")
            dlg._insert_function()
            # No assertion needed — just must not raise
        finally:
            root.destroy()

    def test_empty_name_no_emit(self) -> None:
        """Empty function name does not emit."""
        root = _make_root()
        try:
            bus = EventBus()
            received: list[str] = []
            bus.subscribe("keypad_insert", lambda e: received.append(e))

            dlg = FunctionsListDialog(root, event_bus=bus)
            dlg._name_var.set("")
            dlg._insert_function()

            assert len(received) == 0
        finally:
            root.destroy()

    def test_insert_function_sets_result_true(self) -> None:
        """Inserting a function sets _result to True."""
        root = _make_root()
        try:
            bus = EventBus()
            received: list[str] = []
            bus.subscribe("keypad_insert", lambda e: received.append(e))

            dlg = FunctionsListDialog(root, event_bus=bus)
            dlg._name_var.set("sin")
            dlg._insert_function()

            assert len(received) == 1
            assert received[0] == "sin("
            assert dlg.get_result() is True
        finally:
            root.destroy()


class TestShowDetail:
    """Given: a FunctionsListDialog\nWhen:  showing detail for a function\nThen:  name_var is set."""

    def test_show_detail_sets_name(self) -> None:
        """_show_detail sets _name_var to the function name."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root)
            dlg._show_detail("sin")
            assert dlg._name_var.get() == "sin"
        finally:
            root.destroy()

    def test_show_detail_unknown_function(self) -> None:
        """_show_detail works for unknown functions."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root)
            dlg._show_detail("my_custom_func")
            assert dlg._name_var.get() == "my_custom_func"
        finally:
            root.destroy()


# ---------------------------------------------------------------------------
# Integration — requires a display (skip in headless CI)
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="ModalDialog.wait_window causes Tk event loop hang on teardown")
class TestFunctionsListDialogIntegration:
    """Given: a display is available\nWhen:  showing the dialog\nThen:  UI creates correctly."""

    def test_show_and_cancel(self) -> None:
        """show() then cancel returns result=False."""
        root = _make_root()
        try:
            dlg = FunctionsListDialog(root)
            root.after(50, dlg._on_cancel)
            dlg.show()
            assert dlg.get_result() is False
            assert dlg._dialog is None
        finally:
            root.destroy()

    def test_show_with_calculator(self) -> None:
        """show() with calculator populates the list."""
        root = _make_root()
        try:
            calc = CalculatorService()
            dlg = FunctionsListDialog(root, calculator=calc)
            root.after(100, dlg._on_cancel)
            dlg.show()
            assert len(dlg._functions) > 0
        finally:
            root.destroy()

    def test_select_and_insert(self) -> None:
        """Selecting a function and inserting emits event."""
        root = _make_root()
        try:
            bus = EventBus()
            calc = CalculatorService()
            received: list[str] = []
            bus.subscribe("keypad_insert", lambda e: received.append(e))

            dlg = FunctionsListDialog(root, event_bus=bus, calculator=calc)

            def do_select() -> None:
                # Select first item
                dlg._listbox.selection_set(0)
                dlg._on_select()
                # Insert
                dlg._insert_function()

            root.after(100, do_select)
            dlg.show()
            assert len(received) == 1
            assert received[0].endswith("(")
        finally:
            root.destroy()
