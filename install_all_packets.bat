@echo off
setlocal

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
if exist ".\code\pk_common\" (
    echo Installing pk_common...
    pip install -e .\code\pk_common\
) else (
    echo pacchetto common non trovato.
)

if exist ".\code\pk_app_elements\" (
    echo Installing pk_app_elements...
    pip install -e .\code\pk_app_elements\
) else (
    echo pacchetto app_elements non trovato.
)

if exist ".\code\pk_params\" (
    echo Installing pk_params...
    pip install -e .\code\pk_params\
) else (
    echo pacchetto params non trovato.
)

REM ==============================
REM 5️. Fine script
REM ==============================
echo.
echo Installazione completata!
pause
endlocal

