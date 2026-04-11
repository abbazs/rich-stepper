"""Integration tests for the Stepper Rich UI component."""

from __future__ import annotations

import pytest
from rich.console import Console

from stepper import (
    StepDefinition,
    StepStatus,
    Stepper,
    StepperTheme,
)


# ---------------------------------------------------------------------------
# Stepper core tests
# ---------------------------------------------------------------------------


def test_stepper_empty() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    console.print(stepper)
    # Should not raise — output is simply empty
    assert console.export_text() is not None


def test_stepper_single_step() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    steps = [StepDefinition("Only Step")]
    stepper = Stepper(steps=steps, console=console, auto_refresh=False)
    console.print(stepper)
    output = console.export_text()
    assert "Only Step" in output
    # Single step is last, so no connector should appear
    assert "│" not in output


def test_stepper_multiple_steps() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    steps = [
        StepDefinition("Alpha"),
        StepDefinition("Beta"),
        StepDefinition("Gamma"),
    ]
    stepper = Stepper(steps=steps, console=console, auto_refresh=False)
    console.print(stepper)
    output = console.export_text()
    assert "Alpha" in output
    assert "Beta" in output
    assert "Gamma" in output


def test_stepper_add_step_returns_task_id() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    task_id = stepper.add_step("Test")
    assert isinstance(task_id, int)


def test_stepper_add_steps_bulk() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_steps([StepDefinition("A"), StepDefinition("B")])
    console.print(stepper)
    output = console.export_text()
    assert "A" in output
    assert "B" in output


def test_stepper_set_step_status() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("My Step", status=StepStatus.PENDING)
    stepper.set_step_status(0, StepStatus.COMPLETED)
    console.print(stepper)
    output = console.export_text()
    # The completed symbol should appear in output
    assert "●" in output


def test_stepper_set_step_status_out_of_range() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("Only")
    with pytest.raises(IndexError):
        stepper.set_step_status(99, StepStatus.COMPLETED)


def test_stepper_set_step_status_negative_index() -> None:
    """Negative index accesses last element via Python list semantics."""
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("First", status=StepStatus.PENDING)
    stepper.add_step("Last", status=StepStatus.PENDING)
    stepper.set_step_status(-1, StepStatus.COMPLETED)
    console.print(stepper)
    output = console.export_text()
    assert "●" in output


# ---------------------------------------------------------------------------
# Stepper rendering tests
# ---------------------------------------------------------------------------


def test_render_contains_labels() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    steps = [
        StepDefinition("Step One", StepStatus.COMPLETED),
        StepDefinition("Step Two", StepStatus.ACTIVE),
        StepDefinition("Step Three", StepStatus.PENDING),
    ]
    stepper = Stepper(steps=steps, console=console, auto_refresh=False)
    console.print(stepper)
    output = console.export_text()
    assert "Step One" in output
    assert "Step Two" in output
    assert "Step Three" in output


def test_render_contains_step_description() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    steps = [
        StepDefinition("Step One", step_description="Description text"),
    ]
    stepper = Stepper(steps=steps, console=console, auto_refresh=False)
    console.print(stepper)
    output = console.export_text()
    assert "Description text" in output


def test_render_contains_connector() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    steps = [
        StepDefinition("First"),
        StepDefinition("Second"),
    ]
    stepper = Stepper(steps=steps, console=console, auto_refresh=False)
    console.print(stepper)
    output = console.export_text()
    assert "│" in output


def test_render_no_connector_for_last_step() -> None:
    """Last step has no connector line — verify connector count matches non-last steps."""
    console = Console(record=True, width=80, legacy_windows=False)
    steps = [
        StepDefinition("First"),
        StepDefinition("Second"),
        StepDefinition("Third"),
    ]
    stepper = Stepper(steps=steps, console=console, auto_refresh=False)
    console.print(stepper)
    output = console.export_text()
    # With 3 steps and step_gap=0: 2 non-last steps → 2 connector lines
    # Each connector line has 1 "│" (default thickness)
    connector_count = output.count("│")
    assert connector_count == 2


def test_render_custom_theme_symbols() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(
        completed_symbol="[OK]",
        active_symbol="[>>]",
        pending_symbol="[--]",
    )
    steps = [
        StepDefinition("Done", StepStatus.COMPLETED),
        StepDefinition("Doing", StepStatus.ACTIVE),
        StepDefinition("Todo", StepStatus.PENDING),
    ]
    stepper = Stepper(steps=steps, theme=theme, console=console, auto_refresh=False)
    console.print(stepper)
    output = console.export_text()
    assert "[OK]" in output
    assert "[>>]" not in output
    assert "[--]" in output


# ---------------------------------------------------------------------------
# Stepper with theme edge cases
# ---------------------------------------------------------------------------


def test_render_thick_connector() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(line_thickness=2)
    steps = [
        StepDefinition("First"),
        StepDefinition("Second"),
    ]
    stepper = Stepper(steps=steps, theme=theme, console=console, auto_refresh=False)
    console.print(stepper)
    output = console.export_text()
    # With line_thickness=2, connector_glyph returns "││"
    assert "││" in output


def test_render_step_gap() -> None:
    """step_gap=1 adds extra connector lines → more lines in output."""
    console = Console(record=True, width=80, legacy_windows=False)
    steps_no_gap = [
        StepDefinition("First"),
        StepDefinition("Second"),
    ]
    stepper_no_gap = Stepper(
        steps=steps_no_gap,
        theme=StepperTheme(step_gap=0),
        console=console,
        auto_refresh=False,
    )
    console.print(stepper_no_gap)
    output_no_gap = console.export_text()
    lines_no_gap = len(output_no_gap.splitlines())

    console2 = Console(record=True, width=80, legacy_windows=False)
    steps_gap = [
        StepDefinition("First"),
        StepDefinition("Second"),
    ]
    stepper_gap = Stepper(
        steps=steps_gap,
        theme=StepperTheme(step_gap=1),
        console=console2,
        auto_refresh=False,
    )
    console2.print(stepper_gap)
    output_gap = console2.export_text()
    lines_gap = len(output_gap.splitlines())

    assert lines_gap > lines_no_gap


def test_render_label_padding() -> None:
    """label_padding=3 adds 3 spaces before the label."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(label_padding=3)
    steps = [
        StepDefinition("Padded"),
    ]
    stepper = Stepper(steps=steps, theme=theme, console=console, auto_refresh=False)
    console.print(stepper)
    output = console.export_text()
    # 3 spaces + "Padded"
    assert "   Padded" in output


# ---------------------------------------------------------------------------
# Progress bar tests
# ---------------------------------------------------------------------------


def test_set_step_progress_updates_bar() -> None:
    theme = StepperTheme(show_bar=True)
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Active Step", status=StepStatus.ACTIVE)
    stepper.set_step_progress(0, 0.5)
    console.print(stepper)
    output = console.export_text()
    assert "━" in output
    task_id = stepper._step_task_ids[0]
    task = stepper._tasks[task_id]
    assert task.completed == 50


def test_set_step_progress_clamp_above_one() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(show_bar=True)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Test")
    stepper.set_step_progress(0, 1.5)
    task_id = stepper._step_task_ids[0]
    task = stepper._tasks[task_id]
    assert task.completed == 100


def test_set_step_progress_clamp_below_zero() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(show_bar=True)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Test")
    stepper.set_step_progress(0, -0.5)
    task_id = stepper._step_task_ids[0]
    task = stepper._tasks[task_id]
    assert task.completed == 0


def test_set_step_progress_clamp_exact_boundaries() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(show_bar=True)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Low")
    stepper.add_step("High")
    stepper.set_step_progress(0, 0.0)
    stepper.set_step_progress(1, 1.0)
    low_task = stepper._tasks[stepper._step_task_ids[0]]
    high_task = stepper._tasks[stepper._step_task_ids[1]]
    assert low_task.completed == 0
    assert high_task.completed == 100


def test_set_step_progress_out_of_range() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    stepper.add_step("Only")
    with pytest.raises(IndexError):
        stepper.set_step_progress(99, 0.5)


def test_finished_bar_style() -> None:
    """When progress reaches 100%, task.finished becomes True (uses finished_style)."""
    theme = StepperTheme(show_bar=True)
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Done Step", status=StepStatus.ACTIVE)
    stepper.set_step_progress(0, 1.0)
    task_id = stepper._step_task_ids[0]
    task = stepper._tasks[task_id]
    assert task.finished is True
    assert task.completed == 100


# ---------------------------------------------------------------------------
# Integration: all features combined
# ---------------------------------------------------------------------------


def test_stepper_with_all_features() -> None:
    """Stepper with show_bar, show_elapsed_time, and logging enabled."""
    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(
        show_bar=True,
        show_elapsed_time=True,
        max_log_rows=3,
        log_prefix="→",
    )
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("Build", status=StepStatus.COMPLETED)
    stepper.add_step("Test", status=StepStatus.ACTIVE)
    stepper.add_step("Deploy", status=StepStatus.PENDING)
    stepper.set_step_progress(1, 0.7)
    stepper.log(0, "build succeeded")
    stepper.log(1, "running tests...")
    console.print(stepper)
    output = console.export_text()
    assert "Build" in output
    assert "Test" in output
    assert "Deploy" in output
    assert "━" in output
    assert "build succeeded" in output
    assert "running tests..." in output
    # Completed step shows time, pending shows dash
    assert "-:--:--" in output


def test_rich_console_renders_stepper() -> None:
    """Console().print(stepper) must work without entering the context manager."""
    stepper = Stepper(console=Console(record=True, width=80, legacy_windows=False), auto_refresh=False)
    stepper.add_step("Alpha", status=StepStatus.COMPLETED)
    outer = Console(record=True, width=80, legacy_windows=False)
    outer.print(stepper)
    assert "Alpha" in outer.export_text()


# ---------------------------------------------------------------------------
# Task 5: Parallel Group API
# ---------------------------------------------------------------------------


def test_add_parallel_group_returns_index() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    idx = stepper.add_parallel_group("Tests")
    assert isinstance(idx, int)


def test_add_parallel_step_returns_child_index() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    group_idx = stepper.add_parallel_group("Tests")
    child_idx = stepper.add_parallel_step(group_idx, "Unit Tests")
    assert isinstance(child_idx, int)
    assert child_idx != group_idx


def test_add_parallel_step_wrong_target_raises() -> None:
    """add_parallel_step raises TypeError when target is not a parallel group."""
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    step_idx = stepper.add_step("Regular")
    with pytest.raises(TypeError):
        stepper.add_parallel_step(step_idx, "Child")


def test_parallel_group_renders_children() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    g = stepper.add_parallel_group("Test Suite")
    stepper.add_parallel_step(g, "Unit Tests", status=StepStatus.COMPLETED)
    stepper.add_parallel_step(g, "E2E Tests", status=StepStatus.FAILED)
    console.print(stepper)
    output = console.export_text()
    assert "Test Suite" in output
    assert "Unit Tests" in output
    assert "E2E Tests" in output
    assert "├─" in output
    assert "└─" in output


def test_parallel_group_renders_parallel_badge() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    g = stepper.add_parallel_group("Run Tests")
    stepper.add_parallel_step(g, "A")
    console.print(stepper)
    output = console.export_text()
    assert "parallel" in output


def test_set_step_status_on_parallel_child() -> None:
    """set_step_status works on a parallel child via its global index."""
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    g = stepper.add_parallel_group("Tests")
    child_idx = stepper.add_parallel_step(g, "Unit", status=StepStatus.PENDING)
    stepper.set_step_status(child_idx, StepStatus.COMPLETED)
    node = stepper._node_index[child_idx]
    assert node.status is StepStatus.COMPLETED


# ---------------------------------------------------------------------------
# Task 6: Sub-step API
# ---------------------------------------------------------------------------


def test_add_sub_step_returns_child_index() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    parent_idx = stepper.add_step("Process")
    sub_idx = stepper.add_sub_step(parent_idx, "Validate")
    assert isinstance(sub_idx, int)
    assert sub_idx != parent_idx


def test_add_sub_step_on_parallel_group_raises() -> None:
    """add_sub_step raises TypeError when target is a parallel group."""
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    g = stepper.add_parallel_group("Tests")
    with pytest.raises(TypeError):
        stepper.add_sub_step(g, "Sub")


def test_add_sub_step_on_step_with_parallel_children_raises() -> None:
    """Multiple sub-steps under a regular step are fine (not parallel children)."""
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    parent_idx = stepper.add_step("Deploy")
    stepper.add_sub_step(parent_idx, "Stage")
    stepper.add_sub_step(parent_idx, "Prod")   # also OK


def test_sub_step_renders_in_output() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    parent_idx = stepper.add_step("Process Data")
    stepper.add_sub_step(parent_idx, "Validate schema", status=StepStatus.COMPLETED)
    stepper.add_sub_step(parent_idx, "Write to DB", status=StepStatus.ACTIVE)
    console.print(stepper)
    output = console.export_text()
    assert "Process Data" in output
    assert "Validate schema" in output
    assert "Write to DB" in output
    assert "├─" in output
    assert "└─" in output


def test_set_step_status_on_sub_step() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    parent_idx = stepper.add_step("Build")
    sub_idx = stepper.add_sub_step(parent_idx, "Compile", status=StepStatus.PENDING)
    stepper.set_step_status(sub_idx, StepStatus.COMPLETED)
    node = stepper._node_index[sub_idx]
    assert node.status is StepStatus.COMPLETED


def test_log_on_sub_step() -> None:
    console = Console(record=True, width=80, legacy_windows=False)
    stepper = Stepper(console=console, auto_refresh=False)
    parent_idx = stepper.add_step("Build")
    sub_idx = stepper.add_sub_step(parent_idx, "Compile")
    stepper.log(sub_idx, "compiled 42 files")
    node = stepper._node_index[sub_idx]
    assert "compiled 42 files" in node.logs
