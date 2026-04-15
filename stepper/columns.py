from __future__ import annotations

from datetime import timedelta

from rich.console import Group, RenderableType
from rich.progress import ProgressColumn, Task
from rich.spinner import Spinner
from rich.text import Text

from stepper.node import StepNode
from stepper.theme import StepperTheme
from stepper.types import LogPosition, StepStatus


class StatusMapper:
    """Single source of truth for status -> (symbol, style) mapping."""

    def __init__(self, theme: StepperTheme) -> None:
        self._theme = theme

    def symbol_and_style(self, status: StepStatus) -> tuple[str, str]:
        if status is StepStatus.COMPLETED:
            return self._theme.completed_symbol, self._theme.completed_style
        if status is StepStatus.ACTIVE:
            return self._theme.active_symbol, self._theme.active_style
        if status is StepStatus.FAILED:
            return self._theme.failed_symbol, self._theme.failed_style
        if status is StepStatus.WARNING:
            return self._theme.warning_symbol, self._theme.warning_style
        if status is StepStatus.SKIPPED:
            return self._theme.skipped_symbol, self._theme.skipped_style
        return self._theme.pending_symbol, self._theme.pending_style

    def style(self, status: StepStatus) -> str:
        return self.symbol_and_style(status)[1]


class LogRenderer:
    """Single source of truth for log capping and line building."""

    def __init__(self, theme: StepperTheme) -> None:
        self._theme = theme

    def visible_count(self, total_logs: int, max_visible: int | None) -> int:
        max_rows = self._theme.max_log_rows
        if max_rows == 0 or total_logs == 0:
            return 0
        if max_rows is not None:
            return min(total_logs, max_rows)
        if max_visible is not None:
            return min(total_logs, max_visible)
        return total_logs

    def build_lines(
        self,
        logs: list[str],
        max_visible: int | None,
        tree_prefix: str = "",
        tree_style: str = "",
    ) -> list[Text]:
        """Build styled Text lines from log messages.

        When *tree_prefix* is set (e.g. ``"│ "`` for non-last children),
        the prefix portion is rendered with *tree_style* while the log
        text retains the theme's ``log_style``.
        """
        count = self.visible_count(len(logs), max_visible)
        if count == 0:
            return []
        visible = logs[-count:]
        padding = " " * max(0, self._theme.label_padding)
        prefix = self._theme.log_prefix + " " if self._theme.log_prefix else ""
        lines: list[Text] = []
        for msg in visible:
            text = Text()
            if tree_prefix and tree_style:
                # Tree connector gets its own style (connector_style);
                # log text keeps log_style.
                text.append(f"{padding}{tree_prefix}", style=tree_style)
                text.append(f"{prefix}{msg}", style=self._theme.log_style)
            else:
                text.append(f"{padding}{prefix}{msg}", style=self._theme.log_style)
            lines.append(text)
        return lines


class StepIndicatorColumn(ProgressColumn):
    max_refresh = 0.08

    def __init__(
        self, theme: StepperTheme, status: StatusMapper, log: LogRenderer
    ) -> None:
        super().__init__()
        self._theme = theme
        self._status = status
        self._log = log
        self._spinner = Spinner(
            self._theme.spinner_name,
            style=self._theme.active_style,
            speed=self._theme.spinner_speed,
        )

    def render(self, task: Task) -> RenderableType:
        status_val = task.fields.get("status", StepStatus.PENDING)
        is_last = task.fields.get("is_last", False)

        # Compute parent log count and whether logs render above the label.
        max_visible = task.fields.get("max_visible_logs")
        log_count = self._log.visible_count(
            len(task.fields.get("logs", [])), max_visible
        )
        logs_above = self._theme.log_position is LogPosition.ABOVE and log_count > 0

        lines: list[RenderableType] = []

        # When logs render above the label in StepLabelColumn, prepend blank
        # spacers so the indicator symbol aligns with the label row.
        if logs_above:
            for _ in range(log_count):
                lines.append(Text(""))

        if status_val is StepStatus.ACTIVE:
            lines.append(self._spinner.render(task.get_time()))
        else:
            symbol, style = self._status.symbol_and_style(status_val)
            lines.append(Text(symbol, style=style))

        if not is_last:
            connector = self._theme.connector_glyph()

            # Count rows contributed by each embedded child (label + description + logs).
            children: list[StepNode] = task.fields.get("children", [])
            child_rows = sum(
                1  # child label row
                + (1 if child.description else 0)
                + self._log.visible_count(len(child.logs), max_visible)
                for child in children
            )

            # Connector rows after the symbol:
            #   1 (parent label row) + description + child_rows
            #   + 1 (child group separator, only when children exist) + step_gap
            #   ABOVE: parent log rows already prepended as spacers, not counted here
            #   BELOW: parent log rows appear after the label, so connectors span them
            connector_rows = (
                1
                + (1 if task.fields.get("step_description") else 0)
                + child_rows
                + (1 if children else 0)
                + max(0, self._theme.step_gap)
            )
            if not logs_above:
                # BELOW: parent log rows appear after the label, so the
                # connector must span them too.
                connector_rows += log_count

            for _ in range(connector_rows):
                lines.append(Text(connector, style=self._theme.connector_style))

        return Group(*lines)


class StepLabelColumn(ProgressColumn):
    def __init__(
        self, theme: StepperTheme, status: StatusMapper, log: LogRenderer
    ) -> None:
        super().__init__()
        self._theme = theme
        self._status = status
        self._log = log

    def render(self, task: Task) -> RenderableType:
        status_val = task.fields.get("status", StepStatus.PENDING)
        is_last = task.fields.get("is_last", False)
        description = task.fields.get("step_description")
        label = task.fields.get("label", "")
        is_parallel_group = task.fields.get("is_parallel_group", False)

        label_style = self._merge_styles(
            self._status.style(status_val), self._theme.label_style
        )
        padding = " " * max(0, self._theme.label_padding)
        max_visible = task.fields.get("max_visible_logs")
        log_lines = self._log.build_lines(task.fields.get("logs", []), max_visible)

        lines: list[RenderableType] = []

        if self._theme.log_position is LogPosition.ABOVE:
            lines.extend(log_lines)

        # Parent label — append 'parallel' badge for group headers.
        if is_parallel_group:
            label_text = Text()
            label_text.append(f"{padding}{label}", style=label_style)
            label_text.append("  parallel", style="bright_black")
            lines.append(label_text)
        else:
            lines.append(Text(f"{padding}{label}", style=label_style))

        if description:
            lines.append(
                Text(
                    f"{padding}{description}", style=self._theme.step_description_style
                )
            )

        if self._theme.log_position is LogPosition.BELOW:
            lines.extend(log_lines)

        # Render embedded children (sub-steps or parallel children) with tree branches.
        children: list = task.fields.get("children", [])
        for i, child in enumerate(children):
            is_last_child = i == len(children) - 1
            branch = (
                self._theme.tree_branch_last
                if is_last_child
                else self._theme.tree_branch_mid
            )
            # Tree continuation: │ for non-last children, blank for last.
            # Width matches the branch glyph so columns align.
            branch_width = len(branch)
            tree_cont = (
                self._theme.connector_symbol + " " * max(0, branch_width - 1)
                if not is_last_child
                else " " * branch_width
            )
            child_symbol, child_style = self._status.symbol_and_style(child.status)
            lines.append(
                Text(
                    f"{padding}{branch} {child_symbol}  {child.label}",
                    style=child_style,
                )
            )
            if child.description:
                desc_text = Text()
                desc_text.append(
                    f"{padding}{tree_cont}  ", style=self._theme.connector_style
                )
                desc_text.append(
                    child.description, style=self._theme.step_description_style
                )
                lines.append(desc_text)
            # Child logs always render below the child's label row,
            # with tree continuation connector for non-last children.
            child_log_lines = self._log.build_lines(
                child.logs,
                max_visible,
                tree_prefix=tree_cont,
                tree_style=self._theme.connector_style,
            )
            lines.extend(child_log_lines)

        if not is_last:
            # Add a trailing blank separator between steps. When children are
            # present, an extra blank is added so the indicator connector height
            # matches the label column row count (children each add a connector
            # row and the group needs one additional separator blank).
            connector_lines = 1 + (1 if children else 0) + max(0, self._theme.step_gap)
            for _ in range(connector_lines):
                lines.append(Text(""))

        return Group(*lines)

    @staticmethod
    def _merge_styles(*styles: str) -> str:
        return " ".join(style for style in styles if style)


class StepperTimeColumn(ProgressColumn):
    def __init__(self, theme: StepperTheme) -> None:
        super().__init__()
        self._theme = theme

    def render(self, task: Task) -> Text:
        status = task.fields.get("status", StepStatus.PENDING)
        if status is StepStatus.PENDING:
            return Text("-:--:--", style=self._theme.time_style)
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text("-:--:--", style=self._theme.time_style)
        delta = timedelta(seconds=max(0, int(elapsed)))
        return Text(str(delta), style=self._theme.time_style)
