from ..app_elements import affinity_file
from pathlib import Path
import pandas as pd
import numpy as np

## PARAMS ##
EXP_COLUMNS = ('path', 'group', 'v0', '0', '15', '30')
GROUP_COLUMNS = ('group', 'aff')

## FUNC ##
def load_or_create_affinity_df(file_path: Path, sheet_name: str, columns: list) -> pd.DataFrame:
    """Carica o crea un dataframe di indice"""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df['path'] = df['path'].apply(Path)
        return df
    except (FileNotFoundError, ValueError):
        return pd.DataFrame(columns=columns)

def save_df(df_exp:pd.DataFrame, df_group:pd.DataFrame, output_file:Path)->None:
    """
    Salva i dataframe delle affinità nel file excel specificato
    """
    with pd.ExcelWriter(output_file) as writer:
        df_exp.to_excel(writer, sheet_name='exp', index=False)
        df_group.to_excel(writer, sheet_name='group', index=False)

## MAIN FUNC ##
def affinities_table_updater(indexes_file: str | Path) -> None:
    """
    Aggiorna il file contenente i valori delle affinità dei vari esperimenti a partire dal file degli indici
    """
    # Params
    idx_file_path = Path(indexes_file)
    idx = pd.read_excel(idx_file_path, sheet_name='IdVd')   # rendo il file degli indici un df

    paths = set(idx['file_path'].apply(Path))
    groups = set(idx['group'].unique())

    paths_to_add = []
    groups_to_add = []

    # controlla che il file contenente i valori delle affinità esista, altrimenti crea un DataFrame vuoto
    df_aff_exp = load_or_create_affinity_df(affinity_file, 'exp', EXP_COLUMNS)
    df_aff_group = load_or_create_affinity_df(affinity_file, 'group', GROUP_COLUMNS)

    # rimuove le righe con file non esistenti
    df_aff_exp = df_aff_exp[df_aff_exp['path'].isin(paths)]
    df_aff_group = df_aff_group[df_aff_group['group'].isin(groups)]

    # aggiunge i path/groups non presenti nel file a una lista
    present_paths = set(df_aff_exp['path'])
    present_group = set(df_aff_group['group'])
    for path in paths:
        if path not in present_paths:
            paths_to_add.append(path)
    for group in groups:
        if group not in present_group:
            groups_to_add.append(group)

    # aggiunge i nuovi dati ai df
    if paths_to_add:
        null_list = [None]*len(paths_to_add)
        df_to_concat = pd.DataFrame({
            'path' : paths_to_add,
            'group' : [idx.loc[idx['file_path']==path,'group'].values[0] for path in paths_to_add],
            'v0':null_list,
            '0':null_list,
            '15':null_list,
            '30':null_list,
        })
        pd.concat([df_aff_exp, df_to_concat], ignore_index=True)
    if groups_to_add:
        df_to_concat = pd.DataFrame({
            'group' : groups_to_add,
            'aff': [None]*len(groups_to_add),
        })
        pd.concat([df_aff_group, df_to_concat], ignore_index=True)

    # salva i nuovi df
    with pd.ExcelWriter(affinity_file) as writer:
        df_aff_exp.to_excel(writer, sheet_name='exp', index=False)
        df_aff_group.to_excel(writer, sheet_name='group', index=False)

    return None