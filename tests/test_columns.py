"""Tests for column renderers: StepIndicatorColumn, StepLabelColumn, StepperTimeColumn."""

from __future__ import annotations

import time as time_mod
from unittest.mock import MagicMock

import pytest
from rich.console import Console, Group
from rich.progress import TaskID
from rich.text import Text

from stepper import (
    LogPosition,
    StepStatus,
    Stepper,
    StepperTheme,
)
from stepper.columns import (
    LogRenderer,
    StatusMapper,
    StepIndicatorColumn,
    StepLabelColumn,
    StepperTimeColumn,
)


def _make_task(
    status: StepStatus = StepStatus.PENDING,
    *,
    is_last: bool = False,
    logs: list[str] | None = None,
    label: str = "Test Step",
    step_description: str | None = None,
    get_time: float | None = None,
) -> MagicMock:
    """Create a mock Task object for column testing."""
    task = MagicMock()
    task.fields = {
        "status": status,
        "is_last": is_last,
        "logs": logs or [],
        "label": label,
        "step_description": step_description,
    }
    task.id = TaskID(1)
    task.description = label
    task.finished = False
    task.finished_time = None
    task.elapsed = None
    task.get_time.return_value = (
        get_time if get_time is not None else time_mod.monotonic()
    )
    return task


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


# ---------------------------------------------------------------------------
# Spinner support tests
# ---------------------------------------------------------------------------


class TestSpinnerSupport:
    def test_theme_has_spinner_defaults(self) -> None:
        theme = StepperTheme()
        assert theme.spinner_name == "dots"
        assert theme.spinner_speed == 1.0

    def test_theme_accepts_custom_spinner(self) -> None:
        theme = StepperTheme(spinner_name="line", spinner_speed=2.0)
        assert theme.spinner_name == "line"
        assert theme.spinner_speed == 2.0

    def test_indicator_column_has_max_refresh(self) -> None:
        theme = StepperTheme()
        col = StepIndicatorColumn(theme, StatusMapper(theme), LogRenderer(theme))
        assert col.max_refresh == 0.08

    def test_active_step_renders_spinner(self) -> None:
        from rich.spinner import Spinner

        theme = StepperTheme(spinner_name="dots")
        col = StepIndicatorColumn(theme, StatusMapper(theme), LogRenderer(theme))
        task = _make_task(status=StepStatus.ACTIVE)
        result = col.render(task)
        assert isinstance(result, Group)
        first_line = result.renderables[0]
        assert isinstance(first_line, Text)
        assert first_line.plain != "◉"

    def test_completed_step_renders_static_symbol(self) -> None:
        theme = StepperTheme(completed_symbol="✓")
        col = StepIndicatorColumn(theme, StatusMapper(theme), LogRenderer(theme))
        task = _make_task(status=StepStatus.COMPLETED)
        result = col.render(task)
        first_line = result.renderables[0]
        assert isinstance(first_line, Text)
        assert first_line.plain == "✓"

    def test_pending_step_renders_static_symbol(self) -> None:
        theme = StepperTheme(pending_symbol="○")
        col = StepIndicatorColumn(theme, StatusMapper(theme), LogRenderer(theme))
        task = _make_task(status=StepStatus.PENDING)
        result = col.render(task)
        first_line = result.renderables[0]
        assert isinstance(first_line, Text)
        assert first_line.plain == "○"

    def test_spinner_uses_theme_speed(self) -> None:
        theme = StepperTheme(spinner_name="dots", spinner_speed=3.0)
        col = StepIndicatorColumn(theme, StatusMapper(theme), LogRenderer(theme))
        assert col._spinner.speed == 3.0

    def test_spinner_uses_theme_style(self) -> None:
        theme = StepperTheme(active_style="magenta bold")
        col = StepIndicatorColumn(theme, StatusMapper(theme), LogRenderer(theme))
        assert str(col._spinner.style) == "magenta bold"


def test_status_mapper_failed_warning_skipped() -> None:
    theme = StepperTheme(
        failed_symbol="✕",
        failed_style="red bold",
        warning_symbol="⚠",
        warning_style="yellow bold",
        skipped_symbol="⊘",
        skipped_style="bright_black",
    )
    mapper = StatusMapper(theme)
    assert mapper.symbol_and_style(StepStatus.FAILED) == ("✕", "red bold")
    assert mapper.symbol_and_style(StepStatus.WARNING) == ("⚠", "yellow bold")
    assert mapper.symbol_and_style(StepStatus.SKIPPED) == ("⊘", "bright_black")


# ---------------------------------------------------------------------------
# LOG_POSITION.ABOVE alignment tests
# ---------------------------------------------------------------------------


def test_indicator_above_prepends_blank_spacers() -> None:
    """When log_position=ABOVE with n logs, indicator column must prepend n blank
    spacers before the symbol so the symbol row aligns with the label row in
    StepLabelColumn, which renders logs first."""
    theme = StepperTheme(log_position=LogPosition.ABOVE, max_log_rows=2)
    col = StepIndicatorColumn(theme, StatusMapper(theme), LogRenderer(theme))
    task = _make_task(status=StepStatus.PENDING, is_last=False, logs=["a", "b"])
    result = col.render(task)
    assert isinstance(result, Group)
    renderables = result.renderables
    # 2 blank spacers + symbol + 1 connector (label row only) = 4
    assert len(renderables) == 4
    # Rows 0-1: blank spacers (one per log line above the label)
    assert isinstance(renderables[0], Text) and renderables[0].plain == ""
    assert isinstance(renderables[1], Text) and renderables[1].plain == ""
    # Row 2: pending symbol
    assert isinstance(renderables[2], Text) and renderables[2].plain == "○"
    # Row 3: connector spans only the label row, not the log rows
    assert isinstance(renderables[3], Text) and "│" in renderables[3].plain


def test_indicator_above_connector_count_excludes_log_rows() -> None:
    """With log_position=ABOVE and 2 logs, only 1 connector renders below the symbol
    (for the label row), not 3 (which would wrongly include the 2 log rows)."""
    from rich.console import Console

    from stepper import StepDefinition

    console = Console(record=True, width=80, legacy_windows=False)
    theme = StepperTheme(log_position=LogPosition.ABOVE, max_log_rows=2)
    stepper = Stepper(console=console, auto_refresh=False, theme=theme)
    stepper.add_step("First")
    stepper.add_step("Second")
    stepper.log(0, "line one")
    stepper.log(0, "line two")
    console.print(stepper)
    output = console.export_text()
    # ABOVE + 2 logs → 1 connector (label row only); BELOW would give 3
    connector_count = output.count("│")
    assert connector_count == 1


def test_indicator_column_counts_child_rows_in_connector() -> None:
    """Indicator column emits one extra connector row per child step."""
    from stepper.node import StepNode

    theme = StepperTheme()
    col = StepIndicatorColumn(theme, StatusMapper(theme), LogRenderer(theme))
    child1 = StepNode(0, "C1", StepStatus.COMPLETED, None, [], [], False, 1, None)
    child2 = StepNode(1, "C2", StepStatus.PENDING, None, [], [], False, 1, None)
    task = _make_task(status=StepStatus.PENDING, is_last=False)
    task.fields["children"] = [child1, child2]
    result = col.render(task)
    renderables = result.renderables
    # symbol + (1 label + 2 children + 1 blank) = symbol + 4 connectors
    assert len(renderables) == 5


def test_label_column_renders_tree_branches_for_children() -> None:
    """Label column renders ├─ for intermediate children and └─ for the last."""
    from stepper.node import StepNode

    theme = StepperTheme()
    col = StepLabelColumn(theme, StatusMapper(theme), LogRenderer(theme))
    child1 = StepNode(
        10, "Unit Tests", StepStatus.COMPLETED, None, [], [], False, 0, None
    )
    child2 = StepNode(11, "E2E Tests", StepStatus.FAILED, None, [], [], False, 0, None)
    task = _make_task(label="Test Suite", is_last=False)
    task.fields["children"] = [child1, child2]
    task.fields["is_parallel_group"] = True
    result = col.render(task)
    rendered_text = "".join(r.plain for r in result.renderables if hasattr(r, "plain"))
    assert "├─" in rendered_text
    assert "└─" in rendered_text
    assert "Unit Tests" in rendered_text
    assert "E2E Tests" in rendered_text


def test_label_column_renders_parallel_badge() -> None:
    """Parallel group header label includes a 'parallel' badge."""
    from stepper.node import StepNode

    theme = StepperTheme()
    col = StepLabelColumn(theme, StatusMapper(theme), LogRenderer(theme))
    task = _make_task(label="Run Tests", is_last=True)
    task.fields["children"] = []
    task.fields["is_parallel_group"] = True
    result = col.render(task)
    rendered_text = "".join(r.plain for r in result.renderables if hasattr(r, "plain"))
    assert "parallel" in rendered_text


# ---------------------------------------------------------------------------
# Tree continuation connector tests
# ---------------------------------------------------------------------------


def test_non_last_child_description_has_tree_connector() -> None:
    """Non-last child description lines must include │ tree continuation."""
    from stepper.node import StepNode

    theme = StepperTheme()
    col = StepLabelColumn(theme, StatusMapper(theme), LogRenderer(theme))
    child1 = StepNode(
        1, "Compile", StepStatus.COMPLETED, "42 files", [], [], False, 0, None
    )
    child2 = StepNode(2, "Test", StepStatus.PENDING, None, [], [], False, 0, None)
    task = _make_task(label="Build", is_last=False)
    task.fields["children"] = [child1, child2]
    result = col.render(task)
    renderables = result.renderables
    # Row 0: parent label, Row 1: child1 label (├─), Row 2: child1 description
    desc_row = renderables[2]
    assert "│" in desc_row.plain
    assert "42 files" in desc_row.plain


def test_last_child_description_has_no_tree_connector() -> None:
    """Last child description lines must have blank instead of │."""
    from stepper.node import StepNode

    theme = StepperTheme()
    col = StepLabelColumn(theme, StatusMapper(theme), LogRenderer(theme))
    child1 = StepNode(1, "Compile", StepStatus.COMPLETED, None, [], [], False, 0, None)
    child2 = StepNode(2, "Test", StepStatus.PENDING, "running", [], [], False, 0, None)
    task = _make_task(label="Build", is_last=False)
    task.fields["children"] = [child1, child2]
    result = col.render(task)
    renderables = result.renderables
    # Find the description row for child2 (last child)
    rendered_text = "".join(r.plain for r in renderables if hasattr(r, "plain"))
    # Last child's description should NOT have │ continuation
    lines = rendered_text.split("\n")
    desc_line = [l for l in lines if "running" in l][0]
    # The line before "running" should not start with │ for the last child
    assert "└─" in rendered_text


def test_non_last_child_logs_have_tree_connector() -> None:
    """Non-last child log lines must include │ tree continuation."""
    from stepper.node import StepNode

    theme = StepperTheme(max_log_rows=3)
    col = StepLabelColumn(theme, StatusMapper(theme), LogRenderer(theme))
    child1 = StepNode(
        1,
        "Compile",
        StepStatus.COMPLETED,
        None,
        ["file 1", "file 2"],
        [],
        False,
        0,
        None,
    )
    child2 = StepNode(2, "Test", StepStatus.PENDING, None, [], [], False, 0, None)
    task = _make_task(label="Build", is_last=False)
    task.fields["children"] = [child1, child2]
    result = col.render(task)
    rendered_text = "".join(r.plain for r in result.renderables if hasattr(r, "plain"))
    # Log lines for non-last child should contain │
    assert "file 1" in rendered_text
    log_lines = [l for l in rendered_text.split("\n") if "file" in l]
    for line in log_lines:
        assert "│" in line, f"Expected │ in log line: {line!r}"


def test_last_child_logs_have_no_tree_connector() -> None:
    """Last child log lines must have blank instead of │."""
    from stepper.node import StepNode

    theme = StepperTheme(max_log_rows=3)
    col = StepLabelColumn(theme, StatusMapper(theme), LogRenderer(theme))
    child1 = StepNode(1, "Compile", StepStatus.COMPLETED, None, [], [], False, 0, None)
    child2 = StepNode(
        2, "Test", StepStatus.PENDING, None, ["passed", "failed"], [], False, 0, None
    )
    task = _make_task(label="Build", is_last=False)
    task.fields["children"] = [child1, child2]
    result = col.render(task)
    rendered_text = "".join(r.plain for r in result.renderables if hasattr(r, "plain"))
    lines = rendered_text.split("\n")
    # Find log lines for child2 (last child) — after └─ line
    last_child_idx = next(i for i, l in enumerate(lines) if "└─" in l)
    log_lines_after_last = lines[last_child_idx + 1 :]
    for line in log_lines_after_last:
        if "passed" in line or "failed" in line:
            # Last child's logs should NOT have │ — they should have spaces
            stripped = line.lstrip()
            # The line should start with spaces (tree continuation blank), not │
            leading = line[: len(stripped)]
            assert "│" not in leading, f"Last child log should not have │: {line!r}"


def test_tree_continuation_width_matches_branch() -> None:
    """Tree continuation width must match tree_branch_mid/tree_branch_last width."""
    from stepper.node import StepNode

    # Custom wider branches
    theme = StepperTheme(tree_branch_mid="├──", tree_branch_last="└──")
    col = StepLabelColumn(theme, StatusMapper(theme), LogRenderer(theme))
    child1 = StepNode(
        1, "A", StepStatus.COMPLETED, "desc", ["log1"], [], False, 0, None
    )
    child2 = StepNode(2, "B", StepStatus.PENDING, None, [], [], False, 0, None)
    task = _make_task(label="Parent", is_last=False)
    task.fields["children"] = [child1, child2]
    ic = StepIndicatorColumn(theme, StatusMapper(theme), LogRenderer(theme))
    ic_rows = len(ic.render(task).renderables)
    lc_rows = len(col.render(task).renderables)
    assert ic_rows == lc_rows, f"Indicator={ic_rows}, Label={lc_rows}"
