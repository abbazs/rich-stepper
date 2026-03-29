"""Tests for column renderers: StepIndicatorColumn, StepLabelColumn, StepperTimeColumn."""

from __future__ import annotations

import pytest
from rich.console import Console

from stepper import (
    StepIndicatorColumn,
    StepLabelColumn,
    StepStatus,
    Stepper,
    StepperTheme,
)
from stepper.columns import HeightAwareLogRenderable, StepperTimeColumn


# ---------------------------------------------------------------------------
# StepIndicatorColumn tests
# ---------------------------------------------------------------------------


def test_indicator_symbol_for_completed() -> None:
    theme = StepperTheme()
    col = StepIndicatorColumn(theme)
    result = col._symbol_for(StepStatus.COMPLETED)
    assert result == (theme.completed_symbol, theme.completed_style)


def test_indicator_symbol_for_active() -> None:
    theme = StepperTheme()
    col = StepIndicatorColumn(theme)
    result = col._symbol_for(StepStatus.ACTIVE)
    assert result == (theme.active_symbol, theme.active_style)


def test_indicator_symbol_for_pending() -> None:
    theme = StepperTheme()
    col = StepIndicatorColumn(theme)
    result = col._symbol_for(StepStatus.PENDING)
    assert result == (theme.pending_symbol, theme.pending_style)


# ---------------------------------------------------------------------------
# StepLabelColumn tests
# ---------------------------------------------------------------------------


def test_label_merge_styles_multiple() -> None:
    assert StepLabelColumn._merge_styles("bold", "red") == "bold red"


def test_label_merge_styles_empty() -> None:
    assert StepLabelColumn._merge_styles("", "") == ""


def test_label_merge_styles_single() -> None:
    assert StepLabelColumn._merge_styles("bold") == "bold"


def test_label_status_style_completed() -> None:
    theme = StepperTheme()
    col = StepLabelColumn(theme)
    assert col._status_style(StepStatus.COMPLETED) == theme.completed_style


def test_label_status_style_active() -> None:
    theme = StepperTheme()
    col = StepLabelColumn(theme)
    assert col._status_style(StepStatus.ACTIVE) == theme.active_style


def test_label_status_style_pending() -> None:
    theme = StepperTheme()
    col = StepLabelColumn(theme)
    assert col._status_style(StepStatus.PENDING) == theme.pending_style


# ---------------------------------------------------------------------------
# StepperTimeColumn tests
# ---------------------------------------------------------------------------


def test_elapsed_time_shows_for_active_step() -> None:
    """ACTIVE step shows elapsed time in output."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(show_elapsed_time=True)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Active Step", status=StepStatus.ACTIVE)
    console.print(stepper)
    output = console.export_text()
    # Active step should show time format like "0:00:00"
    assert "0:00:00" in output


def test_elapsed_time_shows_dash_for_pending() -> None:
    """PENDING step shows '-:--:--' when elapsed time is None."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(show_elapsed_time=True)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Pending Step", status=StepStatus.PENDING)
    console.print(stepper)
    output = console.export_text()
    assert "-:--:--" in output


def test_elapsed_time_freezes_on_completion() -> None:
    """COMPLETED step shows frozen time (not ticking)."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(show_elapsed_time=True)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Done Step", status=StepStatus.ACTIVE)
    stepper.set_step_status(0, StepStatus.COMPLETED)
    console.print(stepper)
    output = console.export_text()
    # Completed step should show a time value (frozen), not "-:--:--"
    assert "-:--:--" not in output


def test_time_column_custom_style() -> None:
    """Verify custom time_style is applied to rendered output."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(show_elapsed_time=True, time_style="bold magenta")
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Styled Step", status=StepStatus.PENDING)
    console.print(stepper)
    output = console.export_text()
    # The time dash should appear regardless of style
    assert "-:--:--" in output
    # Verify the column was created with custom style
    time_col = StepperTimeColumn(theme)
    assert time_col._theme.time_style == "bold magenta"


# ---------------------------------------------------------------------------
# HeightAwareLogRenderable tests
# ---------------------------------------------------------------------------


def test_height_aware_renderable_empty_logs() -> None:
    """Empty logs list returns nothing (no yield)."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme()
    renderable = HeightAwareLogRenderable([], theme)
    with console.capture() as capture:
        console.print(renderable)
    assert capture.get().strip() == ""


def test_height_aware_renderable_zero_max_rows() -> None:
    """max_log_rows=0 returns nothing regardless of log content."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(max_log_rows=0)
    logs = ["msg1", "msg2", "msg3"]
    renderable = HeightAwareLogRenderable(logs, theme)
    with console.capture() as capture:
        console.print(renderable)
    assert capture.get().strip() == ""
