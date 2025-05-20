"""
Interactive setup wizard for su6oRecon.
"""

from rich import print
from rich.prompt import Prompt
from utils import save_config


def run_setup_wizard():
    print("[bold magenta]Welcome to su6oRecon Setup Wizard![/bold magenta]")
    print("Let's configure su6oRecon.")
    config = {}
    use_telegram = Prompt.ask(
        "Enable Telegram notifications?", choices=["y", "n"], default="n"
    )
    if use_telegram.lower() == "y":
        bot_token = Prompt.ask("Enter your Telegram Bot Token (BotFather)")
        chat_id = Prompt.ask("Enter your Telegram Chat ID")
        config["telegram_bot_token"] = bot_token.strip()
        config["telegram_chat_id"] = chat_id.strip()
    else:
        print("Skipping Telegram setup. You can configure it later via config.")
    save_config(config)
    print("[green]Setup complete![/green] Your configuration has been saved.")