"""Live Update — animate step progression using context manager."""

import time

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition("Connecting", StepStatus.ACTIVE),
    StepDefinition("Downloading", StepStatus.PENDING),
    StepDefinition("Installing", StepStatus.PENDING),
    StepDefinition("Verifying", StepStatus.PENDING),
    StepDefinition("Done", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_style="green bold",
    active_style="cyan bold",
    pending_style="bright_black",
    connector_style="bright_black",
)

stepper = Stepper(steps=steps, theme=theme)
with stepper:
    for i in range(len(steps)):
        time.sleep(0.5)
        if i > 0:
            stepper.set_step_status(i, StepStatus.ACTIVE)
        time.sleep(0.5)
        stepper.set_step_status(i, StepStatus.COMPLETED)
