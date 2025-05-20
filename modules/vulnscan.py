"""
Vulnerability scanning module using Nuclei.
"""

import subprocess
from rich import print


def run_vulnerability_scan(targets, templates=None):
    """
    Run Nuclei scanning on given targets.
    """
    results = {}
    nuclei_templates = templates or "/path/to/nuclei-templates"
    for target in targets:
        print(f"[yellow]Running Nuclei on {target}...[/yellow]")
        output_file = f"nuclei_{target}.txt"
        try:
            subprocess.run(
                [
                    "nuclei",
                    "-u",
                    f"http://{target}",
                    "-o",
                    output_file,
                    "-t",
                    nuclei_templates,
                ],
                check=True,
            )
            with open(output_file) as f:
                data = f.read().splitlines()
            results[target] = data
        except FileNotFoundError:
            print("[red]Error:[/red] nuclei not found. Please install it.")
            break
        except subprocess.CalledProcessError:
            print(f"[red]Nuclei scan failed on {target}[/red]")
    return results