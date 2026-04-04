@ECHO OFF
REM ============================================================
REM ntjobs_reload.cmd
REM Invia il comando SYS.RELOAD ad aiJobsOS2.
REM Lo script Python crea ntjobs.restart e termina.
REM Il CMD launcher rileva ntjobs.restart e fa GOTO :START,
REM ricaricando da zero config, utenti e azioni.
REM ============================================================

ECHO Creazione jobs.ini SYS.RELOAD...

(
ECHO [CONFIG]
ECHO TYPE=NTJOBS.APP.1.0
ECHO NAME=SYS_RELOAD
ECHO.
ECHO [JOB_RELOAD]
ECHO COMMAND=SYS.RELOAD
) > "K:\ntjobsai2\users\admin\jobs.ini"

IF ERRORLEVEL 1 (
    ECHO ERRORE: impossibile creare jobs.ini
    EXIT /B 1
)

ECHO OK - aiJobsOS2 ripartira con la configurazione aggiornata.
