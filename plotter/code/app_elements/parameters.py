from pathlib import Path
import pandas as pd

from plotter.code.common.indexer import IDVD_COLUMNS

## PARAMS ##
data_dir = Path(__file__).parent.parent.parent/'data'
IdVd_df = pd.read_excel(data_dir / 'indexes.xlsx', sheet_name='IdVd')
IdVd_table_exp_mode = IdVd_df.to_dict('records')

TrapData_df = pd.read_excel(data_dir / 'indexes.xlsx', sheet_name='TrapData')
TrapData_table = TrapData_df.to_dict('records')

export_dir = Path(__file__).parent.parent.parent/'exported_files'

## DERIVED PARAMS ##
group_first_only_indexes = IdVd_df.drop_duplicates(subset='group', keep='first').index.tolist()  # restituisce una lista degli indici delle prime occorrenze di ogni gruppo
IdVd_table_group_mode = IdVd_df.iloc[group_first_only_indexes].to_dict('records')