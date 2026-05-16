# setup_task.ps1
# GitHub Streak Bot icin Windows Task Scheduler gorevini olusturur.
# Yonetici yetkisi gerekmez (kullanici hesabi altinda calisir).

$ErrorActionPreference = "Stop"

$TaskName  = "GitHubStreakBot"
$ScriptDir = $PSScriptRoot
$BotScript = Join-Path $ScriptDir "bot.py"

# Python yolunu bul (once 'python', sonra 'py' launcher)
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    $PythonPath = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $PythonPath) {
    Write-Error "Python bulunamadi. Lutfen Python'u kurup PATH'e ekleyin."
    exit 1
}

Write-Host "Python: $PythonPath"
Write-Host "Bot:    $BotScript"
Write-Host ""

# Eski gorev varsa sil
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Eski gorev silindi."
}

# Calistirma aksiyonu
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$BotScript`"" `
    -WorkingDirectory $ScriptDir

# Tetikleyici 1: Kullanici giris yaptiginda (yani bilgisayar acilinca)
$TriggerLogon = New-ScheduledTaskTrigger -AtLogOn -User "$env:COMPUTERNAME\$env:USERNAME"

# Tetikleyici 2: Her gun saat 20:00
$TriggerDaily = New-ScheduledTaskTrigger -Daily -At 8:00PM

# Ayarlar: pilde de calissin, bir sonraki firsatta yetissin
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

Register-ScheduledTask `
    -TaskName    $TaskName `
    -Action      $Action `
    -Trigger     @($TriggerLogon, $TriggerDaily) `
    -Settings    $Settings `
    -Description "Her gun GitHub'a otomatik commit atar (streak icin)."

Write-Host ""
Write-Host "Gorev olusturuldu: $TaskName"
Write-Host ""
Write-Host "Hemen test etmek icin:"
Write-Host "  Start-ScheduledTask -TaskName $TaskName"
Write-Host ""
Write-Host "Gorevi silmek icin:"
Write-Host "  Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
