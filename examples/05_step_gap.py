"""Step Gap Spacing — extra vertical space between steps via step_gap=2."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition("Initialize", StepStatus.COMPLETED),
    StepDefinition(
        "Configure", StepStatus.ACTIVE, step_description="Set up environment"
    ),
    StepDefinition("Execute", StepStatus.PENDING),
    StepDefinition("Finalize", StepStatus.PENDING),
]

theme = StepperTheme(step_gap=2)

stepper = Stepper(steps=steps, theme=theme)
Console().print(stepper)
