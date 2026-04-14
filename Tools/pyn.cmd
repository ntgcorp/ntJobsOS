@ECHO OFF
REM VERSIONE 20260313 - AGGIUNTO PODMAN
REM VERSIONE 20260219 - AGGIUNTA W64
REM VERSIONE 20260129 - PICCOLA CORREZIONE
REM VERSIONE 20250405 - CORREZIONI - INSTALLAZIONE CRYPTOGRAFY - FORSE PSUTIL
REM VERSIONE 20250130 - GESTIONE MIGLIORE RUNTIME
REM VERSIONE 20250203 - DEFUALT X64
REM VERSIONE 20250803 - PYN MASTER che gestisce gli upgrade "SOLO su NTGCORP" con flag
REM                   - comandi x reqx - pip requirements export e x reqi - pip requirements import
REM TOGLIERE ECHO OFF SOPRA PER DEBUG
REM PATH ESISTENZA VERIFICHE ESISTENZA KIT IN SEQUENZA
SET PATHP_01=D:\APPLIC\PYTHONX64\APP\PYTHON
SET PATHP_02=C:\APPLIC\PYTHONX64\APP\PYTHON
SET PATHP_MACH0=K:\Tools\PythonX64\APP\PYTHON
SET PATHP_03=X:\_ntgcorp\PythonX64\APP\PYTHON
SET PYN_VER=20260320

REM SETUP
SET PY_SCRIPT=%0
SET PY_P0=%~dp0
IF "%PY_TYPE%"=="" SET PY_TYPE=X64
SET PY_PATH=

REM VERIFICA QUALE FOLDER E' PRESENTE X32 o X64	CON CACHE.
REM SE PRESENTE pyn_master.flag nella stessa cartella salta avanti
IF EXIST "%PY_P0%" SET PY_PATH=%PY_P0%PYTHON%PY_TYPE%
IF EXIST "%PY_P0%PYTHON%PY_TYPE%\*.*" SET PY_PATH=%PY_P0%PYTHON%PY_TYPE%\App\Python
IF EXIST "%PY_P0%pyn_master.flag" GOTO PYN_1

REM CASO VDI.MACH0
IF EXIST "K:\MACH0_PROD.TXT" SET PY_PATH=%PATHP_MACH0%

REM CASO AMBIENTE NTGCORP
IF "%PY_PATH%"=="" SET PY_PATH=%PATHP_03%

REM CASO C:\APPLIC - SOVRAPPONI
IF EXIST C:\APPLIC\PYTHONX64\APP\PYTHON\*.* SET PY_PATH=%PATHP_02%

REM CASO D:\APPLIC - SOVRAPPONI
IF EXIST D:\APPLIC\PYTHONX64\APP\PYTHON\*.* SET PY_PATH=%PATHP_01%

:PYN_1
REM AVVIO
@ECHO LAUNCHER PYTHON PORTABLE NTJOBS %PYN_VER%: Tipo %PY_TYPE%: Path: %PY_PATH%
REM EVENTUALE USCITA PER ERRORE
IF "%PY_PATH%"=="" GOTO :ERR

REM DEBUG TEST
REM ECHO PATH PYTHON: %PY_PATH%

REM VERIFICA FORZATURA
IF NOT "%PY_PATH%"=="" GOTO :CMD
IF "%PY_TYPE%"=="X32" SET PY_PATH=%PY_P0%PYTHONX32
IF "%PY_TYPE%"=="X64" SET PY_PATH=%PY_P0%PYTHONX64
IF "%PY_TYPE%"=="W64" SET PY_PATH=%PY_P0%PYTHONW64

REM PY_CMD
:CMD
SET PY_CMD=%PY_PATH%\PYTHON.EXE

REM COMANDI ESTESI (sempre minuscoli)
IF EXIST "%1" GOTO :RUN
IF "%1"=="x" GOTO :X
IF "%1"=="pip" GOTO :PIP
IF "%1"=="pod" GOTO :POD
IF "%1"==""  GOTO :SINTASSI

:RUN
IF NOT EXIST "%PY_CMD%" GOTO :ERR
ECHO START PYTHON SCRIPT: %PY_SCRIPT% - %PY_0% - %PY_CMD% - %1 %2 %3 %4 %5 %6 %7 %8 %9
"%PY_CMD%" %1 %2 %3 %4 %5 %6 %7 %8 %9
GOTO :END

:ERR
@ECHO OFF
ECHO PYN: Attenzione, non esiste la cartella PYTHON%PY_TYPE% richiesta allo stesso livello
GOTO :END

:X
REM UPGRADE - Necessaria presenza PIP-REVIEW
IF "%2"=="upgrade" GOTO :UPGRADE
IF "%2"=="req" "%PY_CMD%" -m  pip freeze > requirements.txt
IF "%2"=="mod" "%PY_CMD%" -m  %3 %4 %5 %6 %7 %8 %9
IF "%2"=="pip" "%PY_CMD%" -m  pip %3 %4 %5 %6 %7 %8 %9
IF "%2"=="pip_i" "%PY_CMD%" -m  pip install %3 %4 %5 %6 %7 %8 %9
IF "%2"=="pip_re" GOTO :PIP_RE
IF "%2"=="pip_ri" "%PY_CMD%" -m  pip install -r requirements_%PY_TYPE%.txt
IF "%2"=="autoc" chrome --remote-debugging-port=9222 --user-data-dir="C:\chromedata"
IF "%2"=="upgrade2" goto :UPGALL
IF "%2"=="" ECHO COMANDO ESTESO (x) NON INSERITO
GOTO :END

:PIP
"%PY_CMD%" -m pip %2 %3 %4 %5 %6 %7 %8 %9
GOTO :END

:POD
IF "%POD_PATH%"=="" SET POD_PATH=c:\podman
IF "%POD_APP%"=="" SET POD_APP=ntjobsos
IF "%2"=="" GOTO :SINTASSI
IF "%2"=="x" GOTO :POD_RUN
IF "%2"=="start" GOTO :POD_START
IF "%2"=="end" GOTO :POD_END
IF "%2"=="opt" GOTO :POD_OPT

ECHO Podman Esecuzione Standard
podman %2 %3 %4 %5 %6 %7 %8 %9
GOTO :END

:POD_RUN
ECHO Podman Esecuzione Python ntjobsos Script
podman run -it --rm -v "%POD_PATH%:/app" %POD_APP%:v1 %3
GOTO :END

:POD_END
ECHO Podman Stop e chiudi wsl
wsl --shutdown
GOTO :END

:POD_START
ECHO Podman Esecuzione motore
podman machine start
GOTO :END

:POD_OPT
@echo off
setlocal
:: --- CONFIGURAZIONE ---
:: Inserisci qui il percorso del tuo file VHDX se lo hai spostato, 
:: altrimenti lo script proverà a cercarlo in quello standard.
set VHDX_PATH=%USERPROFILE%\.local\share\containers\podman\machine\wsl\podman-machine-default_data.vhdx

echo [1/4] Avvio macchina per pulizia interna...
podman machine start

echo [2/4] Esecuzione fstrim (segnalo i blocchi vuoti)...
:: Lanciamo fstrim dentro la macchina tramite SSH
podman machine ssh sudo fstrim -av

echo [3/4] Spegnimento totale WSL per liberare il file...
podman machine stop
wsl --shutdown

echo [4/4] Ottimizzazione disco VHDX (Richiede privilegi Admin)...
:: Usiamo PowerShell per compattare il file fisicamente
powershell -Command "Optimize-VHD -Path '%VHDX_PATH%' -Mode Full"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ATTENZIONE: Optimize-VHD e fallito. 
    echo Assicurati di aver eseguito questo file come AMMINISTRATORE.
) else (
    echo.
    echo OPERAZIONE COMPLETATA CON SUCCESSO!
)

pause
GOTO :END

:PIP_RE
"%PY_CMD%" -m  pip freeze > requirements_%PY_TYPE%.txt
for /f "tokens=1 delims==" %%i in (requirements_%PY_TYPE%.txt) do @echo %%i >> requirements_%PY_TYPE%_LIGHT.txt
GOTO :END

:UPGRADE
"%PY_CMD%" -m pip install --upgrade pip
"%PY_CMD%" "%PY_PATH%\Scripts\pip-review.exe" --interactive
call pyn.cmd x pip_re
GOTO :END

:UPGALL
ECHO VIENE IMPOSTATA VARIBILE X32 X64 W64 e upgrade per tutti e 2 i tipi

ECHO ATTUALE: %PY_TYPE%
SET PY_STACK=%PY_TYPE%

SET PY_TYPE=X32
call pyn.cmd x upgrade
SET PY_TYPE=X64
call pyn.cmd x upgrade
SET PY_TYPE=W64
call pyn.cmd x upgrade

SET PY_TYPE=%PY_STACK%
SET PY_STACK=
ECHO ATTUALE: %PY_TYPE%

GOTO :END

:SINTASSI
@ECHO OFF
ECHO SCRIPT PYN.CMD di lancio PYTHON PORTABLE. X64 o X32 
ECHO Sintassi PYN.CMD script.py [parametri 2..9]
ECHO PY_TYPE=Variabile d'ambiente per forzarel 32 o 64bit (SET PY_TYPE=X32 o PY_TYPE=X64) prima dell'esecuzione di PYN.CMD
ECHO PYN.CMD pip [comando pip]
ECHO PYN.CMD x [comando esteso]
ECHO PYN.CMD x autoc - Chrome automation per playwright
ECHO PYN.CMD x upgrade (upgrade di tutti i package) + PIP_UPGRADE + REQUIREMENTS
ECHO PYN.CMD x upgrade2 (upgrade di tutti i package - sia x32 che x64)
ECHO PYN.CMD x pip richiamo mod pip [comandi] per gestione librerie interne, aggiornamenti, ecc.
ECHO PYN.CMD x pip_i richiamo mod pip install per install librerie (fino a 7)
ECHO PYN.CMD x pip_re/pip_ri - Crea requirements_x32/x64.txt - Importa requirements.txt
ECHO PYN.CMD x mod modulo richiamo mod specifico
ECHO PYN.CMD %CD%\test_python.py (Esecuzione script di test)
ECHO PYN.CMD pod comando script . Devono essere impostate le ENV POD_PATH e POD_APP(ntjobsos default)
ECHO PYN.CMD pod end
ECHO PYN.CMD pod start

:END