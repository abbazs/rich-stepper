from __future__ import annotations

from dataclasses import dataclass

from stepper.types import StepStatus


@dataclass(frozen=True)
class StepperTheme:
    completed_symbol: str = "●"
    active_symbol: str = "◉"
    pending_symbol: str = "○"
    completed_style: str = "green"
    active_style: str = "cyan bold"
    pending_style: str = "bright_black"
    connector_symbol: str = "│"
    connector_style: str = "bright_black"
    line_thickness: int = 1
    step_gap: int = 0
    label_style: str = ""
    step_description_style: str = "dim"
    label_padding: int = 1
    show_elapsed_time: bool = False
    time_style: str = "progress.elapsed"
    show_bar: bool = False
    bar_width: int | None = 20
    bar_complete_style: str = "bar.complete"
    bar_finished_style: str = "bar.finished"
    bar_pulse_style: str = "bar.pulse"
    log_position: str = "below"
    max_log_rows: int | None = None
    log_style: str = "dim italic"
    log_prefix: str = "›"

    def connector_glyph(self) -> str:
        thickness = max(1, self.line_thickness)
        return self.connector_symbol * thickness
