"""
Auto-installer for external tools and dependencies.
"""

import platform
import subprocess
import shutil

TOOLS = {
    "assetfinder": "github.com/tomnomnom/assetfinder",
    "subfinder": "github.com/projectdiscovery/subfinder/v2/cmd/subfinder",
    "amass": "golang.org/x/tools/cmd/goimports (amass might require manual install)",
    "httpx": "github.com/projectdiscovery/httpx/cmd/httpx",
    "nmap": "system package (apt/brew)",
    "ffuf": "github.com/ffuf/ffuf",
    "gowitness": "github.com/sensepost/gowitness",
    "paramspider": "pip install paramspider or go to its repo",
    "subjack": "github.com/haccer/subjack",
    "nuclei": "github.com/projectdiscovery/nuclei/v2/cmd/nuclei",
}


def main():
    os_name = platform.system()
    print(f"Detected OS: {os_name}")
    # Install system packages
    if os_name == "Linux":
        if shutil.which("apt"):
            subprocess.run(["sudo", "apt", "update"])
            subprocess.run(["sudo", "apt", "install", "-y", "nmap", "git", "golang-go"])
        elif shutil.which("pacman"):
            subprocess.run(
                ["sudo", "pacman", "-Sy", "--noconfirm", "nmap", "git", "go"]
            )
    elif os_name == "Darwin":
        if shutil.which("brew"):
            subprocess.run(["brew", "install", "nmap", "git", "go"])

    # Install Go-based tools
    for tool, repo in TOOLS.items():
        if shutil.which(tool):
            print(f"{tool} is already installed.")
        else:
            print(f"Installing {tool}...")
            if repo.startswith("github.com"):
                try:
                    subprocess.run(["go", "install", f"{repo}@latest"], check=True)
                except Exception as e:
                    print(f"Failed to install {tool}: {e}")
            elif tool == "paramspider":
                try:
                    subprocess.run(["pip", "install", "paramspider"], check=True)
                except Exception as e:
                    print(f"Failed to install paramspider: {e}")
    print("Installation complete. Ensure your GO bin directory is in PATH.")


if __name__ == "__main__":
    main()