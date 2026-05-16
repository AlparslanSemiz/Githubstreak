@echo off
REM ============================================
REM  GitHub Streak Bot - Manuel Commit
REM ============================================
REM  Bu dosyaya cift tiklayinca hemen bir veya
REM  birkac commit atar (rastgele 1-3 arasinda).
REM  Bugun zaten commit atilmis olsa bile yine atar.
REM ============================================

cd /d "%~dp0"

echo.
echo  GitHub Streak Bot - manuel commit baslatiliyor...
echo.

python bot.py --force

echo.
echo  Islem tamamlandi. Kapatmak icin bir tusa bas.
pause >nul
