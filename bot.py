#!/usr/bin/env python3
"""
GitHub Daily Streak Bot

Her çalıştığında repo'da o gün commit atılıp atılmadığını kontrol eder.
Atılmamışsa rastgele 1-3 commit atar (havuzdan rastgele mesajlarla) ve push'lar.

Kullanım:
    python bot.py              # Bugün commit yoksa rastgele 1-3 commit at
    python bot.py --force      # Bugün commit olsa bile yeni commit at
    python bot.py --count 2    # Tam olarak 2 commit at
"""

import argparse
import datetime
import random
import subprocess
import sys
import time
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
LOG_FILE = REPO_DIR / "streak_log.md"
RUN_LOG = REPO_DIR / "bot_run.log"

# Bugün kaç commit atılacağının dağılımı: %70 bir, %25 iki, %5 üç
COMMIT_COUNT_CHOICES = [1, 2, 3]
COMMIT_COUNT_WEIGHTS = [70, 25, 5]

# Commit mesajları havuzu (developer-style, gerçekçi)
COMMIT_MESSAGES = [
    "chore: update notes",
    "refactor: small cleanup",
    "docs: minor tweaks",
    "chore: sync state",
    "fix: small adjustment",
    "wip: progress",
    "style: formatting",
    "chore: housekeeping",
    "review: code review notes",
    "docs: update",
    "refactor: tidy up",
    "chore: daily update",
    "fix: minor",
    "chore: bump log",
    "docs: notebook update",
    "chore: routine maintenance",
    "review: notes",
    "chore: misc",
]

# streak_log.md dosyasına yazılacak çeşitli aktivite tipleri
LOG_ENTRY_TYPES = [
    "daily check-in",
    "notes update",
    "review session",
    "progress log",
    "quick note",
    "sync",
    "todo update",
    "journal entry",
    "reading log",
]


def log(message: str) -> None:
    """Bot çalışma geçmişini bot_run.log'a yazar."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    with open(RUN_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Repo dizininde bir git komutu çalıştırır."""
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode != 0:
        log(f"Git hatası: git {' '.join(args)}\n{result.stderr.strip()}")
        sys.exit(1)
    return result


def has_commit_today() -> bool:
    """Bugün (gece yarısından beri) bu repo'da commit atılmış mı?"""
    result = run_git("log", "--since=midnight", "--pretty=format:%H", check=False)
    return bool(result.stdout.strip())


def append_log_entry() -> str:
    """streak_log.md dosyasına rastgele bir aktivite satırı ekler."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_type = random.choice(LOG_ENTRY_TYPES)

    if LOG_FILE.exists():
        content = LOG_FILE.read_text(encoding="utf-8")
    else:
        content = "# Streak Log\n\nGünlük aktivite kayıtları.\n\n"

    new_entry = f"- {now} -> {entry_type}\n"
    LOG_FILE.write_text(content + new_entry, encoding="utf-8")
    return new_entry.strip()


def make_one_commit() -> None:
    """Bir tane commit atar (log dosyasına satır ekler, add ve commit yapar)."""
    entry = append_log_entry()
    run_git("add", LOG_FILE.name)
    msg = random.choice(COMMIT_MESSAGES)
    run_git("commit", "-m", msg)
    log(f'Commit atildi: "{msg}" | {entry}')


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub Streak Bot")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bugün zaten commit atılmış olsa bile yeni commit at.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Sabit sayıda commit at (varsayılan: rastgele 1-3).",
    )
    args = parser.parse_args()

    log("Bot başlatıldı.")

    if not (REPO_DIR / ".git").exists():
        log(f"HATA: {REPO_DIR} bir git repo'su değil.")
        sys.exit(1)

    log("git pull --rebase yapılıyor...")
    run_git("pull", "--rebase", check=False)

    if not args.force and has_commit_today():
        log("Bugün zaten commit atılmış. İşlem yok. (--force ile zorlayabilirsin)")
        return

    if args.count is not None and args.count > 0:
        n = args.count
    else:
        n = random.choices(COMMIT_COUNT_CHOICES, weights=COMMIT_COUNT_WEIGHTS, k=1)[0]

    log(f"Bugün {n} commit atılacak.")

    for i in range(n):
        make_one_commit()
        if i < n - 1:
            # Commitler arası kısa rastgele bekleme (daha doğal görünür)
            wait = random.uniform(3, 12)
            log(f"Sonraki commit için {wait:.1f} sn bekleniyor...")
            time.sleep(wait)

    log(f"{n} commit hazir. git push yapiliyor...")
    run_git("push")
    log("Push basarili. Streak korundu.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Beklenmeyen hata: {e}")
        sys.exit(1)
