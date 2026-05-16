# GitHub Streak Bot

Her gün GitHub'a otomatik bir commit atan basit bir bot. Bilgisayar açıldığında ve her gün 20:00'da çalışır; o gün zaten commit atılmışsa hiçbir şey yapmaz.

## Nasıl çalışır?

Bot kendi reposunda yaşıyor. `bot.py` çalıştığında:

1. `git pull --rebase` ile uzak repo'yu günceller.
2. Bugün (gece yarısından beri) commit var mı diye `git log` ile bakar.
3. Yoksa `streak_log.md` dosyasına bir satır ekler, commit eder ve push'lar.
4. Her çalışmasını `bot_run.log` dosyasına yazar.

## Gereksinimler

Windows'ta Python 3 (PATH'e ekli) ve Git for Windows kurulu olmalı. Git Credential Manager varsayılan olarak gelir; HTTPS kullanıyorsan ilk push'ta GitHub login penceresi çıkar, sonra token saklanır. SSH kullanıyorsan key'in `~/.ssh/`'de olmalı ve agent çalışıyor olmalı.

## Kurulum

Bot dosyalarını boş bir klasöre koy. PowerShell aç:

```powershell
cd C:\path\to\github-streak-bot

git init -b main
git remote add origin https://github.com/KULLANICI_ADIN/REPO_ADI.git
git add .
git commit -m "init: streak bot"
git push -u origin main
```

(Önce GitHub'da boş bir repo açmayı unutma.)

Sonra Task Scheduler görevini kur:

```powershell
.\setup_task.ps1
```

Eğer `.ps1` çalıştırılamıyorsa bir kerelik şunu çalıştır:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Test

```powershell
Start-ScheduledTask -TaskName GitHubStreakBot
```

Birkaç saniye sonra `bot_run.log`'a bak. Başarılıysa GitHub profilinde yeşil kare görünür.

## Saati değiştirmek

`setup_task.ps1` içindeki `-At 8:00PM` satırını istediğin saatle değiştirip scripti tekrar çalıştır.

## Görevi silmek

```powershell
Unregister-ScheduledTask -TaskName GitHubStreakBot -Confirm:$false
```

## Notlar

Bot o gün gerçek bir commit attıysan tekrar bir şey yapmaz, sadece açıkları kapatır. Yani normal çalışmana karışmaz.

Push'un sessizce çalışabilmesi için git auth'ın bir kez interaktif olarak yapılmış olması gerekir. Bot çalıştığında parola sorulması gerekmez; aksi takdirde `bot_run.log`'da hata görürsün.
