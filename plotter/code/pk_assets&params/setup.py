from setuptools import setup, find_packages

setup(
    name='Assets_Params',                  # Nome del pacchetto
    version='1.0.0',                # Versione (usa semantic versioning)
    packages=find_packages(include=['Assets_Params', 'Assets_Params.*']),       # Trova automaticamente tutti i package
    description='Modulo contenente i parametri globali dell\'applicazione, indirizzi, file di configurazione e curve target',
    author='Matteo Satanassi',
)