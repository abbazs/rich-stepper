from __future__ import annotations

from datetime import timedelta

from rich.console import Group, RenderableType
from rich.progress import ProgressColumn, Task
from rich.text import Text

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

    def build_lines(self, logs: list[str], max_visible: int | None) -> list[Text]:
        count = self.visible_count(len(logs), max_visible)
        if count == 0:
            return []
        visible = logs[-count:]
        padding = " " * max(0, self._theme.label_padding)
        prefix = self._theme.log_prefix + " " if self._theme.log_prefix else ""
        return [
            Text(f"{padding}{prefix}{msg}", style=self._theme.log_style)
            for msg in visible
        ]


class StepIndicatorColumn(ProgressColumn):
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
        symbol, style = self._status.symbol_and_style(status_val)
        lines: list[RenderableType] = [Text(symbol, style=style)]

        if not is_last:
            connector = self._theme.connector_glyph()
            max_visible = task.fields.get("max_visible_logs")
            log_count = self._log.visible_count(
                len(task.fields.get("logs", [])), max_visible
            )
            total_rows = 1 + max(0, self._theme.step_gap) + log_count
            for _ in range(total_rows):
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

        label_style = self._merge_styles(
            self._status.style(status_val), self._theme.label_style
        )
        padding = " " * max(0, self._theme.label_padding)
        max_visible = task.fields.get("max_visible_logs")
        log_lines = self._log.build_lines(task.fields.get("logs", []), max_visible)

        lines: list[RenderableType] = []

        if self._theme.log_position is LogPosition.ABOVE:
            lines.extend(log_lines)

        lines.append(Text(f"{padding}{label}", style=label_style))

        if description:
            lines.append(
                Text(
                    f"{padding}{description}", style=self._theme.step_description_style
                )
            )

        if self._theme.log_position is LogPosition.BELOW:
            lines.extend(log_lines)

        if not is_last:
            connector_lines = 1 + max(0, self._theme.step_gap)
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
