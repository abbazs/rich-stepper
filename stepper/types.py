from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    COMPLETED = "completed"
    ACTIVE = "active"
    PENDING = "pending"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class LogPosition(Enum):
    BELOW = "below"
    ABOVE = "above"


@dataclass(frozen=True)
class StepDefinition:
    label: str
    status: StepStatus = StepStatus.PENDING
    step_description: str | None = None
    sub_steps: list[StepDefinition] | None = field(default=None)
    parallel: bool = False
