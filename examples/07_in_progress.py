"""In Progress — typical workflow: 2 completed, 1 active, 2 pending."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition("Gather requirements", StepStatus.COMPLETED),
    StepDefinition(
        "Design architecture",
        StepStatus.COMPLETED,
        step_description="System design doc",
    ),
    StepDefinition(
        "Implement features", StepStatus.ACTIVE, step_description="Sprint 1"
    ),
    StepDefinition("QA testing", StepStatus.PENDING),
    StepDefinition("Go live", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_style="green bold",
    active_style="cyan bold",
    pending_style="bright_black",
    connector_style="bright_black",
)

stepper = Stepper(steps=steps, theme=theme)
Console().print(stepper)
