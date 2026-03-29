"""Progress Bar — show per-step progress with show_bar=True and set_step_progress()."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition(
        "Download assets", StepStatus.COMPLETED, step_description="All files fetched"
    ),
    StepDefinition(
        "Process data", StepStatus.ACTIVE, step_description="Transforming rows…"
    ),
    StepDefinition("Generate report", StepStatus.PENDING),
    StepDefinition("Upload results", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_style="green bold",
    active_style="yellow bold",
    pending_style="bright_black",
    connector_style="bright_black",
    show_bar=True,
    bar_width=20,
)

stepper = Stepper(
    steps=steps,
    theme=theme,
    console=Console(),
    auto_refresh=False,
)

stepper.set_step_progress(1, 0.6)

Console().print(stepper)
