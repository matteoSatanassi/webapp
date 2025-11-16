from pathlib import Path
import json

## FUNC ##
def load_configs():
    """Carica configurazione esistente o crea default"""
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        return {
            "theme": "SUPERHERO",
            "data_directory": str(Path(__file__).parent.parent.parent.parent/'data'),
            "export_directory": str(Path.home() / 'Desktop' / 'exported_files'),
            "export_format": "png",
            "legend": True,
            "colors": True,
            "DPI": 150,
        }

def load_files_info():
    """
    Carica i tipi di file da analizzare nella run,
    i parametri a loro associati e le curve contenute
    """
    if file_params_file.exists():
        with open(file_params_file, 'r') as f:
            return json.load(f)
    else:
        return {}

## PARAMS ##
assets_dir = Path(__file__).resolve().parent / 'assets'
config_file = assets_dir / 'config.json'
file_params_file = assets_dir / 'file_params.json'

data_dir = Path(load_configs()["data_directory"])
indexes_file = data_dir/'indexes.xlsx'
affinity_file = data_dir/'affinity_table.xlsx'