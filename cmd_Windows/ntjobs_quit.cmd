@ECHO OFF
REM ============================================================
REM ntjobs_quit.cmd
REM Invia il comando SYS.QUIT ad aiJobsOS2.
REM Lo script Python termina in modo pulito senza creare
REM alcun file flag: il CMD launcher cade su :END e si chiude.
REM ============================================================

ECHO Creazione jobs.ini SYS.QUIT...

(
ECHO [CONFIG]
ECHO TYPE=NTJOBS.APP.1.0
ECHO NAME=SYS_QUIT
ECHO.
ECHO [JOB_QUIT]
ECHO COMMAND=SYS.QUIT
) > "K:\ntjobsai2\users\admin\jobs.ini"

IF ERRORLEVEL 1 (
    ECHO ERRORE: impossibile creare jobs.ini
    EXIT /B 1
)

ECHO OK - aiJobsOS2 terminera al prossimo ciclo.
