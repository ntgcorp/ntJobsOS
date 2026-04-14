@ECHO OFF
:: Sposta la directory corrente nella cartella dove risiede il file .bat
:: PUSHD gestisce correttamente anche i percorsi di rete (UNC)
PUSHD "%~dp0"

:: Definiamo il percorso di destinazione (livello precedente + users/admin)
SET "TARGET_DIR=..\Users\admin"
SET "FILE_PATH=%TARGET_DIR%\jobs.ini"
SET "SYS_COMMAND=SYS.RELOAD"

ECHO Creazione jobs.ini %SYS_COMMAND%...

:: Creiamo le cartelle. Se il percorso e' UNC, PUSHD lo ha gia risolto.
IF NOT EXIST "%TARGET_DIR%" (
    MKDIR "%TARGET_DIR%" 2>NUL
)

:: Scrittura del file
(
    ECHO [CONFIG]
    ECHO TYPE=NTJOBS.APP.1.0
    ECHO NAME=SYS_COMMAND
    ECHO.
    ECHO [JOB_COMMAND]
    ECHO ACTION=%SYS_COMMAND%
) > "%FILE_PATH%" 2>NUL

:: Verifica finale
IF EXIST "%FILE_PATH%" (
    ECHO OK - ntjobsos ripartira con la configurazione aggiornata.
    ECHO Creato in: %TARGET_DIR%
) ELSE (
    ECHO ERRORE: impossibile creare jobs.ini.
    ECHO Controlla i permessi di scrittura in: %TARGET_DIR%
    POPD
    PAUSE
    EXIT /B 1
)

:: Torna al percorso originale e libera la lettera di unita' virtuale
POPD
PAUSE