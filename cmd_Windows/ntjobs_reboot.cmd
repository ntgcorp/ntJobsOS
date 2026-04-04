@ECHO OFF
REM ============================================================
REM ntjobs_reboot.cmd
REM Invia il comando SYS.REBOOT ad aiJobsOS2.
REM Lo script Python crea ntjobs.shutdown e termina.
REM NOTA: il CMD launcher attuale (aiJobsOs2.cmd) non ha un
REM branch separato per il reboot; mappa su SHUTDOWN.EXE /S.
REM Per abilitare il riavvio effettivo aggiungere in aiJobsOs2.cmd:
REM   IF EXIST "ntjobs.reboot" SHUTDOWN.EXE /R
REM e in aiJobsOS2.py cambiare il flag di SYS.REBOOT
REM da ntjobs.shutdown a ntjobs.reboot.
REM ============================================================

ECHO Creazione jobs.ini SYS.REBOOT...

(
ECHO [CONFIG]
ECHO TYPE=NTJOBS.APP.1.0
ECHO NAME=SYS_REBOOT
ECHO.
ECHO [JOB_REBOOT]
ECHO COMMAND=SYS.REBOOT
) > "K:\ntjobsai2\users\admin\jobs.ini"

IF ERRORLEVEL 1 (
    ECHO ERRORE: impossibile creare jobs.ini
    EXIT /B 1
)

ECHO OK - Il PC si spegnera al termine del ciclo corrente.
