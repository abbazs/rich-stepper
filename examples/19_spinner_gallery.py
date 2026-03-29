"""Spinner Gallery — compare all popular spinner styles side-by-side."""

import time

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

SPINNERS = [
    ("dots", "Dots (default)"),
    ("line", "Line"),
    ("arrow", "Arrow"),
    ("star", "Star"),
    ("dots2", "Dots Braille"),
    ("bounce", "Bounce"),
    ("circleQuarters", "Circle Quarters"),
    ("triangle", "Triangle"),
]

console = Console()

for spinner_name, title in SPINNERS:
    theme = StepperTheme(
        spinner_name=spinner_name,
        spinner_speed=1.2,
        active_style="cyan bold",
        show_elapsed_time=True,
        max_log_rows=2,
        log_prefix="›",
    )

    steps = [
        StepDefinition("Step A", StepStatus.ACTIVE, step_description="First action"),
        StepDefinition("Step B", StepStatus.PENDING, step_description="Second action"),
        StepDefinition("Step C", StepStatus.PENDING, step_description="Third action"),
    ]

    stepper = Stepper(steps=steps, theme=theme, console=console)
    with stepper:
        for i in range(len(steps)):
            stepper.log(i, f"Working on {steps[i].label}…")
            time.sleep(0.6)
            stepper.log(i, f"{steps[i].label} done")
            stepper.set_step_status(i, StepStatus.COMPLETED)
            if i + 1 < len(steps):
                stepper.set_step_status(i + 1, StepStatus.ACTIVE)

    console.print(f"  ── {title} (spinner_name={spinner_name!r}) ──\n")
