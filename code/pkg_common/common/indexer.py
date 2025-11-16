from pathlib import Path
import pandas as pd
import numpy as np
from params import *
## PARAMS ##
IDVD_COLUMNS = ('trap_distr', 'e_sigma', 'e_mid', 'v_gf', 'group', 'file_path')
TRAPDATA_COLUMNS = ('trap_distr', 'e_sigma', 'e_mid', 'v_gf', 'start_cond', 'file_path')

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
    ['exponential', 1.72, 1.04, 2, 'IdVd_exponential_Em_1.04_Es_1.72', '../IdVd_exponential_Vgf_2_Es_1.72_Em_1.04.csv']
    >>> info_extract('../TrapData_exponential_Vgf_0_Es_1.72_Em_0.18_(0,0).csv')
    ['exponential', 1.72, 0.18, 0, 'v0', '../TrapData_exponential_Vgf_0_Es_1.72_Em_0.18_(0,0).csv']
    """
    info = np.array((file_path.stem.split('_'))) #es: IdVd_exponential_Vgf_2_Es_1.72_Em_1.04
    if info[0] == 'IdVd':
        group = f"IdVd_{info[1]}_Em_{info[7]}_Es_{info[5]}"
        return info[1],info[5],info[7],info[3],group,str(file_path)
    else:
        return info[1],info[5],info[7],info[3],info[8],str(file_path)

def save_indexes(df_idvd:pd.DataFrame, df_trap:pd.DataFrame, output_file:Path)->None:
    """
    Salva i dataframe degli indici nel file excel specificato
    :param df_idvd: dataframe indici IdVd
    :param df_trap: dataframe indici TrapData
    :param output_file: indirizzo del file excel
    :return: None
    """
    with pd.ExcelWriter(output_file) as writer:
        df_idvd.to_excel(writer, sheet_name='IdVd', index=False)
        df_trap.to_excel(writer, sheet_name='TrapData', index=False)

def load_or_create_index(file_path: Path, sheet_name: str, columns: list) -> pd.DataFrame:
    """Carica o crea un dataframe di indice"""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df['file_path'] = df['file_path'].apply(Path)   # rendo i valori della colonna dei Path invece che stringhe
        return df
    except (FileNotFoundError, ValueError):
        return pd.DataFrame(columns=columns)

def process_new_file(file: Path) -> tuple:
    """
    Elabora un singolo file
    :param file: indirizzo del file
    :type file: pathlib.Path
    :return: tuple
    """
    # controlla che il nome del file sia supportato
    if not is_valid_filename(file):
        return None, None

    data = info_extract(file)
    return 'IdVd' if 'IdVd' in file.name else 'TrapData', data

def update_dataframe(df:pd.DataFrame, rows_to_add:list, columns:list) -> pd.DataFrame:
    """
    Concatena un df con una lista di righe
    :param df: dataframe a cui concatenare le nuove righe
    :param rows_to_add: lista di righe da aggiungere
    :param columns: lista di colonne del df
    :return: il df con le nuove righe in fondo
    """
    df_to_concat = pd.DataFrame(rows_to_add, columns=columns)
    return pd.concat([df, df_to_concat], ignore_index=True)

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
    excel_indexes_file = data_dir / "indexes.xlsx"

    files_set = set(data_dir.glob('*.csv'))  # set di tutti i file .csv nella data_dir
    files_df = pd.DataFrame([{
        "file_type": file.stem.split('_')[0].upper(), "file_path": str(file),
    } for file in files_set])

    files_to_index = {'IdVd':[],'TrapData':[]}
    unsupported_files: list[Path] = []

    for FileType in load_files_info().keys():

    # controlla che il file degli indici esista, altrimenti crea il DataFrame
    df_indexes_IdVd = load_or_create_index(excel_indexes_file, 'IdVd', IDVD_COLUMNS)
    df_indexes_TrapData = load_or_create_index(excel_indexes_file, 'TrapData', TRAPDATA_COLUMNS)

    # rimuove le righe con file non esistenti
    df_indexes_IdVd = df_indexes_IdVd[df_indexes_IdVd['file_path'].isin(files_set)]
    df_indexes_TrapData = df_indexes_TrapData[df_indexes_TrapData['file_path'].isin(files_set)]

    # add not indexed files to a list
    indexed_files = set(df_indexes_IdVd['file_path']) | set(df_indexes_TrapData['file_path'])
    for file in files_set:
        if file not in indexed_files:
            file_type, file_data = process_new_file(file)
            if file_data:
                files_to_index[file_type].append(file_data)
            else:
                unsupported_files.append(file)

    # aggiunge i nuovi dati a df_indexes
    if files_to_index['IdVd']:
        df_indexes_IdVd = update_dataframe(df_indexes_IdVd, files_to_index['IdVd'], IDVD_COLUMNS)
    if files_to_index['TrapData']:
        df_indexes_TrapData = update_dataframe(df_indexes_TrapData, files_to_index['TrapData'], TRAPDATA_COLUMNS)

    # salva df_indexes
    save_indexes(df_indexes_IdVd, df_indexes_TrapData, excel_indexes_file)

    # stampa un log dei file con nomi non supportati se ce ne sono
    if unsupported_files:
        print("Files non indicizzati:\n" + "\n".join(map(str, unsupported_files)))

    return unsupported_files

fileName_pattern = re.compile(
    r"^(IdVd|TrapData)_"            # inizia con IdVd_ o TrapData_
    r"(exponential|gaussian|uniform|level)_"  # distribuzione
    r"Vgf_-?\d+_"                   # Vgf_ seguito da intero (può essere negativo)
    r"Es_\d+(\.\d+)?_"               # Es_ seguito da numero (con o senza decimali)
    r"Em_\d+(\.\d+)?"                # Em_ seguito da numero (con o senza decimali)
    r"(_\(-?\d+,-?\d+\))?$"              # opzionale _(x,y) per TrapData
)