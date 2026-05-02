"""Failed, Warning, Skipped — demonstrate non-success terminal statuses."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

# Custom theme with distinct symbols for each status
theme = StepperTheme(
    failed_style="red bold",
    warning_style="yellow bold",
    skipped_style="bright_black",
)

steps = [
    StepDefinition("Fetch config", StepStatus.COMPLETED, step_description="200 OK"),
    StepDefinition("Validate schema", StepStatus.COMPLETED, step_description="All checks passed"),
    StepDefinition("Run linting", StepStatus.WARNING, step_description="3 warnings found"),
    StepDefinition("Run unit tests", StepStatus.FAILED, step_description="12 of 150 tests failed"),
    StepDefinition("Run integration tests", StepStatus.SKIPPED, step_description="Skipped due to unit test failures"),
    StepDefinition("Deploy to staging", StepStatus.PENDING),
    StepDefinition("Deploy to production", StepStatus.PENDING),
]

stepper = Stepper(steps=steps, theme=theme, console=Console(), auto_refresh=False)
Console().print(stepper)
