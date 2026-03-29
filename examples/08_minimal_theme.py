"""Minimal Theme — simple ASCII symbols, thin connectors, no descriptions."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition("Start", StepStatus.COMPLETED),
    StepDefinition("Process", StepStatus.ACTIVE),
    StepDefinition("End", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_symbol="+",
    active_symbol=">",
    pending_symbol="o",
    connector_symbol="|",
    line_thickness=1,
)

stepper = Stepper(steps=steps, theme=theme)
Console().print(stepper)
