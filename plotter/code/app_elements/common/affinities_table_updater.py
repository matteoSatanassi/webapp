from plotter.code.app_elements import affinity_file
from pathlib import Path
import pandas as pd

## PARAMS ##
EXP_COLUMNS = ('file_path', 'group', 'v0', '0', '15', '30')
GROUP_COLUMNS = ('group', 'v0', '0', '15', '30')

## FUNC ##
def load_or_create_affinity_df(file_path: Path, sheet_name: str, columns: list) -> pd.DataFrame:
    """Carica o crea un dataframe di indice"""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except (FileNotFoundError, ValueError):
        return pd.DataFrame(columns=columns)

## MAIN FUNC ##
def affinities_table_updater(indexes_file: str | Path) -> None:
    """
    Aggiorna il file contenente i valori delle affinità dei vari esperimenti a partire dal file degli indici
    """
    # Params
    idx_file_path = Path(indexes_file)
    idx = pd.read_excel(idx_file_path, sheet_name='IdVd')   # rendo il file degli indici un df

    paths = set(idx['file_path'])
    groups = set(idx['group'].unique())

    paths_to_add = []
    groups_to_add = []

    # controlla che il file contenente i valori delle affinità esista, altrimenti crea un DataFrame vuoto
    df_aff_exp = load_or_create_affinity_df(affinity_file, 'exp', EXP_COLUMNS)
    df_aff_group = load_or_create_affinity_df(affinity_file, 'groups', GROUP_COLUMNS)

    # rimuove le righe con file/gruppi non esistenti
    df_aff_exp = df_aff_exp[df_aff_exp['file_path'].isin(paths)]
    df_aff_group = df_aff_group[df_aff_group['group'].isin(groups)]

    # aggiunge i path/groups non presenti nel file a una lista
    present_paths = set(df_aff_exp['file_path'])
    present_groups = set(df_aff_group['group'])
    for path in paths:
        if path not in present_paths:
            paths_to_add.append(path)
    for group in groups:
        if group not in present_groups:
            groups_to_add.append(group)

    # aggiunge i nuovi dati ai df
    if paths_to_add:
        df_to_concat = pd.merge(
            pd.DataFrame({'file_path': paths_to_add}),
            idx[['file_path', 'group']],
            on='file_path',
            how='left'
        )
        df_to_concat = df_to_concat.reindex(columns=EXP_COLUMNS)

        df_aff_exp = pd.concat([df_aff_exp, df_to_concat], ignore_index=True)

    if groups_to_add:
        df_to_concat = pd.DataFrame({
            'group' : groups_to_add,
        })
        df_to_concat = df_to_concat.reindex(columns=GROUP_COLUMNS)

        df_aff_group = pd.concat([df_aff_group, df_to_concat], ignore_index=True)

    # salva i nuovi df
    with pd.ExcelWriter(affinity_file) as writer:
        df_aff_exp.to_excel(writer, sheet_name='exp', index=False)
        df_aff_group.to_excel(writer, sheet_name='groups', index=False)

    return None