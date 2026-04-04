@ECHO OFF
REM ============================================================
REM ntjobs_shutdown.cmd
REM Invia il comando SYS.SHUTDOWN ad aiJobsOS2.
REM Lo script Python crea ntjobs.shutdown e termina.
REM Il CMD launcher rileva ntjobs.shutdown ed esegue
REM SHUTDOWN.EXE /S per spegnere il PC.
REM ============================================================

ECHO Creazione jobs.ini SYS.SHUTDOWN...

(
ECHO [CONFIG]
ECHO TYPE=NTJOBS.APP.1.0
ECHO NAME=SYS_SHUTDOWN
ECHO.
ECHO [JOB_SHUTDOWN]
ECHO COMMAND=SYS.SHUTDOWN
) > "K:\ntjobsai2\jobs.ini"

IF ERRORLEVEL 1 (
    ECHO ERRORE: impossibile creare jobs.ini
    EXIT /B 1
)

ECHO OK - Il PC si spegnera al termine del ciclo corrente.
