@echo off
setlocal

set BASE=%~dp0

echo Creazione cartelle in: %BASE%

mkdir "%BASE%Tools"    2>nul
mkdir "%BASE%Inbox"    2>nul
mkdir "%BASE%Archive"  2>nul
mkdir "%BASE%Temp"     2>nul
mkdir "%BASE%Log"      2>nul
mkdir "%BASE%Users"    2>nul
mkdir "%BASE%Users\Admin" 2>nul
mkdir "%BASE%Users\User"  2>nul

echo.
echo Fatto.
endlocal
