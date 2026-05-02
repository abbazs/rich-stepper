# rich-stepper

[![PyPI version](https://img.shields.io/pypi/v/rich-stepper)](https://pypi.org/project/rich-stepper)
[![Python versions](https://img.shields.io/pypi/pyversions/rich-stepper)](https://pypi.org/project/rich-stepper)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/abbazs/rich-stepper/blob/main/LICENSE)

Beautiful multi-step terminal progress widget for [Rich](https://rich.readthedocs.io/). Connected indicators, per-step logging, elapsed timers, and optional progress bars — all rendered live in your terminal.

## Installation

```
pip install rich-stepper
```

Requires Python 3.10+ and [Rich](https://pypi.org/project/rich/) 13+.

## Quick Start

```python
from rich.console import Console
from stepper import StepDefinition, StepStatus, Stepper

steps = [
    StepDefinition("Clone repository", StepStatus.COMPLETED),
    StepDefinition("Install dependencies", StepStatus.ACTIVE),
    StepDefinition("Run tests", StepStatus.PENDING),
    StepDefinition("Deploy", StepStatus.PENDING),
]

stepper = Stepper(steps=steps)
Console().print(stepper)
```

Renders a connected vertical stepper with status indicators:

```
● Clone repository
│
◉ Install dependencies
│
○ Run tests
│
○ Deploy
```

## Live Updates

Use the context manager for animated step progression:

```python
import time
from stepper import StepDefinition, StepStatus, Stepper

steps = [
    StepDefinition("Connecting", StepStatus.ACTIVE),
    StepDefinition("Downloading", StepStatus.PENDING),
    StepDefinition("Installing", StepStatus.PENDING),
    StepDefinition("Done", StepStatus.PENDING),
]

stepper = Stepper(steps=steps)
with stepper:
    for i in range(len(steps)):
        time.sleep(0.5)
        if i > 0:
            stepper.set_step_status(i, StepStatus.ACTIVE)
        time.sleep(0.5)
        stepper.set_step_status(i, StepStatus.COMPLETED)
```

## Per-Step Logging

Append log messages to any step with `stepper.log()`:

```python
from rich.console import Console
from stepper import StepDefinition, StepStatus, Stepper, StepperTheme

theme = StepperTheme(max_log_rows=3, log_style="dim italic", log_prefix="›")

stepper = Stepper(
    steps=[
        StepDefinition("Fetch schema", StepStatus.COMPLETED, step_description="200 OK"),
        StepDefinition("Migrate database", StepStatus.ACTIVE, step_description="Applying patches…"),
        StepDefinition("Seed data", StepStatus.PENDING),
    ],
    theme=theme,
    console=Console(),
    auto_refresh=False,
)

stepper.log(0, "Connected to postgres://db:5432")
stepper.log(0, "Fetched 42 table definitions")
stepper.log(1, "Applying 001_create_users.sql")
stepper.log(1, "Applying 002_add_indexes.sql")
stepper.log(1, "Applying 003_seed_config.sql")
stepper.log(1, "Applying 004_migrate_orders.sql")  # oldest dropped (max_log_rows=3)

Console().print(stepper)
```

Logs render inline below (or above) each step label. Set `max_log_rows` to cap visible lines, or leave it `None` for terminal-height-aware truncation.

### Log position

Control where logs appear relative to the step label:

```python
from stepper import LogPosition, StepperTheme

theme = StepperTheme(log_position=LogPosition.ABOVE)  # logs above the label
```

## Progress Bars

Enable per-step progress bars with `show_bar=True`:

```python
theme = StepperTheme(show_bar=True, bar_width=20)
stepper = Stepper(steps=steps, theme=theme, console=Console(), auto_refresh=False)
stepper.set_step_progress(1, 0.6)  # 60% complete
Console().print(stepper)
```

The `percent` argument is clamped to `[0.0, 1.0]`.

## Elapsed Time

Show elapsed time per step:

```python
theme = StepperTheme(show_elapsed_time=True)
```

Completed and active steps show elapsed time. Pending steps display `-:--:--`. Time freezes when a step is marked completed.

## Dynamic Steps

Add steps at runtime inside a context manager:

```python
with Stepper(theme=theme, console=console) as stepper:
    for url, label in sites:
        idx = stepper.add_step(label, status=StepStatus.ACTIVE, step_description=url)
        stepper.log(idx, f"Fetching {url}")
        # ... do work ...
        stepper.set_step_status(idx, StepStatus.COMPLETED)
```

## Lifecycle Callbacks

Hook into status transitions with optional callbacks:

```python
def on_start(idx: int, label: str) -> None:
    print(f"Starting {label}")

def on_complete(idx: int, label: str) -> None:
    print(f"Finished {label}")

def on_fail(idx: int, label: str, description: str | None) -> None:
    send_alert(label, description)

stepper = Stepper(
    steps=steps,
    on_step_start=on_start,
    on_step_complete=on_complete,
    on_step_fail=on_fail,
)
```

Callbacks fire synchronously when `set_step_status` (or convenience methods `succeed`/`fail`/`warn`/`skip`) transitions a step.

## Theming

`StepperTheme` is a frozen dataclass — set any combination of fields at construction:

### Symbols and styles

```python
theme = StepperTheme(
    completed_symbol="✓",
    active_symbol="◎",
    pending_symbol="○",
    completed_style="green bold",
    active_style="magenta bold",
    pending_style="bright_black",
)
```

### Connectors

```python
theme = StepperTheme(
    connector_symbol="│",
    connector_style="bright_black",
    line_thickness=2,    # repeat connector symbol N times
    step_gap=1,          # blank lines between steps
)
```

### Label formatting

```python
theme = StepperTheme(
    label_style="",
    step_description_style="dim",
    label_padding=2,     # spaces before label text
)
```

### Progress bar styling

```python
theme = StepperTheme(
    show_bar=True,
    bar_width=20,
    bar_complete_style="bar.complete",
    bar_finished_style="bar.finished",
    bar_pulse_style="bar.pulse",
)
```

### Log styling

```python
from stepper import LogPosition

theme = StepperTheme(
    log_position=LogPosition.BELOW,  # or LogPosition.ABOVE
    max_log_rows=5,                  # None for terminal-aware
    log_style="dim italic",
    log_prefix="›",
)
```

### Time column

```python
theme = StepperTheme(
    show_elapsed_time=True,
    time_style="progress.elapsed",
)
```

## API Reference

### `Stepper`

Extends `rich.progress.Progress`. All Progress constructor args are forwarded.

| Method | Description |
|---|---|
| `Stepper(steps, theme, console, on_step_start, on_step_complete, on_step_fail, ...)` | Create stepper with optional initial steps, theme, and lifecycle callbacks |
| `add_step(label, status, step_description)` | Add a top-level step, returns `int` (global index) |
| `add_steps(steps)` | Add multiple steps from `StepDefinition` list (handles parallel and sub_steps) |
| `add_parallel_group(label, step_description)` | Add a parallel group header, returns `int` (group index) |
| `add_parallel_step(group_index, label, status, step_description)` | Add a child to a parallel group, returns `int` (child index) |
| `add_sub_step(parent_index, label, status, step_description)` | Add a sequential sub-step under a regular step, returns `int` (child index) |
| `set_step_status(index, status)` | Update step status by global index |
| `set_step_progress(index, percent)` | Set progress bar (0.0–1.0), top-level steps only |
| `log(index, message)` | Append a log message to any step |
| `succeed(index, description)` | Mark step as COMPLETED with optional description |
| `fail(index, description)` | Mark step as FAILED with optional description |
| `warn(index, description)` | Mark step as WARNING with optional description |
| `skip(index, description)` | Mark step as SKIPPED with optional description |

### `StepStatus`

| Value | Symbol | Description |
|---|---|---|
| `StepStatus.COMPLETED` | `●` | Step finished successfully |
| `StepStatus.ACTIVE` | `◉` | Currently running (animated spinner) |
| `StepStatus.PENDING` | `○` | Not yet started |
| `StepStatus.FAILED` | `✕` | Step failed |
| `StepStatus.WARNING` | `⚠` | Completed with warnings |
| `StepStatus.SKIPPED` | `⊘` | Step was skipped |

### `LogPosition`

| Value | Description |
|---|---|
| `LogPosition.BELOW` | Logs render below the step label (default) |
| `LogPosition.ABOVE` | Logs render above the step label |

### `StepDefinition`

```python
StepDefinition(label, status=StepStatus.PENDING, step_description=None, sub_steps=None, parallel=False)
```

| Field | Type | Default | Description |
|---|---|---|---|
| `label` | `str` | required | Step label |
| `status` | `StepStatus` | `PENDING` | Initial status |
| `step_description` | `str \| None` | `None` | Secondary description line |
| `sub_steps` | `list[StepDefinition] \| None` | `None` | Nested children |
| `parallel` | `bool` | `False` | If True, creates a parallel group |

### `StepperTheme`

All fields have sensible defaults. Override any combination:

| Field | Type | Default |
|---|---|---|
| `completed_symbol` | `str` | `"●"` |
| `active_symbol` | `str` | `"◉"` |
| `pending_symbol` | `str` | `"○"` |
| `completed_style` | `str` | `"green"` |
| `active_style` | `str` | `"cyan bold"` |
| `pending_style` | `str` | `"bright_black"` |
| `spinner_name` | `str` | `"dots"` | Rich spinner name for ACTIVE steps |
| `spinner_speed` | `float` | `1.0` | Spinner animation speed multiplier |
| `failed_symbol` | `str` | `"✕"` | Symbol for FAILED steps |
| `failed_style` | `str` | `"red bold"` | Style for FAILED steps |
| `warning_symbol` | `str` | `"⚠"` | Symbol for WARNING steps |
| `warning_style` | `str` | `"yellow bold"` | Style for WARNING steps |
| `skipped_symbol` | `str` | `"⊘"` | Symbol for SKIPPED steps |
| `skipped_style` | `str` | `"bright_black"` | Style for SKIPPED steps |
| `tree_branch_mid` | `str` | `"├─"` | Tree branch for non-last children |
| `tree_branch_last` | `str` | `"└─"` | Tree branch for last child |
| `connector_symbol` | `str` | `"│"` |
| `connector_style` | `str` | `"bright_black"` |
| `line_thickness` | `int` | `1` |
| `step_gap` | `int` | `0` |
| `label_style` | `str` | `""` |
| `step_description_style` | `str` | `"dim"` |
| `label_padding` | `int` | `1` |
| `show_elapsed_time` | `bool` | `False` |
| `time_style` | `str` | `"progress.elapsed"` |
| `show_bar` | `bool` | `False` |
| `bar_width` | `int \| None` | `20` |
| `bar_complete_style` | `str` | `"bar.complete"` |
| `bar_finished_style` | `str` | `"bar.finished"` |
| `bar_pulse_style` | `str` | `"bar.pulse"` |
| `log_position` | `LogPosition` | `LogPosition.BELOW` |
| `max_log_rows` | `int \| None` | `None` |
| `log_style` | `str` | `"dim italic"` |
| `log_prefix` | `str` | `"›"` |

## Examples

The `examples/` directory contains 31 runnable scripts covering every feature:

| Example | Description |
|---|---|
| `01_basic` | Default theme with mixed statuses |
| `02_custom_colors` | Custom symbol and style colors |
| `03_emoji_symbols` | Emoji-based step indicators |
| `04_thick_connectors` | Multi-line connector glyphs |
| `05_step_gap` | Blank lines between steps |
| `06_all_completed` | All steps in completed state |
| `07_in_progress` | Partially completed workflow |
| `08_minimal_theme` | Stripped-down minimal appearance |
| `09_dense_layout` | Compact layout with descriptions |
| `10_many_steps` | Handling 10+ steps |
| `11_single_step` | Single-step edge case |
| `12_live_update` | Animated context manager usage |
| `13_elapsed_time` | Elapsed time column |
| `14_progress_bar` | Per-step progress bars |
| `15_step_logging` | Inline log messages |
| `16_full_featured` | Everything combined |
| `17_web_scraper` | Real-world web scraper demo |
| `18_spinner_basics` | Spinner animation with context manager |
| `19_spinner_gallery` | Multiple spinner types (dots, line, arrow, star, etc.) |
| `20_ci_pipeline` | CI/CD pipeline: dynamic steps, incremental progress |
| `21_file_operations` | File operations: incremental progress ticks, detailed logs |
| `22_data_pipeline` | ETL pipeline: pre-defined steps, Rich Panel summary |
| `23_api_health_check` | Health check: dynamic steps, error simulation |
| `24_package_installer` | Package installer: dependency logging, multi-stage progress |
| `25_database_migration` | Database migration: StepDefinition with splat unpacking |
| `26_devops_deploy` | Kubernetes deploy: StepDefinition with Rich Table |
| `27_spinner_speeds` | Spinner speed variations (0.3x to 4.0x) |
| `28_parallel_groups` | Parallel group creation and auto-derived status |
| `29_sub_steps` | Sequential sub-steps with tree rendering |
| `30_failed_warning_skipped` | FAILED/WARNING/SKIPPED status display |
| `31_log_position_above` | LogPosition.ABOVE with multi-step layout |

Run any example directly:

```bash
python examples/16_full_featured.py
```

## How It Works

`Stepper` extends Rich's `Progress` class with custom columns:

- **StepIndicatorColumn** — renders status symbols and vertical connectors
- **StepLabelColumn** — renders labels, descriptions, and inline logs
- **StepperTimeColumn** — renders elapsed/frozen time per step

Status mapping and log rendering are handled by shared `StatusMapper` and `LogRenderer` helpers for consistency across columns.

## License

[MIT](https://github.com/abbazs/rich-stepper/blob/main/LICENSE)
