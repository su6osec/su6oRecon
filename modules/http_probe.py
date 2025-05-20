"""
HTTP probing module using httpx to find alive domains.
"""

import subprocess
from rich import print


def run_http_probe(domains, proxy=None, tor=False):
    """
    Run httpx on a list of domains to probe HTTP services.
    Returns a list of alive domains/URLs.
    """
    alive = []
    cmd = ["httpx", "-silent"]
    if proxy:
        cmd.extend(["-proxy", proxy])
    if tor:
        cmd.extend(["-proxy", "socks5://127.0.0.1:9050"])
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        print("[red]Error:[/red] httpx not found. Please install it.")
        return alive
    input_data = "\n".join(domains)
    stdout, stderr = proc.communicate(input=input_data)
    if stderr:
        print(f"[red]httpx error:[/red] {stderr.strip()}")
    for line in stdout.splitlines():
        line = line.strip()
        if line:
            alive.append(line)
    return alive