"""Single Step — one step only, no connector rendered for the last step."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper

steps = [
    StepDefinition(
        "Only step", StepStatus.ACTIVE, step_description="This is the sole step"
    ),
]

stepper = Stepper(steps=steps)
Console().print(stepper)
