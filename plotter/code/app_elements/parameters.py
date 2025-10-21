from pathlib import Path
import json

## FUNC ##
def load_configs():
    """Carica configurazione esistente o crea default"""
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "theme": "SUPERHERO",
            "data_directory": str(Path(__file__).parent.parent.parent/'data'),
            "export_directory": str(Path.home() / 'Desktop' / 'exported_files'),
            "export_format": "png",
            "legend": True,
            "colors": True,
            "DPI": 150,
        }

## PARAMS ##
assets_dir = Path(__file__).resolve().parent.parent / 'assets'
config_path = assets_dir / 'config.json'

data_dir = Path(load_configs()["data_directory"])
indexes_file = data_dir/'indexes.xlsx'
affinity_file = data_dir/'affinity_table.xlsx'