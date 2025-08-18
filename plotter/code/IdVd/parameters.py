from pathlib import Path
import pandas as pd

## PARAMS ##
data_dir = Path('../../data')
df = pd.read_excel(data_dir / 'indexes.xlsx', sheet_name='IdVd')
exp_mode_dict = df.to_dict('records')

## DERIVED PARAMS ##
group_first_only_indexes = df.drop_duplicates(subset='group', keep='first').index.tolist()  # restituisce una lista degli indici delle prime occorrenze di ogni gruppo
group_mode_dict = df.iloc[group_first_only_indexes].to_dict('records')