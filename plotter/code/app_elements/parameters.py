from pathlib import Path
import pandas as pd
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
            "export_directory": str(Path.home() / 'Desktop' / 'exported_files'),
            "export_format": "png",
            "legend": True,
            "colors": True,
            "DPI": 150,
        }

## PARAMS ##
data_dir = Path(__file__).parent.parent.parent/'data'
indexes_file = data_dir/'indexes.xlsx'

assets_dir = Path(__file__).resolve().parent.parent / 'assets'
config_path = assets_dir / 'config.json'

affinity_file = data_dir/'affinity_table.xlsx'