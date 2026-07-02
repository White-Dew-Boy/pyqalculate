"""Publish-subscribe event bus for decoupled widget communication."""

from __future__ import annotations

from typing import Any, Callable

# Event constants
EXPRESSION_SUBMITTED = "expression_submitted"
RESULT_DISPLAYED = "result_displayed"
HISTORY_RECALLED = "history_recalled"
HISTORY_UPDATED = "history_updated"
MODE_CHANGED = "mode_changed"
PREFERENCE_APPLIED = "preference_applied"
CONVERSION_RESULT = "conversion_result"
CLEAR_ALL = "clear_all"
OPEN_NUMBER_BASES = "open_number_bases"
OPEN_PREFERENCES = "open_preferences"
OPEN_PLOT = "open_plot"
TOGGLE_HISTORY = "toggle_history"
TOGGLE_KEYPAD = "toggle_keypad"
TOGGLE_CONVERSION = "toggle_conversion"
OPEN_UNIT_CONVERSION = "open_unit_conversion"
OPEN_HISTORY_WINDOW = "open_history_window"
COPY_RESULT = "copy_result"
IMPORT_CSV = "import_csv"
EXPORT_CSV = "export_csv"
IMPORT_XLSX = "import_xlsx"
EXPORT_XLSX = "export_xlsx"
OPEN_HELP_DOC = "open_help_doc"


class EventBus:
    """Simple publish-subscribe event bus."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[..., Any]]] = {}

    def subscribe(self, event: str, callback: Callable[..., Any]) -> None:
        """Subscribe to an event."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        if callback not in self._subscribers[event]:
            self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable[..., Any]) -> None:
        """Unsubscribe from an event."""
        if event in self._subscribers:
            self._subscribers[event] = [
                cb for cb in self._subscribers[event] if cb != callback
            ]

    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event to all subscribers."""
        if event in self._subscribers:
            for callback in self._subscribers[event]:
                callback(*args, **kwargs)
