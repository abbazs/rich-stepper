from __future__ import annotations

from dataclasses import dataclass

from stepper.types import LogPosition, StepStatus


@dataclass(frozen=True)
class StepperTheme:
    completed_symbol: str = "●"
    active_symbol: str = "◉"
    pending_symbol: str = "○"
    completed_style: str = "green"
    active_style: str = "cyan bold"
    spinner_name: str = "dots"
    spinner_speed: float = 1.0
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
    log_position: LogPosition = LogPosition.BELOW
    max_log_rows: int | None = None
    log_style: str = "dim italic"
    log_prefix: str = "›"
    failed_symbol: str = "✕"
    warning_symbol: str = "⚠"
    skipped_symbol: str = "⊘"
    failed_style: str = "red bold"
    warning_style: str = "yellow bold"
    skipped_style: str = "bright_black"
    tree_branch_mid: str = "├─"
    tree_branch_last: str = "└─"

    def connector_glyph(self) -> str:
        thickness = max(1, self.line_thickness)
        return self.connector_symbol * thickness
