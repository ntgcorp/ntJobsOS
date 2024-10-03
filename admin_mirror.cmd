REM @echo off
REM ROBOCOPY LIST FILES
ECHO Sintax mirror "path_source" "path_dest" "file_list"
ECHO Path With "\" ad end

REM VERIFICA
IF '%1'=='' GOTO :END
IF '%2'=='' GOTO :END
IF '%3'=='' GOTO :END

REM SETUP
SET dest=%~2
SET source=%~1
SET file_list=%~3

REM EXEC
FOR /f "useback tokens=1" %%f IN (`type %file_list%`) DO (
   IF exist "%source%%%f" (
      ECHO copying %%f from %source% to %dest%
      COPY "%source%%%f" "%dest%%%f" /y
   )
)
@REM     ROBOCOPY /NP /NJH /NJS "%source%" "%dest%" "%%~nxf"


:END
ECHO END MIRROR