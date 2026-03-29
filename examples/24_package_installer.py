"""Package Installer — simulate installing packages with dependency resolution."""

import time

from rich.console import Console

from stepper import StepStatus, Stepper, StepperTheme

PACKAGES = [
    ("flask", "2.3.0", ["werkzeug", "jinja2", "click"]),
    ("requests", "2.31.0", ["urllib3", "certifi", "charset-normalizer"]),
    ("numpy", "1.25.0", []),
    ("pandas", "2.1.0", ["numpy", "pytz", "tzdata"]),
    ("scikit-learn", "1.3.0", ["numpy", "scipy", "joblib"]),
]

theme = StepperTheme(
    spinner_name="dots",
    active_style="cyan bold",
    completed_style="green bold",
    pending_style="bright_black",
    connector_style="bright_black",
    show_elapsed_time=True,
    show_bar=True,
    bar_width=20,
    max_log_rows=6,
    log_style="dim italic",
    log_prefix="›",
)

console = Console()

with Stepper(console=console, theme=theme) as stepper:
    for name, version, deps in PACKAGES:
        idx = stepper.add_step(
            f"Installing {name} {version}",
            status=StepStatus.ACTIVE,
            step_description=f"{len(deps)} dependencies",
        )
        stepper.log(idx, "Resolving dependencies...")
        time.sleep(0.15)
        stepper.set_step_progress(idx, 0.15)

        for dep in deps:
            time.sleep(0.08)
            stepper.log(idx, f"  \u2713 {dep} (already installed)")

        progress = 0.4
        stepper.set_step_progress(idx, progress)
        time.sleep(0.1)

        size_mb = round(len(name) * 0.3 + len(deps) * 0.5 + 1.0, 1)
        stepper.log(idx, f"Downloading {name}-{version}.tar.gz ({size_mb} MB)...")
        time.sleep(0.2)
        progress = 0.6
        stepper.set_step_progress(idx, progress)

        stepper.log(idx, "Extracting archive...")
        time.sleep(0.1)
        progress = 0.8
        stepper.set_step_progress(idx, progress)

        stepper.log(idx, f"Installing {name}-{version}...")
        time.sleep(0.15)
        stepper.log(idx, f"Successfully installed {name}-{version}")
        stepper.set_step_progress(idx, 1.0)
        stepper.set_step_status(idx, StepStatus.COMPLETED)

console.print()
console.print(
    f"[green bold]Successfully installed {len(PACKAGES)} packages[/green bold]"
)
