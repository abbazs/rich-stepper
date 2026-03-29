from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StepStatus(Enum):
    COMPLETED = "completed"
    ACTIVE = "active"
    PENDING = "pending"


@dataclass(frozen=True)
class StepDefinition:
    label: str
    status: StepStatus = StepStatus.PENDING
    step_description: str | None = None
