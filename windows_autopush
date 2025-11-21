import os
import subprocess
from datetime import datetime
import string
import logging
from ctypes import windll
import smtplib
import ssl
import requests

# ================================================
# 🔐 NOTIFICATION CREDENTIALS (FILL THESE)
# ================================================

# Telegram
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# Discord Webhook
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

# Email (SMTP)
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASS = "your_app_password"
TO_EMAIL = "recipient_email@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ================================================
# General Configuration
# ================================================
BRANCH = "main"
LOG_FILE = os.path.expanduser("git_auto_push.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")
log = logging.info

# ================================================
# Notification Functions
# ================================================

def notify_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        log(f"Telegram notification error: {e}")


def notify_discord(message):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        log(f"Discord notification error: {e}")


def notify_email(subject, body):
    if not EMAIL_USER or not EMAIL_PASS:
        return
    try:
        msg = f"Subject: {subject}\n\n{body}"
        context = ssl.create_default_context()

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, TO_EMAIL, msg)
    except Exception as e:
        log(f"Email error: {e}")


def notify_all(message):
    log(message)
    notify_telegram(message)
    notify_discord(message)
    notify_email("Git Auto Push Report", message)

# ================================================
# Git Functions
# ================================================

def show_git_credentials():
    notify_all("=== Showing Git Credential Configuration ===")

    def run_cmd(label, cmd):
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            notify_all(f"--- {label} ---\n{result.stdout.strip()}")
        except Exception as e:
            notify_all(f"Error fetching {label}: {e}")

    run_cmd("Global Config", ["git", "config", "--global", "--list"])
    run_cmd("System Config", ["git", "config", "--system", "--list"])
    run_cmd("Local Config", ["git", "config", "--local", "--list"])
    notify_all("=== End Git Config ===")


def get_available_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1 and letter != 'C':
            drives.append(f"{letter}:\\")
        bitmask >>= 1
    return drives


def has_changes(path):
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip() != ""
    except:
        return False


def commit_and_push(path):
    notify_all(f"→ Checking repo: {path}")

    try:
        # Validate remote repo
        remote_result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if "fatal" in remote_result.stderr.lower():
            notify_all(f"✘ Invalid or missing remote in {path}. Skipping.")
            return

        # Commit + Push
        if has_changes(path):
            subprocess.run(["git", "add", "."], cwd=path, check=True)
            subprocess.run(["git", "commit", "-m", f"Auto commit on {datetime.now()}"], cwd=path, check=True)

            push = subprocess.run(
                ["git", "push", "origin", BRANCH],
                cwd=path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if push.returncode != 0:
                notify_all(f"✘ Push failed in {path}:\n{push.stderr}")
            else:
                notify_all(f"✔ Pushed changes from {path}")
        else:
            notify_all(f"✓ No changes in {path}")

    except Exception as e:
        notify_all(f"✘ Error in {path}: {e}")


def scan_drive(drive):
    notify_all(f"🔍 Scanning drive: {drive}")
    for root, dirs, files in os.walk(drive):
        if ".git" in dirs:
            commit_and_push(root)
            dirs.clear()


def main():
    notify_all("===== Git Auto Push Started =====")
    show_git_credentials()

    for drive in get_available_drives():
        scan_drive(drive)

    notify_all("===== Execution Completed =====")


if __name__ == "__main__":
    main()
