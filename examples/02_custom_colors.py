"""Custom Colors — override completed/active/pending and connector styles."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition("Research", StepStatus.COMPLETED),
    StepDefinition("Prototype", StepStatus.ACTIVE, step_description="Building MVP"),
    StepDefinition("Review", StepStatus.PENDING),
    StepDefinition("Ship", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_style="green bold",
    active_style="yellow bold",
    pending_style="dim",
    connector_style="dim",
)

stepper = Stepper(steps=steps, theme=theme)
Console().print(stepper)
