"""Internal tree node representing a single step in the stepper."""

from __future__ import annotations

from dataclasses import dataclass

from rich.progress import TaskID

from stepper.types import StepStatus


@dataclass
class StepNode:
    """Mutable internal representation of a step or group node.

    Each node maps to one Rich Task (via task_id). Children are embedded
    here rather than as separate Rich Tasks so connector-row arithmetic
    stays localised to the render cycle.
    """

    idx: int
    label: str
    status: StepStatus
    description: str | None
    logs: list[str]
    children: list[StepNode]
    is_parallel: bool
    parent_idx: int | None
    task_id: TaskID | None
