#!/usr/bin/env python3
"""
Autosync: отслеживает изменения в ~/wiki/ и пушит в GitHub.
Запускается как launchd агент, живёт фоново.
Использует kqueue для файловых событий (нативный macOS, без зависимостей).
"""

import os
import sys
import time
import stat
import subprocess
import json
import fcntl
import select
import logging

WIKI_DIR = os.path.expanduser("~/wiki")
LOCK_FILE = os.path.expanduser("~/wiki/.autosync.lock")
STATE_FILE = os.path.expanduser("~/wiki/.autosync-state.json")
COOLDOWN = 5  # секунд после последнего изменения перед коммитом
MAX_BATCH = 60  # макс секунд ждать батча

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [autosync] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
log = logging.getLogger("autosync")


def git(*args):
    """Execute git command in WIKI_DIR."""
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


def push_pending():
    """Commit and push any changes."""
    # Проверяем есть ли что коммитить
    status = git("status", "--porcelain")
    if not status.stdout.strip():
        return False

    changed = status.stdout.strip().split("\n")
    log.info(f"Changes detected ({len(changed)} files), committing...")

    for line in changed:
        log.info(f"  {line}")

    # Add all
    git("add", "-A")
    # Commit
    commit = git("commit", "-m", f"autosync: {len(changed)} file(s)")
    if commit.returncode != 0:
        return False

    # Push
    push = git("push", "origin", "main")
    if push.returncode == 0:
        log.info(f"Pushed {len(changed)} file(s) ✅")
        return True
    else:
        log.warning(f"Push failed: {push.stderr.strip()}")
        return False


def watch_kqueue():
    """Watch ~/wiki/ for changes using kqueue (pure Python, zero deps)."""
    log.info(f"Starting autosync watcher on {WIKI_DIR}")

    fd = select.kqueue()
    changes_since = 0
    pending_push = False

    # Начальная индексация всех директорий
    dirs = set()
    dirs.add(WIKI_DIR)

    def scan_dirs(base):
        """Recursively find all directories, skipping .git."""
        for root, dirnames, files in os.walk(base):
            if ".git" in root:
                continue
            dirs.add(root)

    scan_dirs(WIKI_DIR)
    log.info(f"Watching {len(dirs)} directories")

    # Ставим наблюдателей на все директории
    watchers = {}
    for d in sorted(dirs):
        ev = [
            select.kevent(
                os.open(d, os.O_EVTONLY | os.O_NONBLOCK),
                filter=select.KQ_FILTER_VNODE,
                flags=select.KQ_EV_ADD | select.KQ_EV_CLEAR,
                fflags=(
                    select.KQ_NOTE_WRITE
                    | select.KQ_NOTE_DELETE
                    | select.KQ_NOTE_RENAME
                    | select.KQ_NOTE_EXTEND
                ),
            )
        ]
        try:
            result = fd.control(ev, 0)
            watchers[d] = ev
        except Exception as e:
            log.warning(f"Could not watch {d}: {e}")

    log.info(f"Kqueue watchers created: {len(watchers)}")

    try:
        while True:
            events = fd.control([], 1)  # 1 second timeout
            if events:
                now = time.time()
                changes_since = now
                pending_push = True

            if pending_push and changes_since > 0:
                elapsed = time.time() - changes_since
                if elapsed >= COOLDOWN or elapsed >= MAX_BATCH:
                    if push_pending():
                        changes_since = 0
                        pending_push = False
                    else:
                        # Если пуша не было, ждём ещё
                        changes_since = time.time()

    except KeyboardInterrupt:
        log.info("Shutting down")
    finally:
        fd.close()


if __name__ == "__main__":
    watch_kqueue()
