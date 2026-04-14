REM @ECHO OFF
for %%F in (%0) do set PYSCRIPT=%%~nF.py
SET PYN=k:\tools\pyn.cmd
ECHO "%PYN%" "%PYSCRIPT%" %1 %2
"%PYN%" "%PYSCRIPT%" %1 %2

