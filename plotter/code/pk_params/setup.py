from setuptools import setup, find_packages

setup(
    name='params',                  # Nome del pacchetto
    version='1.0.0',                # Versione (usa semantic versioning)
    packages=find_packages(include=['params', 'params.*']),       # Trova automaticamente tutti i package
    description='Modulo contenente i parametri globali dell\'applicazione, indirizzi, file di configurazione e curve target',
    author='Matteo Satanassi',
)