"""DevOps Deployment — full deployment pipeline with spinners."""

import time

from rich.console import Console
from rich.table import Table

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

DEPLOY_STEPS = [
    "Pulling latest code from main",
    "Running pre-deploy checks",
    "Building Docker image",
    "Pushing to container registry",
    "Running smoke tests",
    "Updating Kubernetes deployment",
    "Rolling out to production",
    "Post-deploy verification",
]

theme = StepperTheme(
    spinner_name="triangle",
    active_style="magenta",
    completed_style="green bold",
    pending_style="bright_black",
    connector_style="bright_black",
    show_elapsed_time=True,
    show_bar=True,
    bar_width=20,
    max_log_rows=5,
    log_style="dim italic",
    log_prefix="›",
)

console = Console()
step_results: list[dict[str, str]] = []

with Stepper(
    steps=[
        StepDefinition(s, StepStatus.ACTIVE if i == 0 else StepStatus.PENDING)
        for i, s in enumerate(DEPLOY_STEPS)
    ],
    theme=theme,
    console=console,
) as stepper:
    for i, step_label in enumerate(DEPLOY_STEPS):
        step_start = time.monotonic()

        if i > 0:
            stepper.set_step_status(i, StepStatus.ACTIVE)

        if i == 0:  # Pull code
            stepper.log(i, "$ git pull origin main")
            time.sleep(0.3)
            stepper.log(i, "Already up to date — 3 commits ahead")
            stepper.set_step_progress(i, 1.0)

        elif i == 1:  # Pre-deploy checks
            stepper.log(i, "Linting...")
            time.sleep(0.15)
            stepper.set_step_progress(i, 0.3)
            stepper.log(i, "Type checking...")
            time.sleep(0.15)
            stepper.set_step_progress(i, 0.6)
            stepper.log(i, "Security scan — no vulnerabilities")
            time.sleep(0.1)
            stepper.log(i, "All checks passed")
            stepper.set_step_progress(i, 1.0)

        elif i == 2:  # Docker build
            stages = ["base", "builder", "runtime"]
            for j, stage in enumerate(stages):
                stepper.log(
                    i, f"Step {j + 1}/{len(stages)}: {stage} — FROM python:3.12-slim"
                )
                time.sleep(0.2)
                stepper.set_step_progress(i, (j + 1) / len(stages))
            stepper.log(i, "Image built: app:2.4.1 (128 MB)")
            stepper.set_step_progress(i, 1.0)

        elif i == 3:  # Push to registry
            stepper.log(i, "$ docker push registry.example.com/app:2.4.1")
            time.sleep(0.2)
            stepper.set_step_progress(i, 0.3)
            stepper.log(i, "Layer 1/3 pushed...")
            time.sleep(0.15)
            stepper.set_step_progress(i, 0.6)
            stepper.log(i, "Layer 3/3 pushed")
            time.sleep(0.1)
            stepper.log(i, "Digest: sha256:a3f8...c4d2")
            stepper.set_step_progress(i, 1.0)

        elif i == 4:  # Smoke tests
            tests = ["/health", "/api/v1/status", "/api/v1/docs"]
            for test in tests:
                stepper.log(i, f"GET {test} → 200 OK")
                time.sleep(0.1)
                stepper.set_step_progress(i, 0.33)
            stepper.log(i, "3/3 smoke tests passed")
            stepper.set_step_progress(i, 1.0)

        elif i == 5:  # Kubernetes
            stepper.log(i, "$ kubectl apply -f k8s/deployment.yaml")
            time.sleep(0.2)
            stepper.set_step_progress(i, 0.4)
            stepper.log(i, "deployment.apps/app configured")
            time.sleep(0.15)
            stepper.log(i, "Pod app-7d4f8b9c6-x2k9l — Running")
            stepper.set_step_progress(i, 0.8)
            time.sleep(0.1)
            stepper.log(i, "Rollout: 1/1 replicas available")
            stepper.set_step_progress(i, 1.0)

        elif i == 6:  # Rollout
            stepper.log(i, "Traffic shifting: 0% → 50% → 100%")
            time.sleep(0.3)
            stepper.set_step_progress(i, 0.5)
            stepper.log(i, "Canary analysis — no errors detected")
            time.sleep(0.2)
            stepper.log(i, "Full traffic on v2.4.1")
            stepper.set_step_progress(i, 1.0)

        elif i == 7:  # Post-deploy
            stepper.log(i, "Verifying /health endpoint...")
            time.sleep(0.2)
            stepper.log(i, "Response: 200 OK — uptime: 5s")
            stepper.set_step_progress(i, 0.5)
            time.sleep(0.1)
            stepper.log(i, "Metrics forwarding confirmed")
            stepper.set_step_progress(i, 1.0)

        duration = f"{time.monotonic() - step_start:.1f}s"
        step_results.append({"step": step_label, "status": "OK", "duration": duration})
        stepper.set_step_status(i, StepStatus.COMPLETED)

console.print()
table = Table(title="Deployment Summary", show_header=True, header_style="bold magenta")
table.add_column("Step", style="cyan")
table.add_column("Status", justify="center")
table.add_column("Duration", justify="right", style="green")

for r in step_results:
    table.add_row(r["step"], f"[green]{r['status']}[/green]", r["duration"])

console.print(table)
