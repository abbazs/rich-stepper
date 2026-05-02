"""Parallel Groups — create parallel groups with auto-derived status."""

from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper

# Create a stepper with a parallel group and a regular step.
console = Console()
stepper = Stepper(console=console, auto_refresh=False)

# Regular step
stepper.add_step("Initialize", status=StepStatus.COMPLETED, step_description="Done in 0.3s")

# Parallel group with 3 children
group = stepper.add_parallel_group("Run Tests", step_description="3 test suites")
stepper.add_parallel_step(group, "Unit Tests", status=StepStatus.COMPLETED)
stepper.add_parallel_step(group, "Integration Tests", status=StepStatus.FAILED)
stepper.add_parallel_step(group, "E2E Tests", status=StepStatus.SKIPPED)

# Final step
stepper.add_step("Deploy", status=StepStatus.PENDING, step_description="Waiting for tests")

# Group status auto-derived: FAILED (because one child failed, none active)
Console().print(stepper)
