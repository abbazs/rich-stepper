"""Database Migration — run database schema migrations with spinners."""

import time

from rich.console import Console
from rich.panel import Panel

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

MIGRATIONS = [
    "001_create_users.sql",
    "002_add_email_index.sql",
    "003_create_orders.sql",
    "004_add_foreign_keys.sql",
    "005_seed_admin_user.sql",
]

steps = [
    StepDefinition("Checking current schema version", StepStatus.ACTIVE),
    *[StepDefinition(f"Applying {m}", StepStatus.PENDING) for m in MIGRATIONS],
    StepDefinition("Running data integrity checks", StepStatus.PENDING),
    StepDefinition("Updating schema version to 5", StepStatus.PENDING),
]

theme = StepperTheme(
    spinner_name="circleQuarters",
    active_style="yellow bold",
    completed_style="green bold",
    pending_style="bright_black",
    connector_style="bright_black",
    show_elapsed_time=True,
    show_bar=True,
    bar_width=20,
    max_log_rows=4,
    log_style="dim italic",
    log_prefix="›",
)

console = Console()

with Stepper(steps=steps, theme=theme, console=console) as stepper:
    time.sleep(0.3)
    stepper.log(0, "Connected to postgres://db:5432/app_db")
    stepper.set_step_progress(0, 0.5)
    time.sleep(0.2)
    stepper.log(0, "Current schema version: 0")
    stepper.set_step_progress(0, 1.0)
    stepper.set_step_status(0, StepStatus.COMPLETED)

    for i, migration in enumerate(MIGRATIONS):
        step_idx = i + 1
        stepper.set_step_status(step_idx, StepStatus.ACTIVE)
        time.sleep(0.1)
        stepper.log(step_idx, f"Executing: {migration}")
        time.sleep(0.2)
        affected = (i + 1) * 12 + 3
        stepper.log(step_idx, f"Applied — {affected} rows affected")
        stepper.set_step_progress(step_idx, 0.5)
        time.sleep(0.1)
        stepper.set_step_progress(step_idx, 1.0)
        stepper.set_step_status(step_idx, StepStatus.COMPLETED)

    integrity_idx = len(MIGRATIONS) + 1
    stepper.set_step_status(integrity_idx, StepStatus.ACTIVE)
    time.sleep(0.2)
    stepper.log(integrity_idx, "Validating row counts...")
    time.sleep(0.15)
    stepper.log(integrity_idx, "users: 156 rows | orders: 423 rows")
    stepper.set_step_progress(integrity_idx, 0.5)
    time.sleep(0.15)
    stepper.log(integrity_idx, "Foreign key constraints: OK")
    stepper.set_step_progress(integrity_idx, 1.0)
    stepper.set_step_status(integrity_idx, StepStatus.COMPLETED)

    version_idx = len(MIGRATIONS) + 2
    stepper.set_step_status(version_idx, StepStatus.ACTIVE)
    time.sleep(0.2)
    stepper.log(version_idx, "UPDATE schema_version SET version = 5")
    time.sleep(0.1)
    stepper.log(version_idx, "Schema version updated: 0 → 5")
    stepper.set_step_progress(version_idx, 1.0)
    stepper.set_step_status(version_idx, StepStatus.COMPLETED)

console.print()
console.print(
    Panel(
        "[green bold]Migration complete: 5 migrations applied[/green bold]\n"
        "[dim]Schema version: 0 → 5 | Database: postgres://db:5432/app_db[/dim]",
        title="Database Migration",
        border_style="green",
    )
)
