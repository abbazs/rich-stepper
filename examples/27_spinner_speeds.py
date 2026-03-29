"""Spinner Speeds — compare animation speeds from slow to fast."""

import time

from rich.console import Console
from rich.rule import Rule

from stepper import StepStatus, Stepper, StepperTheme

SPEEDS = [
    (0.3, "Slow"),
    (0.7, "Medium-Slow"),
    (1.0, "Default"),
    (2.0, "Fast"),
    (4.0, "Very Fast"),
]

console = Console()

for speed, label in SPEEDS:
    console.print()
    console.print(Rule(title=f"[bold cyan]{label} (speed: {speed}x)[/bold cyan]"))

    theme = StepperTheme(
        spinner_name="dots",
        spinner_speed=speed,
        active_style="cyan bold",
        completed_style="green bold",
        pending_style="bright_black",
        connector_style="bright_black",
        show_elapsed_time=True,
        max_log_rows=2,
        log_style="dim italic",
        log_prefix="›",
    )

    with Stepper(console=console, theme=theme) as stepper:
        for j in range(3):
            idx = stepper.add_step(
                f"Step {j + 1}", status=StepStatus.ACTIVE, step_description=label
            )
            stepper.log(idx, f"Speed: {speed}x — spinner_name='dots'")
            time.sleep(0.8)
            stepper.set_step_status(idx, StepStatus.COMPLETED)

console.print()
console.print(Rule(title="[bold]Summary[/bold]"))
console.print(
    "[dim]Higher spinner_speed = faster animation rotation.\n"
    "Adjust via StepperTheme(spinner_speed=N) where N is a float multiplier.\n"
    "Default is 1.0. Use 0.3–0.5 for a relaxed feel, 2.0–4.0 for urgency.[/dim]"
)
