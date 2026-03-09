import os
import subprocess
from datetime import datetime
import string
import logging
from ctypes import windll

# Configuration
BRANCH = "main"
LOG_FILE = os.path.expanduser("git_auto_push.log")

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")
log = logging.info


def show_git_credentials():
    """Show git credential configuration before starting execution"""
    log("=== Showing Git Configuration ===")

    def run_cmd(label, cmd_list):
        try:
            result = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            log(f"--- {label} ---")
            log(result.stdout.strip() or "(No output)")
        except Exception as e:
            log(f"Error fetching {label}: {e}")

    run_cmd("Global Git Config", ["git", "config", "--global", "--list"])
    run_cmd("System Git Config", ["git", "config", "--system", "--list"])
    run_cmd("Local Git Config (may fail if no repo)", ["git", "config", "--local", "--list"])

    log("=== End Git Configuration ===\n")


def get_available_drives():
    """Return a list of available drive letters excluding C:\\ (system drive)"""
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            if letter != 'C':  # Skip system drive
                drives.append(f"{letter}:\\")
        bitmask >>= 1
    return drives


def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))


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
    except Exception as e:
        log(f"Error checking changes in {path}: {e}")
        return False


def commit_and_push(path):
    try:
        log(f"→ Checking repo: {path}")

        # Verify remote exists
        remote_result = subprocess.run(
            ["git", "remote", "-v"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if "fatal" in remote_result.stderr.lower():
            log(f"✘ Invalid or missing remote in {path}. Skipping.")
            return

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
                log(f"✘ Push failed in {path}: {push.stderr}")
            else:
                log(f"✔ Changes pushed from {path}")

        else:
            log(f"✓ No changes in {path}")

    except Exception as e:
        log(f"✘ Error in {path}: {e}")


def scan_drive(drive):
    log(f"🔍 Scanning drive: {drive}")
    for root, dirs, _ in os.walk(drive):
        if ".git" in dirs:
            commit_and_push(root)
            dirs.clear()  # Do not go deeper inside the repo


def main():
    log("===== Windows Git Auto Push Started =====")
    show_git_credentials()

    for drive in get_available_drives():
        scan_drive(drive)

    log("===== Execution Completed =====\n")


if __name__ == "__main__":
    main()
