"""Elapsed Time — show elapsed time per step with show_elapsed_time=True."""

import time

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition(
        "Initialize project", StepStatus.COMPLETED, step_description="Created repo"
    ),
    StepDefinition(
        "Install dependencies", StepStatus.COMPLETED, step_description="uv sync"
    ),
    StepDefinition(
        "Run build", StepStatus.ACTIVE, step_description="Compiling assets…"
    ),
    StepDefinition("Deploy", StepStatus.PENDING),
    StepDefinition("Verify", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_style="green bold",
    active_style="cyan bold",
    pending_style="bright_black",
    connector_style="bright_black",
    show_elapsed_time=True,
)

# auto_refresh=False for snapshot rendering; use get_time to freeze completed times
start = time.monotonic()
stepper = Stepper(
    steps=steps,
    theme=theme,
    console=Console(),
    auto_refresh=False,
    get_time=lambda: start + 5.0,  # simulate 5s elapsed for the active step
)

Console().print(stepper)
