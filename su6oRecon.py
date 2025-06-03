#!/usr/bin/env python3
"""
su6oRecon: A cross-platform CLI bug bounty reconnaissance tool.
"""
import os
import asyncio
import typer
from rich.console import Console
from rich.table import Table

from config_wizard import run_setup_wizard
from utils import (
    load_config,
    save_config,
    save_state,
    load_state,
    send_telegram,
    get_timestamp,
)
from modules.subdomain import run_subdomain_enumeration
from modules.http_probe import run_http_probe
from modules.screenshot import run_screenshot
from modules.portscan import run_port_scan
from modules.directory_scan import run_directory_scan
from modules.vulnscan import run_vulnerability_scan
from modules.param_finder import run_param_spider
from modules.takeover import run_subjack

app = typer.Typer()
console = Console()


def print_banner():
    banner = r"""
███████╗██╗   ██╗ ██████╗  ██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔════╝██║   ██║██╔════╝ ██╔═══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
███████╗██║   ██║███████╗ ██║   ██║██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
╚════██║██║   ██║██╔═══██╗██║   ██║██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
███████║╚██████╔╝╚██████╔╝╚██████╔╝██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                              
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print("[bold green]GitHub:[/bold green] https://github.com/su6osec")
    console.print(
        "[bold green]LinkedIn:[/bold green] https://www.linkedin.com/in/su6osec"
    )
    console.print()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    setup: bool = typer.Option(
        False, "--setup", help="Run the interactive setup wizard"
    ),
):
    """
    su6oRecon main entrypoint. Displays banner and handles setup or subcommands.
    """
    print_banner()
    if setup:
        run_setup_wizard()
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo("No command provided. Use --help for usage information.")
        raise typer.Exit()


@app.command()
def full(
    target: str = typer.Argument(
        ..., help="Target domain or IP for full reconnaissance"
    ),
    proxy: str = typer.Option(
        None, "--proxy", help="HTTP proxy (e.g. http://127.0.0.1:8080)"
    ),
    tor: bool = typer.Option(False, "--tor", help="Route traffic through Tor"),
    resume: bool = typer.Option(
        False, "--resume", help="Resume from last saved session"
    ),
    output: str = typer.Option(
        None, "--output", help="Custom prefix for report filenames"
    ),
):
    """
    Run the full recon pipeline on the target.
    """
    config = load_config()
    bot_token = config.get("telegram_bot_token")
    chat_id = config.get("telegram_chat_id")

    # Load or initialize session
    session = (
        load_state(target)
        if resume
        else {"target": target, "timestamp": get_timestamp(), "results": {}}
    )
    typer.secho(
        f"Starting full recon on [cyan]{target}[/cyan]...", fg=typer.colors.GREEN
    )
    if bot_token and chat_id:
        send_telegram(bot_token, chat_id, f"su6oRecon: Starting recon on {target}")

    # 1) Subdomain enumeration
    subdomains = run_subdomain_enumeration(target)
    session["results"]["subdomains"] = subdomains
    save_state(target, session)

    # 2) HTTP probing
    alive = run_http_probe(subdomains, proxy=proxy, tor=tor)
    session["results"]["alive_domains"] = alive
    save_state(target, session)

    # 3) Screenshot capture
    run_screenshot(alive)

    # 4) Port scanning
    port_results = run_port_scan(alive)
    session["results"]["port_scan"] = port_results
    save_state(target, session)

    # 5) Directory brute-forcing
    dir_results = run_directory_scan(alive)
    session["results"]["directory_scan"] = dir_results
    save_state(target, session)

    # 6) Vulnerability scanning (Nuclei)
    vuln_results = run_vulnerability_scan(alive)
    session["results"]["vulnerability_scan"] = vuln_results
    save_state(target, session)

    # 7) Parameter discovery
    params = run_param_spider(alive)
    session["results"]["parameters"] = params
    save_state(target, session)

    # 8) Subdomain takeover detection
    takeover_results = run_subjack(alive)
    session["results"]["takeover"] = takeover_results
    save_state(target, session)

    typer.secho("Recon pipeline completed.", fg=typer.colors.GREEN)
    if bot_token and chat_id:
        send_telegram(
            bot_token,
            chat_id,
            f"su6oRecon: Recon completed for {target}. Generating reports.",
        )

    from utils import generate_reports

    generate_reports(session, output_prefix=output)
    if bot_token and chat_id:
        send_telegram(bot_token, chat_id, f"su6oRecon: Reports generated for {target}.")


@app.command()
def subdomain(
    target: str = typer.Argument(..., help="Target domain for subdomain enumeration"),
    module: str = typer.Option(
        None, "--module", help="Specify 'assetfinder', 'subfinder', or 'amass'"
    ),
):
    """
    Run subdomain enumeration (assetfinder, subfinder, amass).
    """
    subdomains = run_subdomain_enumeration(target, module=module)
    table = Table(title=f"Subdomains for {target}", show_lines=True)
    table.add_column("Subdomain", style="cyan")
    for s in subdomains:
        table.add_row(s)
    console.print(table)
    # Save to file
    with open(f"{target}_subdomains.txt", "w") as f:
        for s in subdomains:
            f.write(s + "\n")
    typer.secho(f"Subdomains saved to {target}_subdomains.txt", fg=typer.colors.GREEN)


@app.command()
def httpx(
    target: str = typer.Argument(..., help="Domain or file of domains for HTTP probing")
):
    """
    Run httpx to check for alive hosts.
    """
    if os.path.isfile(target):
        with open(target) as f:
            domains = [line.strip() for line in f if line.strip()]
    else:
        domains = [target]
    alive = run_http_probe(domains)
    console.print("[green]Alive domains:[/green]")
    for url in alive:
        console.print(f" - {url}")
    with open("httpx_alive.txt", "w") as f:
        for url in alive:
            f.write(url + "\n")
    typer.secho(
        "HTTP probing complete. Results saved to httpx_alive.txt", fg=typer.colors.GREEN
    )


@app.command()
def screenshot(
    target: str = typer.Argument(..., help="Domain or file of domains for screenshots")
):
    """
    Capture screenshots for the given target(s) using gowitness.
    """
    if os.path.isfile(target):
        with open(target) as f:
            domains = [line.strip() for line in f if line.strip()]
    else:
        domains = [target]
    run_screenshot(domains)
    typer.secho(
        "Screenshots saved to './screenshots/' directory.", fg=typer.colors.GREEN
    )


@app.command()
def nmap(target: str = typer.Argument(..., help="Domain or IP for port scanning")):
    """
    Run nmap port scan with service detection.
    """
    run_port_scan([target])
    typer.secho("Nmap scan complete.", fg=typer.colors.GREEN)


@app.command()
def fuzz(target: str = typer.Argument(..., help="Domain for directory brute-forcing")):
    """
    Run ffuf directory brute-force on the given domain.
    """
    if os.path.isfile(target):
        with open(target) as f:
            domains = [line.strip() for line in f if line.strip()]
    else:
        domains = [target]
    run_directory_scan(domains)
    typer.secho("Directory brute-forcing complete.", fg=typer.colors.GREEN)


@app.command()
def nuclei(
    target: str = typer.Argument(..., help="Domain or file for vulnerability scanning")
):
    """
    Run Nuclei vulnerability scanning on the given target(s).
    """
    if os.path.isfile(target):
        with open(target) as f:
            domains = [line.strip() for line in f if line.strip()]
    else:
        domains = [target]
    run_vulnerability_scan(domains)
    typer.secho("Nuclei scanning complete.", fg=typer.colors.GREEN)


@app.command()
def params(target: str = typer.Argument(..., help="Domain for parameter discovery")):
    """
    Run ParamSpider on the given target domain.
    """
    run_param_spider([target])
    typer.secho("ParamSpider scan complete.", fg=typer.colors.GREEN)


@app.command()
def takeover(
    target: str = typer.Argument(
        ..., help="Domain or file of subdomains for takeover check"
    )
):
    """
    Run Subjack on the given target(s).
    """
    if os.path.isfile(target):
        with open(target) as f:
            domains = [line.strip() for line in f if line.strip()]
    else:
        domains = [target]
    run_subjack(domains)
    typer.secho("Subjack scan complete.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
