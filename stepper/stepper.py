from __future__ import annotations

from collections.abc import Callable

from rich.console import Console
from rich.progress import Progress, ProgressColumn, TaskID

from stepper.columns import (
    LogRenderer,
    StatusMapper,
    StepIndicatorColumn,
    StepLabelColumn,
    StepperTimeColumn,
)
from stepper.theme import StepperTheme
from stepper.types import StepDefinition, StepStatus


class Stepper(Progress):
    def __init__(
        self,
        steps: list[StepDefinition] | None = None,
        theme: StepperTheme | None = None,
        console: Console | None = None,
        auto_refresh: bool = True,
        refresh_per_second: float = 10,
        speed_estimate_period: float = 30,
        transient: bool = False,
        redirect_stdout: bool = True,
        redirect_stderr: bool = True,
        get_time: Callable[[], float] | None = None,
        disable: bool = False,
        expand: bool = False,
        **kwargs: object,
    ) -> None:
        self.theme = theme or StepperTheme()
        self._step_task_ids: list[TaskID] = []
        self._status = StatusMapper(self.theme)
        self._log = LogRenderer(self.theme)
        super().__init__(
            *self._build_columns(),
            console=console,
            auto_refresh=auto_refresh,
            refresh_per_second=refresh_per_second,
            speed_estimate_period=speed_estimate_period,
            transient=transient,
            redirect_stdout=redirect_stdout,
            redirect_stderr=redirect_stderr,
            get_time=get_time,
            disable=disable,
            expand=expand,
            **kwargs,
        )
        self.log = self.__class__.log.__get__(self)  # type: ignore[method-assign]
        if steps:
            self.add_steps(steps)

    def _build_columns(self) -> list[ProgressColumn]:
        columns: list[ProgressColumn] = [
            StepIndicatorColumn(self.theme, self._status, self._log),
            StepLabelColumn(self.theme, self._status, self._log),
        ]
        if self.theme.show_bar:
            from rich.progress import BarColumn

            columns.append(
                BarColumn(
                    bar_width=self.theme.bar_width,
                    complete_style=self.theme.bar_complete_style,
                    finished_style=self.theme.bar_finished_style,
                    pulse_style=self.theme.bar_pulse_style,
                )
            )
        if self.theme.show_elapsed_time:
            columns.append(StepperTimeColumn(self.theme))
        return columns

    def add_step(
        self,
        label: str,
        status: StepStatus = StepStatus.PENDING,
        step_description: str | None = None,
    ) -> TaskID:
        index = len(self._step_task_ids)
        total = 100
        completed = 100 if status is StepStatus.COMPLETED else 0
        task_id = self.add_task(label, total=total, completed=completed)
        if self.theme.max_log_rows is None:
            height = self.console.height if self.console else 24
            max_visible = max(1, height - 4)
            self.update(task_id, max_visible_logs=max_visible)
        self._step_task_ids.append(task_id)
        self.update(
            task_id,
            status=status,
            label=label,
            step_description=step_description,
            index=index,
            logs=[],
        )
        self._sync_task_fields()
        return task_id

    def add_steps(self, steps: list[StepDefinition]) -> None:
        for step in steps:
            self.add_step(
                step.label, status=step.status, step_description=step.step_description
            )

    def set_step_status(self, index: int, status: StepStatus) -> None:
        task_id = self._step_task_ids[index]
        if status is StepStatus.COMPLETED:
            task = self._tasks[task_id]
            self.update(task_id, status=status, completed=task.total)
        else:
            self.update(task_id, status=status)

    def set_step_progress(self, step_index: int, percent: float) -> None:
        """Set the progress bar for a step.

        Args:
            step_index: Zero-based index of the step.
            percent: Progress value clamped to [0.0, 1.0].

        Raises:
            IndexError: If step_index is out of range.
        """
        percent = max(0.0, min(1.0, percent))
        task_id = self._step_task_ids[step_index]
        self.update(task_id, completed=int(percent * 100))

    def log(self, step_index: int, message: str) -> None:
        """Append a log message to a step.

        Raises:
            IndexError: If step_index is out of range.
        """
        if not message:
            return
        task_id = self._step_task_ids[step_index]
        task = self._tasks[task_id]
        logs = list(task.fields.get("logs", []))
        logs.append(message)
        self.update(task_id, logs=logs)

    def _sync_task_fields(self) -> None:
        total_steps = len(self._step_task_ids)
        for index, task_id in enumerate(self._step_task_ids):
            self.update(
                task_id, total_steps=total_steps, is_last=index == total_steps - 1
            )
