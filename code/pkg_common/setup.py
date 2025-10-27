from setuptools import setup, find_packages

setup(
    name='common',                  # Nome del pacchetto
    version='1.0.0',                # Versione (usa semantic versioning)
    packages=find_packages(include=['common', 'common.*']),       # Trova automaticamente tutti i package
    description='Modulo comune per funzioni condivise della webapp',
    install_requires=[
        'numpy',
        'pandas',
        'plotly'
    ],
)