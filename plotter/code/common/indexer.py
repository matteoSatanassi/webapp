from pathlib import Path
from Common import toggle
import pandas as pd
import numpy as np
import re

## HELPER FUNC ##
def is_valid_filename(file_path:Path)->bool:
    """
    Controlla che il nome del file sia supportato dall'applicazione
    :param file_path: indirizzo del file
    :type file_path: pathlib.Path
    :return: True/False
    :rtype: bool
    """
    return bool(fileName_pattern.match(file_path.stem))

def info_extract(file_path:Path)->list:
    """
    Estrae le informazioni contenute nel nome di un file esperimento
    :param file_path: indirizzo del file
    :type file_path: pathlib.Path
    :return: lista con i dati dell'esperimento
    :rtype: list
    :example:
    >>> info_extract('../IdVd_exponential_Vgf_2_Es_1.72_Em_1.04.csv')
    ['exponential', 1.72, 1.04, 2, 'exponential_1.04_1.72', '../IdVd_exponential_Vgf_2_Es_1.72_Em_1.04.csv']
    >>> info_extract('../TrapData_exponential_Vgf_0_Es_1.72_Em_0.18_(0,0).csv')
    ['exponential', 1.72, 0.18, 0, 'v0', '../TrapData_exponential_Vgf_0_Es_1.72_Em_0.18_(0,0).csv']
    """
    info = np.array((file_path.stem.split('_'))) #es: IdVd_exponential_Vgf_2_Es_1.72_Em_1.04
    if info[0] == 'IdVd':
        group = f"{info[1]}_{info[7]}_{info[5]}"
        return info[1],info[5],info[7],info[3],group,file_path
    else:
        return info[1],info[5],info[7],info[3],toggle(info[8]),file_path

## MAIN FUNC ##
def indexer(data_dir: str | Path) -> list[Path]:
    """
    Data una cartella di file .csv di dati crea un file indice utile al funzionamento dell'applicazione
    :param data_dir: indirizzo della directory da indicizzare
    :type data_dir: pathlib.Path
    :return: lista di file con nomi non supportati
    :rtype: list[Path]
    """
    # Params
    data_dir = Path(data_dir)
    indexes_table_csv = data_dir / "index_table.csv"

    files_list = list(data_dir.glob('*.csv'))  # lista di tutti i file .csv nella data_dir
    files_list_str = set(str(f) for f in files_list)
    files_to_index: list[list] = []
    unsupported_files: list[Path] = []

    # controlla che il file degli indici esista, altrimenti lo crea
    if indexes_table_csv.exists():
        df_indexes = pd.read_csv(indexes_table_csv)
    elif 'IdVd' in str(data_dir):
        df_indexes = pd.DataFrame(columns=['trap_distr', 'e_sigma', 'e_mid', 'v_gf', 'group', 'file_path'])
    elif 'TrapDistr' in str(data_dir):
        df_indexes = pd.DataFrame(columns=['trap_distr', 'e_sigma', 'e_mid', 'v_gf', 'start_cond', 'file_path'])

    # rimuove le righe con file non esistenti
    df_indexes = df_indexes[df_indexes['file_path'].isin(files_list_str)]

    # add not indexed files to a list
    indexed_files = set(df_indexes['file_path'])
    for file in files_list:
        if str(file) not in indexed_files:
            if file != indexes_table_csv:
                if is_valid_filename(file):
                    files_to_index.append(info_extract(file))
                else:
                    unsupported_files.append(file)

    # aggiunge i nuovi dati a df_indexes
    if files_to_index:
        df_to_add = pd.DataFrame(files_to_index,
                                 columns=['trap_distr', 'e_sigma', 'e_mid', 'v_gf', 'group', 'file_path'])
        df_indexes = pd.concat([df_indexes, df_to_add], ignore_index=True)

    # salva df_indexes
    df_indexes.to_csv(indexes_table_csv, index=False)

    # stampa un log dei file con nomi non supportati se ce ne sono
    if unsupported_files:
        print('Files non indicizzati:',*unsupported_files,sep=', ')

    return unsupported_files

fileName_pattern = re.compile(
    r"^(IdVd|TrapData)_"            # inizia con IdVd_ o TrapData_
    r"(exponential|gaussian|uniform)_"  # distribuzione
    r"Vgf_-?\d+_"                   # Vgf_ seguito da intero (può essere negativo)
    r"Es_\d+(\.\d+)?_"               # Es_ seguito da numero (con o senza decimali)
    r"Em_\d+(\.\d+)?"                # Em_ seguito da numero (con o senza decimali)
    r"(_\(\d+,\d+\))?$"              # opzionale _(x,y) per TrapData
)