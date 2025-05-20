"""
Subdomain enumeration module integrating assetfinder, subfinder, and amass.
"""

import asyncio
import subprocess
from rich import print


async def run_assetfinder(domain):
    print(f"[yellow]Running assetfinder for {domain}...[/yellow]")
    try:
        proc = await asyncio.create_subprocess_exec(
            "assetfinder",
            "--subs-only",
            domain,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stderr:
            print(f"[red]assetfinder error:[/red] {stderr.decode().strip()}")
        subs = stdout.decode().split()
        return subs
    except FileNotFoundError:
        print("[red]Error:[/red] assetfinder not found. Please install it.")
        return []


async def run_subfinder(domain):
    print(f"[yellow]Running subfinder for {domain}...[/yellow]")
    try:
        proc = await asyncio.create_subprocess_exec(
            "subfinder",
            "-d",
            domain,
            "-silent",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stderr:
            print(f"[red]subfinder error:[/red] {stderr.decode().strip()}")
        subs = stdout.decode().split()
        return subs
    except FileNotFoundError:
        print("[red]Error:[/red] subfinder not found. Please install it.")
        return []


async def run_amass(domain):
    print(f"[yellow]Running amass for {domain}...[/yellow]")
    try:
        proc = await asyncio.create_subprocess_exec(
            "amass",
            "enum",
            "-d",
            domain,
            "-passive",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stderr:
            print(f"[red]amass error:[/red] {stderr.decode().strip()}")
        subs = stdout.decode().split()
        return subs
    except FileNotFoundError:
        print("[red]Error:[/red] amass not found. Please install it.")
        return []


def run_subdomain_enumeration(domain, proxy=None, tor=False, module=None):
    """
    Run subdomain enumeration using assetfinder, subfinder, and amass.
    If module is specified, run only that tool.
    Returns a deduplicated list of subdomains.
    """
    loop = asyncio.get_event_loop()
    tasks = []
    if module == "assetfinder" or module is None:
        tasks.append(run_assetfinder(domain))
    if module == "subfinder" or module is None:
        tasks.append(run_subfinder(domain))
    if module == "amass" or module is None:
        tasks.append(run_amass(domain))
    if not tasks:
        print("[red]No valid subdomain module selected.[/red]")
        return []
    results = loop.run_until_complete(asyncio.gather(*tasks))
    subdomains = set()
    for res in results:
        for sub in res:
            sub = sub.strip()
            if sub:
                subdomains.add(sub)
    return sorted(subdomains)