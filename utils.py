import os
import json
from datetime import datetime
import requests
from cryptography.fernet import Fernet
from fpdf import FPDF


def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ---------- Configuration Handling (Encrypted) ----------


def load_config():
    """
    Load encrypted configuration from config/config.enc using key in config/key.key.
    Returns a dict or empty if not found.
    """
    key_path = os.path.join("config", "key.key")
    enc_path = os.path.join("config", "config.enc")
    if not os.path.exists(key_path) or not os.path.exists(enc_path):
        print("Config not found. Please run `su6oRecon --setup` first.")
        return {}
    with open(key_path, "rb") as f:
        key = f.read()
    fernet = Fernet(key)
    with open(enc_path, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = fernet.decrypt(encrypted)
        config = json.loads(decrypted.decode())
        return config
    except Exception as e:
        print(f"Failed to decrypt config: {e}")
        return {}


def save_config(config_data):
    """
    Encrypt and save configuration dict to config/config.enc.
    """
    os.makedirs("config", exist_ok=True)
    key_path = os.path.join("config", "key.key")
    enc_path = os.path.join("config", "config.enc")
    # Generate key if not exists
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(key)
    else:
        with open(key_path, "rb") as f:
            key = f.read()
    fernet = Fernet(key)
    data = json.dumps(config_data).encode()
    encrypted = fernet.encrypt(data)
    with open(enc_path, "wb") as f:
        f.write(encrypted)


# ---------- Session State Saving/Loading ----------


def save_state(target, state):
    """
    Save session state to sessions/<target>_session.json.
    """
    os.makedirs("sessions", exist_ok=True)
    filename = os.path.join("sessions", f"{target}_session.json")
    with open(filename, "w") as f:
        json.dump(state, f, indent=2)


def load_state(target):
    """
    Load session state from sessions/<target>_session.json.
    """
    filename = os.path.join("sessions", f"{target}_session.json")
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    else:
        return None


# ---------- Telegram Messaging ----------


def send_telegram(bot_token, chat_id, message):
    """
    Send a message via Telegram Bot API.
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {"chat_id": chat_id, "text": message}
        requests.get(url, params=params)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


# ---------- Report Generation ----------


def generate_reports(session, output_prefix=None):
    """
    Generate reports in PDF, HTML, JSON, TXT, and CSV formats using session data.
    Reports are saved under the 'reports/' directory.
    """
    target = session.get("target")
    timestamp = session.get("timestamp", get_timestamp())
    results = session.get("results", {})

    os.makedirs("reports", exist_ok=True)
    prefix = output_prefix or f"{target}_recon_{timestamp}"

    # JSON report
    json_path = os.path.join("reports", prefix + ".json")
    with open(json_path, "w") as f:
        json.dump(session, f, indent=2)

    # TXT report
    txt_path = os.path.join("reports", prefix + ".txt")
    with open(txt_path, "w") as f:
        f.write(f"Report for {target} - {timestamp}\n\n")
        for key, value in results.items():
            f.write(f"=== {key.upper()} ===\n")
            if isinstance(value, list):
                for item in value:
                    f.write(str(item) + "\n")
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    f.write(f"{subkey}: {subvalue}\n")
            else:
                f.write(str(value) + "\n")
            f.write("\n")

    # CSV reports (one per section)
    for key, value in results.items():
        csv_path = os.path.join("reports", f"{prefix}_{key}.csv")
        with open(csv_path, "w") as f:
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, (list, dict)):
                        f.write(json.dumps(item) + "\n")
                    else:
                        f.write(str(item) + "\n")
            elif isinstance(value, dict):
                f.write("Key,Value\n")
                for subkey, subvalue in value.items():
                    f.write(f"{subkey},{subvalue}\n")
            else:
                f.write(str(value) + "\n")

    # HTML report
    html_path = os.path.join("reports", prefix + ".html")
    logo_path = os.path.join("assets", "logo.jpeg")
    logo_tag = ""
    if os.path.exists(logo_path):
        # Adjust path for HTML
        logo_tag = (
            f'<img src="../assets/logo.jpeg" alt="Logo" style="max-width:200px;"><br>'
        )
    html_content = f"""
<html><head><title>su6oRecon Report - {target}</title></head><body>
{logo_tag}
<h1>su6oRecon Report for {target}</h1>
<p><strong>Generated:</strong> {timestamp}</p>
"""
    for key, value in results.items():
        html_content += f"<h2>{key.capitalize()}</h2>\n<ul>"
        if isinstance(value, list):
            for item in value:
                html_content += f"<li>{item}</li>"
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                html_content += f"<li><strong>{subkey}:</strong> {subvalue}</li>"
        else:
            html_content += f"<li>{value}</li>"
        html_content += "</ul>\n"
    html_content += "</body></html>"
    with open(html_path, "w") as f:
        f.write(html_content)

    # PDF report using FPDF
    pdf_path = os.path.join("reports", prefix + ".pdf")
    pdf = FPDF()
    pdf.add_page()
    # Logo
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"su6oRecon Report for {target}", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated: {timestamp}", ln=1)
    pdf.ln(5)
    for key, value in results.items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, key.capitalize(), ln=1)
        pdf.set_font("Arial", "", 12)
        if isinstance(value, list):
            for item in value:
                pdf.multi_cell(0, 8, str(item))
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                pdf.multi_cell(0, 8, f"{subkey}: {subvalue}")
        else:
            pdf.multi_cell(0, 8, str(value))
        pdf.ln(3)
    pdf.output(pdf_path)