"""File Operations — simulate file processing with spinners and progress."""

import hashlib
import time

from stepper import StepStatus, Stepper, StepperTheme

FILE_COUNT = 10
FAKE_DATA = b"stepper-demo-file-content-" * 100

theme = StepperTheme(
    spinner_name="dots2",
    spinner_speed=1.5,
    active_style="magenta",
    show_elapsed_time=True,
    show_bar=True,
    bar_width=20,
    max_log_rows=3,
    log_prefix="›",
)

OPERATIONS = [
    ("Reading source", "Scanning input directory…"),
    ("Validating files", "Checking file integrity…"),
    ("Compressing data", "Applying gzip compression…"),
    ("Encrypting output", "AES-256 encryption…"),
    ("Writing destination", "Writing to output/…"),
    ("Verifying integrity", "SHA-256 checksum verification…"),
]

stepper = Stepper(theme=theme)
with stepper:
    for op_name, op_desc in OPERATIONS:
        idx = stepper.add_step(
            op_name, status=StepStatus.ACTIVE, step_description=op_desc
        )

        if op_name == "Reading source":
            for i in range(FILE_COUNT):
                time.sleep(0.05)
                stepper.set_step_progress(idx, (i + 1) / FILE_COUNT)
                stepper.log(idx, f"Reading file {i + 1}/{FILE_COUNT}…")
            stepper.log(
                idx, f"Read {FILE_COUNT} files ({len(FAKE_DATA) * FILE_COUNT:,} bytes)"
            )

        elif op_name == "Compressing data":
            for pct in (25, 50, 75, 100):
                time.sleep(0.15)
                stepper.set_step_progress(idx, pct / 100)
                stepper.log(idx, f"Compression: {pct}% — ratio: {67 + pct // 10}%")
            stepper.log(
                idx, f"Compressed to {len(FAKE_DATA) * FILE_COUNT // 3:,} bytes"
            )

        elif op_name == "Verifying integrity":
            checksum = hashlib.sha256(FAKE_DATA).hexdigest()[:16]
            time.sleep(0.3)
            stepper.set_step_progress(idx, 0.5)
            stepper.log(idx, f"Computing SHA-256: {checksum}…")
            time.sleep(0.3)
            stepper.set_step_progress(idx, 1.0)
            stepper.log(idx, f"Checksum verified: {checksum}")
        else:
            for tick in range(4):
                time.sleep(0.12)
                stepper.set_step_progress(idx, (tick + 1) / 4)
            stepper.log(idx, f"{op_name} complete")

        stepper.set_step_status(idx, StepStatus.COMPLETED)
