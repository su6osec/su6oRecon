"""
Screenshot module using gowitness to capture screenshots of domains.
"""

import subprocess
from rich import print


def run_screenshot(domains):
    """
    Run gowitness screenshot for each domain.
    """
    output_dir = "screenshots"
    try:
        subprocess.run(["mkdir", "-p", output_dir], check=True)
    except Exception:
        pass
    for domain in domains:
        url = f"http://{domain}"
        print(f"[yellow]Capturing screenshot of {url}...[/yellow]")
        try:
            subprocess.run(
                ["gowitness", "single", "--url", url, "--destination", output_dir],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            print("[red]Error:[/red] gowitness not found. Please install it.")
            return
        except subprocess.CalledProcessError as e:
            print(
                f"[red]gowitness failed for {domain}:[/red] {e.stderr.decode().strip()}"
            )