from setuptools import setup, find_packages

setup(
    name='common',                  # Nome del pacchetto
    version='0.1.2',                # Versione (usa semantic versioning)
    packages=find_packages(),       # Trova automaticamente tutti i package
    include_package_data=True,      # Includi file non-PY (es. dati, template)
    install_requires=['numpy', 'pathlib'],            # Dipendenze esterne
)