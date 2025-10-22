from setuptools import setup, find_packages

setup(
    name='app_elements',                  # Nome del pacchetto
    version='1.0.0',                # Versione (usa semantic versioning)
    packages=find_packages(include=['app_elements', 'app_elements.*']),       # Trova automaticamente tutti i package
    description='Modulo contenente elementi della webapp, da oggetti dash personalizzati a callbacks',
    install_requires=[
        'numpy',
        'pandas',
        'plotly',
        'dash_bootstrap_components',
        'dash',
    ],
)