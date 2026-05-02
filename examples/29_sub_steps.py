"""Sub-Steps — sequential children under a regular step with tree rendering."""

from rich.console import Console

from stepper import StepStatus, Stepper

console = Console()
stepper = Stepper(console=console, auto_refresh=False)

# Build step with sub-steps
build_idx = stepper.add_step("Build", status=StepStatus.COMPLETED, step_description="All targets built")
stepper.add_sub_step(build_idx, "Compile source", status=StepStatus.COMPLETED)
stepper.add_sub_step(build_idx, "Link binaries", status=StepStatus.COMPLETED)
stepper.add_sub_step(build_idx, "Generate docs", status=StepStatus.SKIPPED)

# Deploy step with sub-steps (in progress)
deploy_idx = stepper.add_step("Deploy", status=StepStatus.ACTIVE, step_description="2 of 3 complete")
stepper.add_sub_step(deploy_idx, "Stage environment", status=StepStatus.COMPLETED)
stepper.add_sub_step(deploy_idx, "Run migrations", status=StepStatus.COMPLETED)
stepper.add_sub_step(deploy_idx, "Health check", status=StepStatus.ACTIVE)

# Pending step
stepper.add_step("Notify", status=StepStatus.PENDING, step_description="Slack + email")

Console().print(stepper)
