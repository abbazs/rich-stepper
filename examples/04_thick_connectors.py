"""Thick Connectors — line_thickness=3 with triple vertical bar connector."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition("Stage 1", StepStatus.COMPLETED),
    StepDefinition("Stage 2", StepStatus.ACTIVE),
    StepDefinition("Stage 3", StepStatus.PENDING),
]

theme = StepperTheme(
    line_thickness=3,
    connector_symbol="┃",
)

stepper = Stepper(steps=steps, theme=theme)
Console().print(stepper)
