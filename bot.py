#!/usr/bin/env python3
"""
GitHub Daily Streak Bot

Her çalıştığında repo'da o gün commit atılıp atılmadığını kontrol eder.
Atılmamışsa streak_log.md dosyasına bir satır ekler, commit eder ve push'lar.
"""

import subprocess
import datetime
import sys
from pathlib import Path

# Bot bu scriptin bulunduğu dizini repo kabul eder
REPO_DIR = Path(__file__).resolve().parent
LOG_FILE = REPO_DIR / "streak_log.md"
RUN_LOG = REPO_DIR / "bot_run.log"


def log(message: str) -> None:
    """Botun çalışma geçmişini bot_run.log'a yazar."""
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


def update_log_file() -> None:
    """streak_log.md dosyasına bugünün girdisini ekler."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if LOG_FILE.exists():
        content = LOG_FILE.read_text(encoding="utf-8")
    else:
        content = "# Streak Log\n\nGünlük otomatik check-in kayıtları.\n\n"

    new_entry = f"- {now} -> daily check-in\n"
    LOG_FILE.write_text(content + new_entry, encoding="utf-8")
    log(f"streak_log.md güncellendi: {new_entry.strip()}")


def main() -> None:
    log("Bot başlatıldı.")

    if not (REPO_DIR / ".git").exists():
        log(f"HATA: {REPO_DIR} bir git repo'su değil. Önce 'git init' yapın.")
        sys.exit(1)

    # Uzak değişiklikleri al ki push çakışmasın
    log("git pull --rebase yapılıyor...")
    run_git("pull", "--rebase", check=False)

    if has_commit_today():
        log("Bugün zaten commit atılmış. İşlem yok.")
        return

    update_log_file()

    run_git("add", LOG_FILE.name)
    today = datetime.date.today().isoformat()
    run_git("commit", "-m", f"chore: daily streak update {today}")
    log("Commit atıldı.")

    log("git push yapılıyor...")
    run_git("push")
    log("Push başarılı. Streak korundu.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Beklenmeyen hata: {e}")
        sys.exit(1)
