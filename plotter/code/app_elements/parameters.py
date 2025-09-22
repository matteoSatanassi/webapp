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
            "export_directory": str(Path.home() / 'Desktop' / 'exported_files'),
            "export_format": "png",
            "theme": "SUPERHERO"
        }

## PARAMS ##
data_dir = Path(__file__).parent.parent.parent/'data'
IdVd_df = pd.read_excel(data_dir / 'indexes.xlsx', sheet_name='IdVd')
IdVd_table_exp_mode = IdVd_df.to_dict('records')

TrapData_df = pd.read_excel(data_dir / 'indexes.xlsx', sheet_name='TrapData')
TrapData_table = TrapData_df.to_dict('records')

config_path = Path(__file__).resolve().parent.parent / 'assets' / 'config.json'

## DERIVED PARAMS ##
group_first_only_indexes = IdVd_df.drop_duplicates(subset='group', keep='first').index.tolist()  # restituisce una lista degli indici delle prime occorrenze di ogni gruppo
IdVd_table_group_mode = IdVd_df.iloc[group_first_only_indexes].to_dict('records')