"""Data Pipeline — ETL workflow with spinner animation."""

import time

from rich.console import Console
from rich.panel import Panel

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition(
        "Connect to source DB",
        StepStatus.ACTIVE,
        step_description="postgres://src:5432",
    ),
    StepDefinition("Extract records", StepStatus.PENDING),
    StepDefinition("Validate schema", StepStatus.PENDING),
    StepDefinition("Transform data", StepStatus.PENDING),
    StepDefinition("Aggregate metrics", StepStatus.PENDING),
    StepDefinition("Load to warehouse", StepStatus.PENDING),
    StepDefinition("Create indexes", StepStatus.PENDING),
    StepDefinition("Verify row counts", StepStatus.PENDING),
]

theme = StepperTheme(
    spinner_name="arrow",
    spinner_speed=1.5,
    active_style="cyan bold",
    show_elapsed_time=True,
    show_bar=True,
    bar_width=16,
    max_log_rows=4,
    log_style="dim italic",
    log_prefix="→",
)

console = Console()
pipeline_start = time.monotonic()
total_rows = 0

stepper = Stepper(steps=steps, theme=theme, console=console)
with stepper:
    for i in range(len(steps)):
        label = steps[i].label
        if label == "Extract records":
            for pct in (20, 40, 60, 80, 100):
                time.sleep(0.2)
                stepper.set_step_progress(i, pct / 100)
                batch_rows = 12_500
                total_rows += batch_rows
                stepper.log(i, f"Fetched {pct}% — {total_rows:,} rows so far")
            stepper.log(i, f"Extracted {total_rows:,} total rows")
        elif label == "Transform data":
            for pct in (25, 50, 75, 100):
                time.sleep(0.15)
                stepper.set_step_progress(i, pct / 100)
                stepper.log(i, f"Transform batch {pct // 25}/4 — mapping columns…")
            stepper.log(i, f"Applied 8 transformations to {total_rows:,} rows")
        elif label == "Load to warehouse":
            for pct in (33, 66, 100):
                time.sleep(0.2)
                stepper.set_step_progress(i, pct / 100)
                stepper.log(i, f"Loading batch {pct // 33}/3 to warehouse…")
            stepper.log(i, f"Loaded {total_rows:,} rows to warehouse")
        elif label == "Verify row counts":
            time.sleep(0.3)
            stepper.set_step_progress(i, 0.5)
            stepper.log(i, f"Source: {total_rows:,} rows")
            time.sleep(0.3)
            stepper.set_step_progress(i, 1.0)
            stepper.log(i, f"Warehouse: {total_rows:,} rows — matched ✓")
        else:
            time.sleep(0.4)
            stepper.set_step_progress(i, 1.0)
            stepper.log(i, f"{label} complete")

        stepper.set_step_status(i, StepStatus.COMPLETED)
        if i + 1 < len(steps):
            stepper.set_step_status(i + 1, StepStatus.ACTIVE)

elapsed = time.monotonic() - pipeline_start

console.print()
console.print(
    Panel(
        f"[bold green]Pipeline completed successfully[/bold green]\n\n"
        f"  Rows processed : [cyan]{total_rows:,}[/cyan]\n"
        f"  Duration       : [cyan]{elapsed:.1f}s[/cyan]\n"
        f"  Throughput     : [cyan]{total_rows / max(elapsed, 0.01):,.0f} rows/s[/cyan]",
        title="ETL Summary",
        border_style="cyan",
    )
)
