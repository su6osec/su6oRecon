"""
Port scanning module using nmap.
"""

import subprocess
from rich import print


def run_port_scan(targets):
    """
    Run nmap port scan (service detection) on target hosts.
    """
    results = {}
    for target in targets:
        print(f"[yellow]Running nmap on {target}...[/yellow]")
        try:
            output_file = f"nmap_{target}.txt"
            subprocess.run(["nmap", "-sV", "-oN", output_file, target], check=True)
            with open(output_file) as f:
                data = f.read()
            results[target] = data
        except FileNotFoundError:
            print("[red]Error:[/red] nmap not found. Please install it.")
            break
        except subprocess.CalledProcessError:
            print(f"[red]nmap scan failed on {target}[/red]")
    return results