"""Spinner Basics — animated step indicators."""

import time

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition(
        "Initialize", StepStatus.ACTIVE, step_description="Setting up workspace…"
    ),
    StepDefinition("Load config", StepStatus.PENDING),
    StepDefinition("Process data", StepStatus.PENDING),
    StepDefinition("Generate report", StepStatus.PENDING),
    StepDefinition("Cleanup", StepStatus.PENDING),
]

# Default theme uses "dots" spinner — the simplest spinner animation
theme = StepperTheme(
    show_elapsed_time=True,
    max_log_rows=2,
    log_prefix="›",
)

stepper = Stepper(steps=steps, theme=theme)
with stepper:
    for i in range(len(steps)):
        stepper.log(i, f"Starting: {steps[i].label}")
        time.sleep(0.8)
        stepper.log(i, f"Finished: {steps[i].label}")
        stepper.set_step_status(i, StepStatus.COMPLETED)
        if i + 1 < len(steps):
            stepper.set_step_status(i + 1, StepStatus.ACTIVE)
