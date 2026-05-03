REM Prova chiusura normale
echo Chiudo Outlook...
taskkill /IM outlook.exe >nul 2>&1

REM Attesa 10 secondi
timeout /T 10 /NOBREAK >nul

REM Controllo se è ancora aperto
tasklist | find /I "outlook.exe" >nul
if %errorlevel%==0 (
    echo Outlook è ancora in esecuzione, forzo chiusura...
    taskkill /F /IM outlook.exe >nul 2>&1
) else (
    echo Outlook chiuso correttamente.
)
