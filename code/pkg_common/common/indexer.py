from pathlib import Path
import pandas as pd
from common.classes import FilesFeatures
from params import *

## HELPER FUNC ##
def load_or_create_df_data_type(data_type:str, idx_file:Path):
    type_configs = load_files_info()[data_type]
    expected_df = add_aff_cols(
        data_type,
        pd.DataFrame(
            None,
            columns=list(type_configs["AllowedFeatures"].keys())
        )
    )

    try:
        idxs = pd.read_excel(idx_file, sheet_name=data_type)
        if set(idxs.columns)!=set(expected_df.columns):
            raise ValueError("Le feature contenute nel file non sono quelle specificate nei config")
        return idxs
    except Exception:
        return expected_df

def add_aff_cols(data_type:str, df:pd.DataFrame):
    type_configs = load_files_info()[data_type]
    if type_configs["TargetCurves"]==1:
        for curve in type_configs["AllowedCurves"]:
            df[f"aff_{curve}"] = None
    return df

## MAIN FUNC ##
def indexer(data_directory:str|Path)->list[Path]:
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
    # config params
    files_configs = load_files_info()

    # params
    data_directory = Path(data_directory)
    excel_indexes_file = data_directory / "indexes.xlsx"

    files_set = set(data_directory.glob("*.csv"))
    df_files = pd.DataFrame([
        {"file_type": f.stem.split("_")[0].upper(), "file_path": str(f)}
        for f in files_set
    ])

    # cache dict to save df before writing them
    df_to_save = {}

    # processing one supported data_type per loop
    for data_type, type_configs in files_configs.items():

        if data_type not in df_files["file_type"].tolist():
            continue

        # controlla che esista il file degli indici e in caso negativo crea un df vuoto
        df_data_type = load_or_create_df_data_type(data_type, excel_indexes_file)

        # rimuove le righe con file non esistenti
        df_data_type = df_data_type[df_data_type['file_path'].isin(files_set)]

        # add not indexed files to a list
        indexed_files = set(df_data_type['file_path'])
        rows = []   # vi aggiungerò le features dei file non indicizzati
        for f in df_files.loc[df_files["file_type"]==data_type]["file_path"]:
            if f not in indexed_files:
                rows.append(FilesFeatures.extract_features(f)[1])

        if rows:
            df_to_concat = add_aff_cols(data_type, pd.DataFrame(data=rows))

            df_to_save[data_type] = df_to_concat if df_data_type.empty else pd.concat([df_data_type, df_to_concat])

    # salvo i df alla fine del processo
    with pd.ExcelWriter(excel_indexes_file) as writer:
        for key, df in df_to_save.items():
            df.to_excel(writer, sheet_name=key, index=False)

if __name__ == "__main__":
    from params import data_dir
    indexer(data_dir)