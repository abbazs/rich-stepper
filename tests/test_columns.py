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
from stepper.columns import LogRenderer, StatusMapper, StepperTimeColumn


# ---------------------------------------------------------------------------
# StatusMapper tests
# ---------------------------------------------------------------------------


def test_status_mapper_returns_correct_symbol_and_style() -> None:
    theme = StepperTheme(
        completed_symbol="C",
        completed_style="green",
        active_symbol="A",
        active_style="cyan",
        pending_symbol="P",
        pending_style="dim",
    )
    mapper = StatusMapper(theme)
    assert mapper.symbol_and_style(StepStatus.COMPLETED) == ("C", "green")
    assert mapper.symbol_and_style(StepStatus.ACTIVE) == ("A", "cyan")
    assert mapper.symbol_and_style(StepStatus.PENDING) == ("P", "dim")


def test_status_mapper_style_shortcut() -> None:
    theme = StepperTheme(completed_style="bold green")
    mapper = StatusMapper(theme)
    assert mapper.style(StepStatus.COMPLETED) == "bold green"


# ---------------------------------------------------------------------------
# LogRenderer tests
# ---------------------------------------------------------------------------


def test_log_renderer_visible_count_fixed() -> None:
    theme = StepperTheme(max_log_rows=3)
    renderer = LogRenderer(theme)
    assert renderer.visible_count(10, None) == 3


def test_log_renderer_visible_count_unbounded() -> None:
    theme = StepperTheme(max_log_rows=None)
    renderer = LogRenderer(theme)
    assert renderer.visible_count(10, 5) == 5


def test_log_renderer_visible_count_zero() -> None:
    theme = StepperTheme(max_log_rows=0)
    renderer = LogRenderer(theme)
    assert renderer.visible_count(10, None) == 0


def test_log_renderer_visible_count_no_logs() -> None:
    theme = StepperTheme(max_log_rows=5)
    renderer = LogRenderer(theme)
    assert renderer.visible_count(0, None) == 0


def test_log_renderer_build_lines_with_prefix() -> None:
    theme = StepperTheme(log_prefix="->", label_padding=2)
    renderer = LogRenderer(theme)
    lines = renderer.build_lines(["hello"], None)
    assert len(lines) == 1
    assert "-> hello" in lines[0].plain


# ---------------------------------------------------------------------------
# StepLabelColumn tests
# ---------------------------------------------------------------------------


def test_label_merge_styles_multiple() -> None:
    assert StepLabelColumn._merge_styles("bold", "red") == "bold red"


def test_label_merge_styles_empty() -> None:
    assert StepLabelColumn._merge_styles("", "") == ""


def test_label_merge_styles_single() -> None:
    assert StepLabelColumn._merge_styles("bold") == "bold"


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
    assert "-:--:--" not in output


def test_time_column_custom_style() -> None:
    """Verify custom time_style is applied to rendered output."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(show_elapsed_time=True, time_style="bold magenta")
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Styled Step", status=StepStatus.PENDING)
    console.print(stepper)
    output = console.export_text()
    assert "-:--:--" in output
    time_col = StepperTimeColumn(theme)
    assert time_col._theme.time_style == "bold magenta"
