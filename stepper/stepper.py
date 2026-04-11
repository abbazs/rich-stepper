from __future__ import annotations

import types
from collections.abc import Callable

from rich.console import Console
from rich.progress import Progress, ProgressColumn, Task, TaskID

from stepper.columns import (
    LogRenderer,
    StatusMapper,
    StepIndicatorColumn,
    StepLabelColumn,
    StepperTimeColumn,
)
from stepper.node import StepNode
from stepper.theme import StepperTheme
from stepper.types import StepDefinition, StepStatus


class Stepper:
    """Multi-step terminal progress widget built on Rich.

    Wraps ``rich.progress.Progress`` internally — no Rich types appear in the
    public API. Each top-level step maps to one Rich task; children (sub-steps
    and parallel children) are embedded in the parent task's fields and rendered
    inline by the label column.
    """

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
        self._status_mapper = StatusMapper(self.theme)
        self._log_renderer = LogRenderer(self.theme)
        # Top-level nodes only (parallel group headers count as top-level)
        self._nodes: list[StepNode] = []
        # All nodes by globally unique idx (includes children)
        self._node_index: dict[int, StepNode] = {}
        self._next_idx: int = 0
        self._progress = Progress(
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
        if steps:
            self.add_steps(steps)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_columns(self) -> list[ProgressColumn]:
        """Construct the column list passed to Progress."""
        columns: list[ProgressColumn] = [
            StepIndicatorColumn(self.theme, self._status_mapper, self._log_renderer),
            StepLabelColumn(self.theme, self._status_mapper, self._log_renderer),
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

    def _alloc_node(
        self,
        label: str,
        status: StepStatus,
        description: str | None,
        is_parallel: bool = False,
        parent_idx: int | None = None,
    ) -> tuple[int, StepNode]:
        """Allocate a StepNode with a globally unique index."""
        idx = self._next_idx
        self._next_idx += 1
        node = StepNode(
            idx=idx,
            label=label,
            status=status,
            description=description,
            logs=[],
            children=[],
            is_parallel=is_parallel,
            parent_idx=parent_idx,
            task_id=None,
        )
        self._node_index[idx] = node
        return idx, node

    def _register_top_level(self, node: StepNode) -> None:
        """Append a top-level node, create its Rich task, and sync is_last."""
        self._nodes.append(node)
        total = 100
        completed = 100 if node.status is StepStatus.COMPLETED else 0
        task_id = self._progress.add_task(node.label, total=total, completed=completed)
        node.task_id = task_id
        self._push_fields(node)
        self._sync_is_last()

    def _push_fields(self, node: StepNode) -> None:
        """Write all node state into the corresponding Rich task's fields."""
        assert node.task_id is not None
        max_visible: int | None = self.theme.max_log_rows
        if max_visible is None:
            console = self._progress.console
            height = console.height if console else 24
            max_visible = max(1, height - 4)
        self._progress.update(
            node.task_id,
            status=node.status,
            label=node.label,
            step_description=node.description,
            logs=node.logs,
            children=node.children,
            is_parallel_group=node.is_parallel,
            max_visible_logs=max_visible,
        )

    def _sync_is_last(self) -> None:
        """Update the is_last field on all top-level tasks."""
        n = len(self._nodes)
        for i, node in enumerate(self._nodes):
            if node.task_id is not None:
                self._progress.update(node.task_id, is_last=(i == n - 1))

    def _get_node(self, index: int) -> StepNode:
        """Look up a node by global index; supports negative indexing for top-level."""
        if index < 0:
            try:
                return self._nodes[index]
            except IndexError:
                raise IndexError(f"step index {index} is out of range") from None
        try:
            return self._node_index[index]
        except KeyError:
            raise IndexError(f"step index {index} is out of range") from None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_step(
        self,
        label: str,
        status: StepStatus = StepStatus.PENDING,
        step_description: str | None = None,
    ) -> int:
        """Add a top-level step and return its global index."""
        idx, node = self._alloc_node(label, status, step_description)
        self._register_top_level(node)
        return idx

    def add_steps(self, steps: list[StepDefinition]) -> None:
        """Add multiple steps from a StepDefinition list.

        Handles ``parallel=True`` (creates a parallel group header) and
        ``sub_steps`` (adds sequential children under the step).
        """
        for step in steps:
            if step.parallel:
                group_idx = self.add_parallel_group(
                    step.label, step_description=step.step_description
                )
                for sub in step.sub_steps or []:
                    self.add_parallel_step(
                        group_idx, sub.label,
                        status=sub.status,
                        step_description=sub.step_description,
                    )
            else:
                parent_idx = self.add_step(
                    step.label, status=step.status,
                    step_description=step.step_description,
                )
                for sub in step.sub_steps or []:
                    self.add_sub_step(
                        parent_idx, sub.label,
                        status=sub.status,
                        step_description=sub.step_description,
                    )

    def add_parallel_group(
        self,
        label: str,
        step_description: str | None = None,
    ) -> int:
        """Add a parallel group header and return its global index.

        Children added via :meth:`add_parallel_step` run concurrently; the
        group header's status auto-derives from its children.
        """
        idx, node = self._alloc_node(
            label,
            StepStatus.PENDING,
            step_description,
            is_parallel=True,
        )
        self._register_top_level(node)
        return idx

    def add_parallel_step(
        self,
        group_index: int,
        label: str,
        status: StepStatus = StepStatus.PENDING,
        step_description: str | None = None,
    ) -> int:
        """Add a child step to a parallel group and return its global index.

        Raises:
            TypeError: If ``group_index`` does not refer to a parallel group.
            IndexError: If ``group_index`` is out of range.
        """
        parent = self._get_node(group_index)
        if not parent.is_parallel:
            raise TypeError(
                f"index {group_index} is not a parallel group; "
                "use add_parallel_group first"
            )
        child_idx, child_node = self._alloc_node(
            label,
            status,
            step_description,
            parent_idx=group_index,
        )
        # Children are embedded in the parent's children list — no Rich task.
        parent.children.append(child_node)
        assert parent.task_id is not None
        self._progress.update(parent.task_id, children=parent.children, refresh=True)
        return child_idx

    def add_sub_step(
        self,
        parent_index: int,
        label: str,
        status: StepStatus = StepStatus.PENDING,
        step_description: str | None = None,
    ) -> int:
        """Add a sequential sub-step under a regular step and return its global index.

        Raises:
            TypeError: If ``parent_index`` refers to a parallel group.
            IndexError: If ``parent_index`` is out of range.
        """
        parent = self._get_node(parent_index)
        if parent.is_parallel:
            raise TypeError(
                f"index {parent_index} is a parallel group; "
                "use add_parallel_step to add children to a parallel group"
            )
        child_idx, child_node = self._alloc_node(
            label,
            status,
            step_description,
            parent_idx=parent_index,
        )
        parent.children.append(child_node)
        assert parent.task_id is not None
        self._progress.update(parent.task_id, children=parent.children, refresh=True)
        return child_idx

    def set_step_status(self, index: int, status: StepStatus) -> None:
        """Update the status of any step by global index."""
        node = self._get_node(index)
        node.status = status
        if node.task_id is not None:
            # Top-level node: update Rich task directly
            if status is StepStatus.COMPLETED:
                task = self._progress._tasks[node.task_id]
                self._progress.update(node.task_id, status=status, completed=task.total)
            else:
                self._progress.update(node.task_id, status=status)
        else:
            # Child node: status already mutated on StepNode; trigger parent refresh
            assert node.parent_idx is not None
            parent = self._node_index[node.parent_idx]
            assert parent.task_id is not None
            self._progress.update(parent.task_id, refresh=True)

    def set_step_progress(self, step_index: int, percent: float) -> None:
        """Set the progress bar value for a top-level step (0.0–1.0, clamped).

        Raises:
            IndexError: If step_index is out of range.
            TypeError: If step_index refers to a child node (progress bars are
                only supported on top-level steps).
        """
        percent = max(0.0, min(1.0, percent))
        node = self._get_node(step_index)
        if node.task_id is None:
            raise TypeError(
                f"set_step_progress is only supported on top-level steps; "
                f"index {step_index} is a child node"
            )
        self._progress.update(node.task_id, completed=int(percent * 100))

    def log(self, step_index: int, message: str) -> None:
        """Append a log message to any step or child step.

        Raises:
            IndexError: If step_index is out of range.
        """
        if not message:
            return
        node = self._get_node(step_index)
        node.logs.append(message)
        if node.task_id is not None:
            # Top-level: push updated logs into the task's own fields
            self._progress.update(node.task_id, logs=node.logs)
        else:
            # Child: logs already mutated on StepNode; trigger parent refresh
            assert node.parent_idx is not None
            parent = self._node_index[node.parent_idx]
            assert parent.task_id is not None
            self._progress.update(parent.task_id, refresh=True)

    def __enter__(self) -> Stepper:
        self._progress.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        self._progress.__exit__(exc_type, exc_val, exc_tb)

    def __rich_console__(self, console: Console, options: object) -> object:
        """Yield the internal Progress so Console().print(stepper) renders correctly."""
        yield self._progress

    # ------------------------------------------------------------------
    # Backward-compat shims — existing tests access these private attrs.
    # User code must not rely on them; they may be removed in a future
    # version once the internal architecture stabilises.
    # ------------------------------------------------------------------

    @property
    def _step_task_ids(self) -> list[TaskID]:
        """Legacy: task IDs of top-level steps in insertion order."""
        return [n.task_id for n in self._nodes if n.task_id is not None]

    @property
    def _tasks(self) -> dict[TaskID, Task]:
        """Legacy: delegates to internal Progress._tasks."""
        return self._progress._tasks
