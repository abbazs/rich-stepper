"""Many Steps — 12-step CI/CD pipeline workflow."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition("Checkout", StepStatus.COMPLETED),
    StepDefinition("Install deps", StepStatus.COMPLETED),
    StepDefinition("Lint", StepStatus.COMPLETED),
    StepDefinition("Type check", StepStatus.COMPLETED),
    StepDefinition(
        "Unit tests", StepStatus.ACTIVE, step_description="Running 142 tests"
    ),
    StepDefinition("Integration tests", StepStatus.PENDING),
    StepDefinition("Build image", StepStatus.PENDING),
    StepDefinition("Push to registry", StepStatus.PENDING),
    StepDefinition("Deploy staging", StepStatus.PENDING),
    StepDefinition("Smoke tests", StepStatus.PENDING),
    StepDefinition("Deploy production", StepStatus.PENDING),
    StepDefinition("Health check", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_style="green bold",
    active_style="yellow bold",
    pending_style="bright_black",
    connector_style="dim",
)

stepper = Stepper(steps=steps, theme=theme)
Console().print(stepper)
