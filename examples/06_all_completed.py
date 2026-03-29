"""All Completed — 5 steps all marked as COMPLETED."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper

steps = [
    StepDefinition("Fork repo", StepStatus.COMPLETED),
    StepDefinition("Create branch", StepStatus.COMPLETED),
    StepDefinition("Write code", StepStatus.COMPLETED),
    StepDefinition("Push changes", StepStatus.COMPLETED),
    StepDefinition("Merge PR", StepStatus.COMPLETED),
]

stepper = Stepper(steps=steps)
Console().print(stepper)
