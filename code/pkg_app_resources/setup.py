from setuptools import setup, find_packages

setup(
    name='app_resources',           # Nome del pacchetto
    version='2.0.0',                # Versione (usa semantic versioning)
    packages=find_packages(include=['app_resources', 'app_resources.*']),       # Trova automaticamente tutti i package
    description="""
    Modulo contenente i parametri globali dell\'applicazione, indirizzi, file di configurazione e curve target, 
    nonché la memoria cache e le classi di cui è composta
    """,
    author='Matteo Satanassi',
)