# v0.3.0 — API Polish + Docs Catch-up

## New Features

### Semantic Convenience Methods

Four new methods that combine status change + optional description update in a single call:

```python
stepper.succeed(idx, description="200 OK")          # → COMPLETED
stepper.fail(idx, description="Connection refused")  # → FAILED
stepper.warn(idx, description="Deprecated API")      # → WARNING
stepper.skip(idx, description="Already up-to-date")  # → SKIPPED
```

### Lifecycle Callbacks

Hook into status transitions with optional callbacks:

```python
stepper = Stepper(
    steps=steps,
    on_step_start=lambda idx, label: print(f"Starting {label}"),
    on_step_complete=lambda idx, label: log_metric(label),
    on_step_fail=lambda idx, label, desc: send_alert(label, desc),
)
```

Callbacks fire synchronously when `set_step_status()` or any convenience method transitions a step.

## Documentation

- **README overhaul**: Updated StepStatus table (now 6 statuses), API reference (13 methods including `add_parallel_group`, `add_sub_step`, convenience methods), StepperTheme table (10 new fields), examples table (now 31 examples), and added Lifecycle Callbacks section.
- **4 new examples**: parallel groups (28), sub-steps (29), failed/warning/skipped statuses (30), log position above (31).

## CI/CD

- Added GitHub Actions workflow running `pytest` + `pyright` on Python 3.10–3.14.

## Full Changelog

- `feat(stepper): add semantic convenience methods succeed/fail/warn/skip`
- `feat(stepper): add lifecycle callbacks on_step_start/on_step_complete/on_step_fail`
- `docs(examples): add parallel groups example (28)`
- `docs(examples): add sub-steps example (29)`
- `docs(examples): add failed/warning/skipped statuses example (30)`
- `docs(examples): add log position above example (31)`
- `ci: add GitHub Actions workflow for pytest + pyright on Python 3.10-3.14`
- `docs(readme): overhaul — add missing statuses, API methods, theme fields, examples, callbacks`
