"""
Il modulo implementa la funzione di indexing da utilizzare sulla directory dei dati,
in modo da creare un file di indicizzazione con i parametri dei vari file supportati
dall'applicazione
"""

from pathlib import Path
import pandas as pd
from common.classes import FilesFeatures
from app_resources.parameters import ConfigCache


## HELPER FUNC ##
def load_or_create_df_data_type(file_type:str, idx_file:Path):
    type_configs = ConfigCache.get_f_configs(file_type)
    expected_df = pd.DataFrame(
        None,
        columns=type_configs.get_table_cols
        )

    try:
        idxs = pd.read_excel(idx_file, sheet_name=file_type)
        if set(idxs.columns)!=set(expected_df.columns):
            raise ValueError("Le feature contenute nel file non sono quelle specificate nei config")
        return idxs
    except Exception:
        return expected_df

def add_aff_cols(data_type:str, df:pd.DataFrame):
    type_configs = ConfigCache.get_f_configs(data_type)
    if type_configs.targets_presents:
        df["aff_tot"]=None
        for curve in type_configs.allowed_curves:
            df[f"aff_{curve}"] = None
    return df

## MAIN FUNC ##
def indexer(data_directory:str|Path):
    """
    La funzione di occupa di indicizzare tutti i file .csv contenuti nella cartella
    specificata, data_directory, creando un corrispondente file nella suddetta.

    Nel caso un file di indicizzazione sia già presente, esso verrà solamente aggiornato,
    aggiungendo file nuovi, eliminando i file non più presenti e aggiungendo le feature non
    presenti, nel caso venissero aggiunte.

    Sono considerati solo i file il cui data_type appare nel file di configurazione.
    Sono estratte quindi tutte le feature utili contenute nel nome, tralasciando quelle
    non specificate nel file di configurazione, e lasciando vuote quelle non specificate
    nel nome del file.

    In caso sia supportata il calcolo dell'affinità per un certo data_type, vengono aggiunte
    colonne preposte a contenere tali dati, nel caso non fossero già presenti, con nomi
    del tipo "aff_<curve_acronym>"

    :param data_directory:
    :return:
    """
    # params
    data_directory = Path(data_directory)
    excel_indexes_file = data_directory / "indexes.xlsx"

    files_set = set(str(p) for p in data_directory.glob("*.csv"))

    files_data_list = []
    for file in files_set:
        try:
            file_type = FilesFeatures.extract_features(file, only_file_type=True)
        except KeyError:
            # ignoro i file con un tipo non supportato
            pass
        else:
            files_data_list.append(
                {
                    "file_type": file_type,
                    "file_path":str(file)
                }
            )

    df_files = pd.DataFrame(files_data_list)

    if df_files.empty:
        return []

    present_file_types = set(df_files["file_type"].tolist())

    # cache dict to save df before writing them
    df_to_save = {}

    # processing one supported data_type per loop
    for file_type in ConfigCache.file_types:

        if file_type not in present_file_types:
            continue

        # controlla che esista il file degli indici e in caso negativo crea un df vuoto
        df_data_type = load_or_create_df_data_type(file_type, excel_indexes_file)

        df_to_save[file_type] = df_data_type

        # rimuove le righe con file non esistenti
        df_data_type = df_data_type[df_data_type['file_path'].isin(files_set)]

        # add not indexed files to a list
        indexed_files:set[str] = set(df_data_type['file_path'].tolist())
        rows = []   # vi aggiungerò le features dei file non indicizzati

        # gli indirizzi da controllare sono tutti quelli con lo stesso data_type di df_data_type
        df_paths_to_check:pd.DataFrame = df_files.loc[df_files["file_type"] == file_type, "file_path"]
        # creo una maschera con i file presenti in indice, che poi negherò per trovare i non presenti
        mask_indexed =df_paths_to_check.isin(indexed_files)
        for f in df_paths_to_check[~mask_indexed]:
            rows.append(FilesFeatures.extract_features(f, only_file_features=True))

        if rows:
            df_to_concat = add_aff_cols(file_type, pd.DataFrame(data=rows))

            df_to_save[file_type] = df_to_concat if df_data_type.empty else pd.concat([df_data_type, df_to_concat])

    # salvo i df alla fine del processo
    with pd.ExcelWriter(excel_indexes_file) as writer:
        for key, df in df_to_save.items():
            df.to_excel(writer, sheet_name=key, index=False)

    return None


if __name__ == "__main__":
    data_dir = Path(
        r'C:\Users\user\Documents\Uni\Tirocinio\webapp\data'
    )

    indexer(data_dir)