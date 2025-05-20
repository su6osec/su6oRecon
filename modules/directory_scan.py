"""
Directory brute-forcing module using ffuf.
"""

import subprocess
from rich import print


def run_directory_scan(targets, wordlist=None):
    """
    Run ffuf on given targets to brute-force directories.
    """
    results = {}
    if not wordlist:
        wordlist = "assets/common_wordlist.txt"
    for target in targets:
        print(f"[yellow]Running ffuf on {target}...[/yellow]")
        output_file = f"ffuf_{target}.txt"
        try:
            subprocess.run(
                [
                    "ffuf",
                    "-u",
                    f"http://{target}/FUZZ",
                    "-w",
                    wordlist,
                    "-o",
                    output_file,
                ],
                check=True,
            )
            with open(output_file) as f:
                data = f.read().splitlines()
            results[target] = data
        except FileNotFoundError:
            print("[red]Error:[/red] ffuf not found. Please install it.")
            break
        except subprocess.CalledProcessError:
            print(f"[red]ffuf scan failed on {target}[/red]")
    return results