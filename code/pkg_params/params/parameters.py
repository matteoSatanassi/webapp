from pathlib import Path
import json

## FUNC ##
def load_configs():
    """Carica configurazione esistente o crea default"""
    if config_file.exists():
        with open(config_file, 'r', encoding="utf-8") as f:
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
    if files_configs_file.exists():
        with open(files_configs_file, 'r', encoding="utf-8") as f:
            out = json.load(f)
            out.pop("_comments")
            return out
    else:
        return {}

## PARAMS ##
assets_dir = Path(__file__).resolve().parent / 'assets'
targets_dir = assets_dir / 'target_curves'
config_file = assets_dir / 'config.json'
files_configs_file = assets_dir / 'files_configs.json'

data_dir = Path(load_configs()["data_directory"])
indexes_file = data_dir/'indexes.xlsx'
affinity_file = data_dir/'affinity_table.xlsx'

if __name__ == '__main__':
    print(load_files_info())