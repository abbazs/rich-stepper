from rich.console import Console

from stepper import StepDefinition, StepStatus, Stepper, StepperTheme


def main() -> None:
    steps = [
        StepDefinition("Collect requirements", StepStatus.COMPLETED),
        StepDefinition(
            "Design UI", StepStatus.ACTIVE, step_description="Define layout and styles"
        ),
        StepDefinition("Implement component", StepStatus.PENDING),
        StepDefinition(
            "Verify output", StepStatus.PENDING, step_description="Run tests and review"
        ),
    ]
    theme = StepperTheme(
        completed_style="green bold",
        active_style="magenta bold",
        pending_style="bright_black",
        connector_style="bright_black",
        line_thickness=1,
        label_padding=2,
        show_elapsed_time=True,
        show_bar=True,
        bar_width=20,
        max_log_rows=3,
        log_style="dim italic",
        log_prefix="›",
    )
    stepper = Stepper(steps=steps, theme=theme, auto_refresh=False)
    stepper.set_step_progress(1, 0.45)
    stepper.log(0, "Stakeholder interview complete")
    stepper.log(1, "Sketching wireframes…")
    stepper.log(1, "Choosing color palette")
    stepper.log(1, "Typography selection")
    Console().print(stepper)


if __name__ == "__main__":
    main()
