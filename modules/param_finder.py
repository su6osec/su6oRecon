"""
Parameter discovery module using ParamSpider.
"""

import subprocess
from rich import print


def run_param_spider(targets):
    """
    Run ParamSpider for each target domain to find parameters.
    """
    results = {}
    for target in targets:
        print(f"[yellow]Running ParamSpider on {target}...[/yellow]")
        output_file = f"params_{target}.txt"
        try:
            subprocess.run(
                ["paramspider", "--domain", target, "--output", output_file], check=True
            )
            with open(output_file) as f:
                data = f.read().splitlines()
            results[target] = data
        except FileNotFoundError:
            print("[red]Error:[/red] ParamSpider not found. Please install it.")
            break
        except subprocess.CalledProcessError:
            print(f"[red]ParamSpider failed on {target}[/red]")
    return results