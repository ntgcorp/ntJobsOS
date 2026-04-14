:START
REM PYTHON INTERPRETER
SET PYTHON=k:\tools\pyn.cmd 

ECHO NTJOBSOS.START
FOR %%A IN (ntjobs.reload ntjobs.restart ntjobs.shutdown) DO IF EXIST "%%A" del "%%A"

@REM LANCIO NTJOBSOS
call %PYTHON% aiJobsOS2.py

@REM EVENTUALE RESTART
IF EXIST "ntjobs.reload" GOTO :START
IF EXIST "ntjobs.shutdown" SHUTDOWN.EXE /S 
IF EXIST "ntjobs.restart" SHUTDOWN.EXE /R


:END
ECHO NTJOBSOS.END