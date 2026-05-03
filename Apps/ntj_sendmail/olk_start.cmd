@echo off

REM Avvio Outlook
echo Avvio Outlook...
start "" "outlook.exe"

REM Attesa 10 secondi
timeout /T 10 /NOBREAK >nul

REM Controllo se è attivo
tasklist | find /I "outlook.exe" >nul
if %errorlevel%==0 (
    echo Outlook avviato correttamente.
) else (
    echo Errore: Outlook non risulta avviato.
)
