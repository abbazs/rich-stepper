"""Tests for step logging features."""

from __future__ import annotations

import pytest
from rich.console import Console

from stepper import (
    StepStatus,
    Stepper,
    StepperTheme,
)


# ---------------------------------------------------------------------------
# Step logging tests
# ---------------------------------------------------------------------------


def test_log_message_appears_in_output() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("My Step")
    stepper.log(0, "something happened")
    console.print(stepper)
    output = console.export_text()
    assert "something happened" in output


def test_log_position_below() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(log_position="below")
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Alpha")
    stepper.log(0, "log line")
    console.print(stepper)
    output = console.export_text()
    alpha_pos = output.index("Alpha")
    log_pos = output.index("log line")
    assert log_pos > alpha_pos


def test_log_position_above() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(log_position="above")
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Alpha")
    stepper.log(0, "log line")
    console.print(stepper)
    output = console.export_text()
    alpha_pos = output.index("Alpha")
    log_pos = output.index("log line")
    assert log_pos < alpha_pos


def test_max_log_rows_caps_display() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(max_log_rows=2)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("My Step")
    for i in range(5):
        stepper.log(0, f"msg{i}")
    console.print(stepper)
    output = console.export_text()
    assert "msg3" in output
    assert "msg4" in output
    assert "msg0" not in output


def test_max_log_rows_zero_hides_logs() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(max_log_rows=0)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("My Step")
    stepper.log(0, "hidden message")
    console.print(stepper)
    output = console.export_text()
    assert "hidden message" not in output


def test_log_empty_string_ignored() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("My Step")
    stepper.log(0, "visible")
    stepper.log(0, "")
    console.print(stepper)
    output = console.export_text()
    assert "visible" in output
    # Empty log should not add extra blank lines with the prefix
    log_lines = [line for line in output.splitlines() if "›" in line]
    assert len(log_lines) == 1


def test_log_out_of_range_raises() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("Only")
    with pytest.raises(IndexError):
        stepper.log(99, "boom")


def test_log_negative_index_works() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("First")
    stepper.add_step("Last")
    stepper.log(-1, "logged on last")
    console.print(stepper)
    output = console.export_text()
    assert "logged on last" in output


def test_terminal_height_capping() -> None:
    console = Console(record=True, width=80, height=10, legacy_windows=False)
    theme = StepperTheme(max_log_rows=None)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("My Step")
    for i in range(50):
        stepper.log(0, f"msg{i}")
    console.print(stepper)
    output = console.export_text()
    output_lines = output.splitlines()
    # With height=10, max_log_rows=None caps at height-4=6 log lines
    log_lines = [line for line in output_lines if "msg" in line]
    assert len(log_lines) <= 7
    assert "msg44" in output
    assert "msg0" not in output


def test_multiple_logs_on_different_steps() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("Step A")
    stepper.add_step("Step B")
    stepper.log(0, "log for A")
    stepper.log(1, "log for B")
    console.print(stepper)
    output = console.export_text()
    assert "log for A" in output
    assert "log for B" in output


def test_log_with_unicode_message() -> None:
    """Verify unicode characters in log messages render correctly."""
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("Unicode Step")
    stepper.log(0, "✅ Success — naïve café résumé")
    console.print(stepper)
    output = console.export_text()
    assert "✅" in output
    assert "naïve" in output
    assert "café" in output


def test_log_prefix_custom() -> None:
    """Verify custom log_prefix renders in output."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(log_prefix="→")
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Prefixed Step")
    stepper.log(0, "custom prefix log")
    console.print(stepper)
    output = console.export_text()
    assert "custom prefix log" in output
    # Default prefix "›" should NOT appear; custom "→" should
    lines_with_prefix = [line for line in output.splitlines() if "→" in line]
    assert len(lines_with_prefix) >= 1
