"""Log Position Above — render log messages above the step label."""

from rich.console import Console

from stepper import LogPosition, StepDefinition, StepStatus, Stepper, StepperTheme

theme = StepperTheme(
    log_position=LogPosition.ABOVE,
    log_style="dim italic",
    log_prefix="›",
    max_log_rows=3,
)

steps = [
    StepDefinition("Clone repository", StepStatus.COMPLETED, step_description="v2.1.0"),
    StepDefinition("Install dependencies", StepStatus.ACTIVE, step_description="pip install..."),
    StepDefinition("Run tests", StepStatus.PENDING),
]

stepper = Stepper(steps=steps, theme=theme, console=Console(), auto_refresh=False)

# Logs appear ABOVE the label instead of below
stepper.log(0, "Cloned in 1.2s")
stepper.log(0, "Checked out main branch")
stepper.log(1, "Installing numpy...")
stepper.log(1, "Installing pandas...")
stepper.log(1, "Installing requests...")

Console().print(stepper)
