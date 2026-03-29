"""Live web scraper — visits 5 websites, extracts data, uses all stepper features."""

import re
import urllib.request
import urllib.error

from rich.console import Console
from rich.table import Table

from stepper import StepStatus, Stepper, StepperTheme

SITES = [
    ("https://httpbin.org/get", "Fetch GET"),
    ("https://httpbin.org/headers", "Fetch Headers"),
    ("https://httpbin.org/user-agent", "Fetch User-Agent"),
    ("https://httpbin.org/ip", "Fetch IP"),
    ("https://httpbin.org/uuid", "Fetch UUID"),
]

theme = StepperTheme(
    completed_style="green bold",
    active_style="cyan bold",
    pending_style="bright_black",
    connector_style="bright_black",
    show_elapsed_time=True,
    show_bar=True,
    bar_width=20,
    max_log_rows=4,
    log_style="dim italic",
    log_prefix=">",
    completed_symbol="[ok]",
    active_symbol="[>>]",
    pending_symbol="[  ]",
)

console = Console()
results: list[dict[str, str]] = []

with Stepper(console=console, theme=theme) as stepper:
    for url, label in SITES:
        idx = stepper.add_step(label, status=StepStatus.ACTIVE, step_description=url)
        stepper.log(idx, f"GET {url}")
        stepper.set_step_progress(idx, 0.1)

        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "stepper-demo/1.0"}
            )
            stepper.log(idx, "Sending request...")
            stepper.set_step_progress(idx, 0.3)

            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                status_code = resp.status
                length = len(body)

            stepper.set_step_progress(idx, 0.7)
            stepper.log(idx, f"Status {status_code}, {length:,} bytes")

            snippet = body.strip()[:120].replace("\n", " ")
            stepper.log(idx, f"Body: {snippet}...")
            stepper.set_step_progress(idx, 1.0)

            uuid_match = re.search(r'"uuid"\s*:\s*"([^"]+)"', body)
            ip_match = re.search(r'"origin"\s*:\s*"([^"]+)"', body)
            ua_match = re.search(r'"user-agent"\s*:\s*"([^"]+)"', body)

            detail = (
                uuid_match.group(1)
                if uuid_match
                else ip_match.group(1)
                if ip_match
                else ua_match.group(1)[:40]
                if ua_match
                else snippet[:30]
            )

            results.append(
                {
                    "site": label,
                    "status": str(status_code),
                    "size": f"{length:,}B",
                    "detail": detail,
                }
            )
            stepper.log(idx, "Done")

        except urllib.error.URLError as e:
            stepper.log(idx, f"Error: {e.reason}")
            results.append(
                {
                    "site": label,
                    "status": "FAIL",
                    "size": "-",
                    "detail": str(e.reason)[:40],
                }
            )

        stepper.set_step_status(idx, StepStatus.COMPLETED)

console.print()
table = Table(title="Scraped Data", show_header=True, header_style="bold magenta")
table.add_column("Site", style="cyan")
table.add_column("Status", justify="center")
table.add_column("Size", justify="right", style="green")
table.add_column("Detail", style="dim")

for r in results:
    style = "green" if r["status"] != "FAIL" else "red"
    table.add_row(
        r["site"], f"[{style}]{r['status']}[/{style}]", r["size"], r["detail"]
    )

console.print(table)
