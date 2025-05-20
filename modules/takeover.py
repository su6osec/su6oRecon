"""
Subdomain takeover detection using subjack.
"""

import subprocess
from rich import print


def run_subjack(targets, timeout=30):
    """
    Run subjack to detect subdomain takeover.
    """
    results = {}
    temp_file = "subjack_targets.txt"
    with open(temp_file, "w") as f:
        for target in targets:
            f.write(target + "\n")
    print("[yellow]Running subjack...[/yellow]")
    output_file = "subjack_results.txt"
    try:
        subprocess.run(
            [
                "subjack",
                "-w",
                temp_file,
                "-t",
                "50",
                "-timeout",
                str(timeout),
                "-o",
                output_file,
            ],
            check=True,
        )
        with open(output_file) as f:
            data = f.read().splitlines()
        results["vulnerabilities"] = data
    except FileNotFoundError:
        print("[red]Error:[/red] subjack not found. Please install it.")
    except subprocess.CalledProcessError:
        print("[red]subjack scan failed[/red]")
    return results