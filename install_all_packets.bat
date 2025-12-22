@echo off
setlocal
cd /d "%~dp0"

REM ==============================
REM 1️. Crea un ambiente virtuale se non esiste
REM ==============================
if not exist ".venv" (
    echo Creazione ambiente virtuale...
    py -3 -m venv .venv
) else (
    echo Ambiente virtuale gia' presente.
)

REM ==============================
REM 2️. Attiva l'ambiente virtuale
REM ==============================
call .venv\Scripts\activate

REM ==============================
REM 3️. Aggiorna pip e installa requirements
REM ==============================
echo Aggiornamento di pip...
python -m pip install --upgrade pip

if exist "requirements.txt" (
    echo Installazione pacchetti da requirements.txt...
    pip install -r requirements.txt
) else (
    echo ATTENZIONE: nessun file requirements.txt trovato!
)

REM ==============================
REM 4️. Installa pacchetti locali (editable mode)
REM ==============================

echo Installing pk_common...
pip install -e ".\code\_custom_pkgs\pkg_common"

echo Installing pk_app_elements...
pip install -e ".\code\_custom_pkgs\pkg_app_elements"

echo Installing pk_params...
pip install -e ".\code\_custom_pkgs\pkg_app_resources"

REM ==============================
REM 5️. Fine script
REM ==============================
echo.
echo Installazione completata!
pause
endlocal

