"""Tests for StepperTheme, StepDefinition, and StepStatus."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from stepper import (
    LogPosition,
    StepDefinition,
    StepStatus,
    StepperTheme,
)


# ---------------------------------------------------------------------------
# StepperTheme tests
# ---------------------------------------------------------------------------


def test_theme_defaults() -> None:
    theme = StepperTheme()
    assert theme.completed_symbol == "●"
    assert theme.active_symbol == "◉"
    assert theme.pending_symbol == "○"
    assert theme.completed_style == "green"
    assert theme.active_style == "cyan bold"
    assert theme.pending_style == "bright_black"
    assert theme.connector_symbol == "│"
    assert theme.connector_style == "bright_black"
    assert theme.line_thickness == 1
    assert theme.step_gap == 0
    assert theme.label_style == ""
    assert theme.step_description_style == "dim"
    assert theme.label_padding == 1


def test_theme_connector_glyph_default() -> None:
    theme = StepperTheme()
    assert theme.connector_glyph() == "│"


def test_theme_connector_glyph_thick() -> None:
    theme = StepperTheme(line_thickness=3)
    assert theme.connector_glyph() == "│││"


def test_theme_connector_glyph_negative_thickness() -> None:
    theme = StepperTheme(line_thickness=-1)
    assert theme.connector_glyph() == "│"


def test_theme_frozen_immutability() -> None:
    theme = StepperTheme()
    with pytest.raises(FrozenInstanceError):
        theme.completed_symbol = "X"  # type: ignore[misc]


def test_theme_new_field_defaults() -> None:
    """Verify all 11 new fields (added after initial theme) have correct defaults."""
    theme = StepperTheme()
    # Progress bar fields
    assert theme.show_elapsed_time is False
    assert theme.time_style == "progress.elapsed"
    assert theme.show_bar is False
    assert theme.bar_width == 20
    assert theme.bar_complete_style == "bar.complete"
    assert theme.bar_finished_style == "bar.finished"
    assert theme.bar_pulse_style == "bar.pulse"
    # Logging fields
    assert theme.log_position is LogPosition.BELOW
    assert theme.max_log_rows is None
    assert theme.log_style == "dim italic"
    assert theme.log_prefix == "›"


def test_theme_new_field_custom() -> None:
    """Verify all 11 new fields can be customized."""
    theme = StepperTheme(
        show_elapsed_time=True,
        time_style="bold magenta",
        show_bar=True,
        bar_width=40,
        bar_complete_style="green bold",
        bar_finished_style="green",
        bar_pulse_style="red",
        log_position=LogPosition.ABOVE,
        max_log_rows=5,
        log_style="cyan",
        log_prefix="→",
    )
    assert theme.show_elapsed_time is True
    assert theme.time_style == "bold magenta"
    assert theme.show_bar is True
    assert theme.bar_width == 40
    assert theme.bar_complete_style == "green bold"
    assert theme.bar_finished_style == "green"
    assert theme.bar_pulse_style == "red"
    assert theme.log_position is LogPosition.ABOVE
    assert theme.max_log_rows == 5
    assert theme.log_style == "cyan"
    assert theme.log_prefix == "→"


# ---------------------------------------------------------------------------
# StepDefinition tests
# ---------------------------------------------------------------------------


def test_step_definition_defaults() -> None:
    step = StepDefinition(label="Test")
    assert step.label == "Test"
    assert step.status is StepStatus.PENDING
    assert step.step_description is None


def test_step_definition_custom() -> None:
    step = StepDefinition(
        label="Custom",
        status=StepStatus.COMPLETED,
        step_description="A custom step",
    )
    assert step.label == "Custom"
    assert step.status is StepStatus.COMPLETED
    assert step.step_description == "A custom step"


def test_step_definition_frozen() -> None:
    step = StepDefinition(label="Test")
    with pytest.raises(FrozenInstanceError):
        step.label = "X"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# StepStatus tests
# ---------------------------------------------------------------------------


def test_step_status_values() -> None:
    assert len(list(StepStatus)) == 3


def test_step_status_value_strings() -> None:
    assert StepStatus.COMPLETED.value == "completed"
    assert StepStatus.ACTIVE.value == "active"
    assert StepStatus.PENDING.value == "pending"


def test_log_position_enum_values() -> None:
    assert LogPosition.BELOW.value == "below"
    assert LogPosition.ABOVE.value == "above"
