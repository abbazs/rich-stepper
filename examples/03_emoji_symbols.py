"""Emoji Symbols — use emoji characters for step indicators."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition("Plan", StepStatus.COMPLETED, step_description="Define scope"),
    StepDefinition("Build", StepStatus.ACTIVE),
    StepDefinition("Test", StepStatus.PENDING),
    StepDefinition("Release", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_symbol="✅",
    active_symbol="🔵",
    pending_symbol="⭕",
)

stepper = Stepper(steps=steps, theme=theme)
Console().print(stepper)
