import os
import subprocess
from datetime import datetime
import string
import logging
from ctypes import windll

# Configuration
BRANCH = "main"  # Replace with your branch if needed
LOG_FILE = os.path.expanduser("git_auto_push.log")

# Setup logging (file + console)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log(msg):
    print(msg)
    logging.info(msg)


def get_available_drives():
    r"""Return a list of available drive letters excluding C:\ (system drive)"""
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            if letter != 'C':  # Skip system drive
                drives.append(f"{letter}:\\")
        bitmask >>= 1
    return drives


def is_git_repo(path):
    """Check if folder is a valid git repo"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False


def has_changes(path):
    """Check if repo has uncommitted changes"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            return False
        return result.stdout.strip() != ""
    except Exception:
        return False


def commit_and_push(path):
    log(f"\n➡️ Checking repository: {path}")

    if not is_git_repo(path):
        log(f"⛔ Not a valid Git repository, skipping: {path}")
        return

    try:
        if has_changes(path):
            log("📝 Changes found → committing...")

            subprocess.run(["git", "add", "."], cwd=path, check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Auto commit on {datetime.now()}"],
                cwd=path,
                check=True
            )
            log("📤 Pushing to remote...")

            push = subprocess.run(
                ["git", "push", "origin", BRANCH],
                cwd=path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if push.returncode != 0:
                log(f"❌ Push failed for: {path}")
                log(f"Error: {push.stderr}")
            else:
                log(f"✔ Successfully pushed changes from: {path}")

        else:
            log("✓ No changes found")

    except subprocess.CalledProcessError as e:
        log(f"❌ Git error in {path}: {e}")
    except Exception as e:
        log(f"⚠️ Unexpected error in {path}: {e}")


def scan_drive(drive):
    log(f"\n🔍 Scanning drive: {drive}")
    for root, dirs, _ in os.walk(drive):
        if ".git" in dirs:
            commit_and_push(root)
            dirs.clear()  # Do not search deeper inside the repo


def main():
    log("\n==============================")
    log("🚀 Starting Windows Git Auto Push")
    log("==============================")

    for drive in get_available_drives():
        scan_drive(drive)

    log("\n==============================")
    log("🏁 Completed scanning all drives\n")
    log("==============================\n")


if __name__ == "__main__":
    main()
