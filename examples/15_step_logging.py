"""Step Logging — show per-step log messages with log() and max_log_rows."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

steps = [
    StepDefinition(
        "Fetch schema", StepStatus.COMPLETED, step_description="200 OK — 42 tables"
    ),
    StepDefinition(
        "Migrate database", StepStatus.ACTIVE, step_description="Applying patches…"
    ),
    StepDefinition("Seed data", StepStatus.PENDING),
    StepDefinition("Run smoke tests", StepStatus.PENDING),
]

theme = StepperTheme(
    completed_style="green bold",
    active_style="cyan bold",
    pending_style="bright_black",
    connector_style="bright_black",
    log_style="dim italic",
    log_prefix="›",
    max_log_rows=3,
)

stepper = Stepper(
    steps=steps,
    theme=theme,
    console=Console(),
    auto_refresh=False,
)

# Add logs — only last 3 shown due to max_log_rows=3
stepper.log(0, "Connected to postgres://db:5432")
stepper.log(0, "Fetched 42 table definitions")
stepper.log(1, "Applying 001_create_users.sql")
stepper.log(1, "Applying 002_add_indexes.sql")
stepper.log(1, "Applying 003_seed_config.sql")
stepper.log(1, "Applying 004_migrate_orders.sql")  # 4th log → oldest dropped

Console().print(stepper)
