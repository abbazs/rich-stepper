"""CI/CD Pipeline — simulate a build-test-deploy workflow with spinners."""

import time

from rich.console import Console
from rich.table import Table

from stepper import StepStatus, Stepper, StepperTheme

PIPELINE_STEPS = [
    ("Checkout code", 0.4, 0.3),
    ("Install dependencies", 1.2, 0.5),
    ("Lint", 0.8, 0.4),
    ("Run tests", 2.0, 0.6),
    ("Build artifacts", 1.5, 0.5),
    ("Run integration tests", 1.8, 0.6),
    ("Deploy to staging", 1.0, 0.4),
    ("Health check", 0.6, 0.3),
]

theme = StepperTheme(
    spinner_name="line",
    spinner_speed=1.5,
    active_style="cyan bold",
    show_elapsed_time=True,
    show_bar=True,
    bar_width=16,
    max_log_rows=3,
    log_style="dim italic",
    log_prefix="→",
)

console = Console()
step_results: list[dict[str, str]] = []

with Stepper(console=console, theme=theme) as stepper:
    for name, duration, progress_step in PIPELINE_STEPS:
        idx = stepper.add_step(
            name, status=StepStatus.ACTIVE, step_description="Running…"
        )
        start = time.monotonic()

        progress = 0.0
        while progress < 1.0:
            time.sleep(duration * progress_step)
            progress = min(progress + progress_step, 1.0)
            stepper.set_step_progress(idx, progress)

        elapsed = time.monotonic() - start
        stepper.log(idx, f"Completed in {elapsed:.1f}s")
        stepper.set_step_status(idx, StepStatus.COMPLETED)
        step_results.append(
            {"step": name, "duration": f"{elapsed:.1f}s", "status": "✓ Pass"}
        )

console.print()
table = Table(title="Pipeline Summary", show_header=True, header_style="bold cyan")
table.add_column("Step", style="white")
table.add_column("Duration", justify="right", style="green")
table.add_column("Status", justify="center")

for r in step_results:
    table.add_row(r["step"], r["duration"], f"[green]{r['status']}[/green]")

console.print(table)
