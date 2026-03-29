"""Basic Stepper — default theme with 4 steps showing mixed statuses."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper

steps = [
    StepDefinition("Clone repository", StepStatus.COMPLETED),
    StepDefinition("Install dependencies", StepStatus.ACTIVE),
    StepDefinition("Run tests", StepStatus.PENDING),
    StepDefinition("Deploy", StepStatus.PENDING),
]

stepper = Stepper(steps=steps)
Console().print(stepper)
