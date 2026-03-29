"""Full Featured — all enhancements combined: elapsed time, progress bar, logging."""

import time

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition(
        "Clone repository", StepStatus.COMPLETED, step_description="git clone OK"
    ),
    StepDefinition(
        "Install deps", StepStatus.COMPLETED, step_description="uv sync — 47 packages"
    ),
    StepDefinition(
        "Build frontend", StepStatus.ACTIVE, step_description="Vite bundling…"
    ),
    StepDefinition("Run tests", StepStatus.PENDING),
    StepDefinition("Deploy to staging", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_style="green bold",
    active_style="magenta bold",
    pending_style="bright_black",
    connector_style="bright_black",
    show_elapsed_time=True,
    show_bar=True,
    bar_width=16,
    max_log_rows=3,
    log_style="dim italic",
    log_prefix="→",
    completed_symbol="✓",
    active_symbol="◎",
    pending_symbol="○",
)

start = time.monotonic()
stepper = Stepper(
    steps=steps,
    theme=theme,
    console=Console(),
    auto_refresh=False,
    get_time=lambda: start + 12.5,
)

# Partial progress on the active build step
stepper.set_step_progress(2, 0.72)

# Logs for completed and active steps
stepper.log(0, "Cloned into ./app (2.1s)")
stepper.log(1, "Resolved lockfile")
stepper.log(1, "Installed 47 packages in 3.4s")
stepper.log(2, "Compiling TypeScript…")
stepper.log(2, "Bundling 128 modules")
stepper.log(2, "Optimizing chunks…")

Console().print(stepper)
