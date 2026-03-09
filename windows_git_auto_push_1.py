import os
import subprocess
from datetime import datetime
import string
import logging
from ctypes import windll

# Configuration
BRANCH = "main"  # Replace with your branch if needed
LOG_FILE = os.path.expanduser("~/git_auto_push.log")

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")
log = logging.info


def get_available_drives():
    """Return a list of available drive letters excluding C:\ (system drive)"""
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
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.strip() != ""


def commit_and_push(path):
    try:
        log(f"→ Checking: {path}")

        if has_changes(path):
            subprocess.run(["git", "add", "."], cwd=path, check=True)
            subprocess.run(["git", "commit", "-m", f"Auto commit on {datetime.now()}"], cwd=path, check=True)
            subprocess.run(["git", "push", "origin", BRANCH], cwd=path, check=True)
            log(f"✔ Changes pushed in {path}")
        else:
            log(f"✓ No changes in {path}")
    except subprocess.CalledProcessError as e:
        log(f"✘ Git error in {path}: {e}")


def scan_drive(drive):
    log(f"🔍 Scanning drive: {drive}")
    for root, dirs, _ in os.walk(drive):
        if ".git" in dirs:
            commit_and_push(root)
            dirs.clear()  # Don't search subfolders once a git repo is found


def main():
    log("=== Starting Windows Git Auto Push ===")
    for drive in get_available_drives():
        scan_drive(drive)
    log("=== Completed ===\n")


if __name__ == "__main__":
    main()
