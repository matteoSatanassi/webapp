@echo off

    ::Attivazione ambiente virtuale
call .venv\Scripts\activate

py ".\code\app.py"

    ::Mantiene il terminale aperto dopo l'esecuzione
pause