from __future__ import annotations

from datetime import timedelta

from rich.console import Console, ConsoleOptions, Group, RenderableType, RenderResult
from rich.progress import ProgressColumn, Task
from rich.text import Text

from stepper.theme import StepperTheme
from stepper.types import StepStatus


class StepIndicatorColumn(ProgressColumn):
    def __init__(self, theme: StepperTheme) -> None:
        super().__init__()
        self._theme = theme

    def render(self, task: Task) -> RenderableType:
        status = task.fields.get("status", StepStatus.PENDING)
        is_last = task.fields.get("is_last", False)
        symbol, style = self._symbol_for(status)
        lines: list[RenderableType] = [Text(symbol, style=style)]

        if not is_last:
            connector = self._theme.connector_glyph()
            total_rows = 1 + max(0, self._theme.step_gap) + self._log_row_count(task)
            for _ in range(total_rows):
                lines.append(Text(connector, style=self._theme.connector_style))

        return Group(*lines)

    def _log_row_count(self, task: Task) -> int:
        logs = task.fields.get("logs", [])
        max_rows = self._theme.max_log_rows
        if max_rows == 0 or not logs:
            return 0
        return min(len(logs), max_rows) if max_rows is not None else len(logs)

    def _symbol_for(self, status: StepStatus) -> tuple[str, str]:
        if status is StepStatus.COMPLETED:
            return self._theme.completed_symbol, self._theme.completed_style
        if status is StepStatus.ACTIVE:
            return self._theme.active_symbol, self._theme.active_style
        return self._theme.pending_symbol, self._theme.pending_style


class StepLabelColumn(ProgressColumn):
    def __init__(self, theme: StepperTheme) -> None:
        super().__init__()
        self._theme = theme

    def render(self, task: Task) -> RenderableType:
        status = task.fields.get("status", StepStatus.PENDING)
        is_last = task.fields.get("is_last", False)
        description = task.fields.get("step_description")
        label = task.fields.get("label", "")

        label_style = self._merge_styles(
            self._status_style(status), self._theme.label_style
        )
        padding = " " * max(0, self._theme.label_padding)
        log_lines = self._build_log_lines(task)

        lines: list[RenderableType] = []

        if self._theme.log_position == "above":
            lines.extend(log_lines)

        lines.append(Text(f"{padding}{label}", style=label_style))

        if description:
            lines.append(
                Text(
                    f"{padding}{description}", style=self._theme.step_description_style
                )
            )

        if self._theme.log_position == "below":
            lines.extend(log_lines)

        if not is_last:
            connector_lines = 1 + max(0, self._theme.step_gap)
            for _ in range(connector_lines):
                lines.append(Text(""))

        return Group(*lines)

    def _build_log_lines(self, task: Task) -> list[Text]:
        logs = task.fields.get("logs", [])
        max_rows = self._theme.max_log_rows
        if max_rows == 0 or not logs:
            return []
        if max_rows is not None and len(logs) > max_rows:
            logs = logs[-max_rows:]
        elif max_rows is None:
            remaining = getattr(task, "_max_visible_logs", None)
            if remaining is not None and len(logs) > remaining:
                logs = logs[-remaining:]
        padding = " " * max(0, self._theme.label_padding)
        prefix = self._theme.log_prefix + " " if self._theme.log_prefix else ""
        return [
            Text(f"{padding}{prefix}{msg}", style=self._theme.log_style) for msg in logs
        ]

    def _status_style(self, status: StepStatus) -> str:
        if status is StepStatus.COMPLETED:
            return self._theme.completed_style
        if status is StepStatus.ACTIVE:
            return self._theme.active_style
        return self._theme.pending_style

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


class HeightAwareLogRenderable:
    """Custom renderable that accesses terminal height for log capping."""

    def __init__(self, logs: list[str], theme: StepperTheme) -> None:
        self._logs = logs
        self._theme = theme

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        logs = self._logs
        max_rows = self._theme.max_log_rows

        if max_rows == 0 or not logs:
            return

        if max_rows is None:
            # Terminal-aware: cap at terminal height minus margin
            available = max(1, options.size.height - 4)
            if len(logs) > available:
                logs = logs[-available:]
                yield Text(
                    f"... ({len(self._logs) - available} truncated)",
                    style=self._theme.log_style,
                )
        elif len(logs) > max_rows:
            logs = logs[-max_rows:]

        for log_msg in logs:
            prefix = self._theme.log_prefix + " " if self._theme.log_prefix else ""
            yield Text(f"{prefix}{log_msg}", style=self._theme.log_style)


class StepLogColumn(ProgressColumn):
    def __init__(self, theme: StepperTheme) -> None:
        super().__init__()
        self._theme = theme

    def render(self, task: Task) -> RenderableType:
        logs = task.fields.get("logs", [])
        return HeightAwareLogRenderable(logs, self._theme)
