#!/usr/bin/env python3
"""
Autosync: отслеживает изменения в ~/wiki/ и пушит в GitHub.
Простой polling-based watcher (совместим с любой версией Python/macOS).
"""

import os
import sys
import time
import subprocess
import hashlib
import json
import logging

WIKI_DIR = os.path.expanduser("~/wiki")
STATE_FILE = os.path.expanduser("~/wiki/.autosync-state.json")
POLL_INTERVAL = 3  # секунд между проверками
COOLDOWN = 5  # секунд после последнего изменения
GIT_PUSH_INTERVAL = 30  # макс интервал между пушами при постоянных изменениях

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [autosync] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
log = logging.getLogger("autosync")


EXCLUDE_FILES = {".autosync-state.json", ".autosync.lock", "autosync.py"}

def get_file_hashes(base_dir):
    """Build a dict of {relative_path: (mtime, size)} for all non-git files.
    Excludes autosync's own files to avoid self-triggering."""
    state = {}
    for root, dirs, files in os.walk(base_dir):
        # Skip .git
        if ".git" in root:
            continue
        for f in files:
            if f in EXCLUDE_FILES:
                continue
            path = os.path.join(root, f)
            try:
                st = os.stat(path)
                rel = os.path.relpath(path, base_dir)
                state[rel] = [st.st_mtime, st.st_size]
            except OSError:
                pass
    return state


def git(*args):
    result = subprocess.run(
        ["git"] + list(args),
        cwd=WIKI_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0 and result.stderr.strip():
        log.warning(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result


def pull_first():
    """Pull latest from GitHub before pushing."""
    result = git("pull", "origin", "main", "--ff-only")
    if result.returncode != 0:
        log.warning(f"Pull failed: {result.stderr.strip()}")
    else:
        stdout = result.stdout.strip()
        if stdout and stdout != "Already up to date.":
            log.info(f"Pull: {stdout[:60]}...")
    return result


def push_pending():
    # Сначала pull, потом push (двусторонняя синхронизация)
    status = git("status", "--porcelain")
    if not status.stdout.strip():
        # Нет локальных изменений, но может быть удалённые (боты писали)
        pull_first()
        return False

    changed = status.stdout.strip().split("\n")
    log.info(f"Changes detected ({len(changed)} files)")

    # Pull перед push — чтобы минимизировать конфликты
    pull_first()

    git("add", "-A")
    commit = git("commit", "-m", f"autosync: {len(changed)} file(s)")
    if commit.returncode != 0:
        return False

    push = git("push", "origin", "main")
    if push.returncode == 0:
        log.info(f"Pushed {len(changed)} file(s) ✅")
        return True
    else:
        log.warning(f"Push failed, retrying after pull...")
        # Если push не удался — возможно новые изменения на GitHub, перетягиваем
        pull_first()
        push = git("push", "origin", "main")
        if push.returncode == 0:
            log.info(f"Pushed {len(changed)} file(s) ✅ (retry)")
            return True
        log.warning(f"Push failed again")
        return False


def watch():
    log.info(f"Autosync started, watching {WIKI_DIR}")

    # Load previous state
    previous = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                previous = json.load(f)
        except Exception:
            pass

    last_change = 0
    first_run = True

    while True:
        current = get_file_hashes(WIKI_DIR)

        if not first_run and current != previous:
            if last_change == 0:
                log.info("Changes detected")
                last_change = time.time()

        # Push if cooldown elapsed
        if last_change > 0:
            elapsed = time.time() - last_change
            if elapsed >= COOLDOWN:
                if push_pending():
                    previous = current
                    last_change = 0

        # Save state periodically (after push or unchanged)
        if last_change == 0:
            try:
                with open(STATE_FILE, "w") as f:
                    json.dump(current, f)
            except Exception:
                pass

        first_run = False
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    watch()
