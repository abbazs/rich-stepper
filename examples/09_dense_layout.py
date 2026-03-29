"""Dense Layout — most compact rendering with step_gap=0 and label_padding=0."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition("Lint", StepStatus.COMPLETED),
    StepDefinition("Build", StepStatus.ACTIVE),
    StepDefinition("Test", StepStatus.PENDING),
    StepDefinition("Deploy", StepStatus.PENDING),
]

theme = StepperTheme(
    step_gap=0,
    label_padding=0,
    connector_style="dim",
)

stepper = Stepper(steps=steps, theme=theme)
Console().print(stepper)
