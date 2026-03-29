"""API Health Check — monitor multiple service endpoints with spinners."""

import random
import time

from rich.console import Console
from rich.table import Table

from stepper import StepStatus, Stepper, StepperTheme

SERVICES = [
    ("auth.example.com", "/health", "Authentication"),
    ("api.example.com", "/status", "API Gateway"),
    ("db.example.com", "/ping", "Database"),
    ("cache.example.com", "/ready", "Cache"),
    ("queue.example.com", "/stats", "Message Queue"),
    ("cdn.example.com", "/probe", "CDN"),
]

theme = StepperTheme(
    spinner_name="bounce",
    active_style="cyan bold",
    completed_style="green bold",
    pending_style="bright_black",
    connector_style="bright_black",
    show_elapsed_time=True,
    show_bar=True,
    bar_width=20,
    max_log_rows=3,
    log_style="dim italic",
    log_prefix="›",
)

console = Console()
results: list[dict[str, str]] = []

# Pre-select 1-2 services to be slow
slow_indices = set(random.sample(range(len(SERVICES)), k=random.randint(1, 2)))

with Stepper(console=console, theme=theme) as stepper:
    for i, (host, endpoint, name) in enumerate(SERVICES):
        idx = stepper.add_step(
            name, status=StepStatus.ACTIVE, step_description=f"{host}{endpoint}"
        )
        stepper.log(idx, f"Connecting to {host}...")

        # Simulate network latency
        base_latency = round(random.uniform(0.05, 0.3), 3)
        is_slow = i in slow_indices
        if is_slow:
            base_latency += round(random.uniform(0.5, 1.2), 3)

        time.sleep(base_latency)
        stepper.set_step_progress(idx, 0.5)
        stepper.log(idx, f"GET {endpoint} → 200 OK ({base_latency}s)")

        # Simulate occasional failures
        is_down = random.random() < 0.15
        if is_down:
            time.sleep(0.2)
            stepper.log(idx, "WARNING: Response timeout, retrying...")
            time.sleep(0.3)
            stepper.log(idx, f"GET {endpoint} → 503 Service Unavailable")
            results.append(
                {"service": name, "status": "DOWN", "latency": f"{base_latency:.3f}s"}
            )
        else:
            time.sleep(0.1)
            status_code = random.choice([200, 200, 200, 201, 204])
            stepper.log(
                idx, f"Healthy — {status_code}, {random.randint(50, 500)} bytes"
            )
            results.append(
                {"service": name, "status": "UP", "latency": f"{base_latency:.3f}s"}
            )

        stepper.set_step_progress(idx, 1.0)
        stepper.set_step_status(idx, StepStatus.COMPLETED)

# Print summary table
console.print()
table = Table(
    title="Health Check Results", show_header=True, header_style="bold magenta"
)
table.add_column("Service", style="cyan")
table.add_column("Status", justify="center")
table.add_column("Latency", justify="right", style="green")

for r in results:
    style = "green" if r["status"] == "UP" else "red"
    table.add_row(r["service"], f"[{style}]{r['status']}[/{style}]", r["latency"])

console.print(table)
