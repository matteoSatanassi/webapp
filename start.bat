@echo off

cd ..\

    ::Attivazione ambiente virtuale
call .venv\Scripts\activate

.venv\Scripts\python.exe plotter\code\app.py

    ::Mantiene il terminale aperto dopo l'esecuzione
pause