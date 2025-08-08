from Common import *

## PARAMS ##
data_dir = Path('../../IdVd_data')
index_table_csv = data_dir/'index_table.csv'

## FUNCTIONS ##
def info_extract(file_path:Path)->list:
    info = np.array((file_path.stem.split('_'))) #es: IdVd_exponential_Vgf_2_Es_1.72_Em_1.04
    group = f"{info[1]}_{info[7]}_{info[5]}" #file group: TrapDistr_Em_Es
    return info[1],info[5],info[7],info[3],group,file_path # trap_distr:str, e_sigma:float, e_mid:float, v_gf:int, group:str, file_path:Path

## MAIN ##
def main()->None:
    files_list = list(Path(data_dir).glob('*.csv'))   #lista di tutti i file .csv nella data_dir
    files_list_str = set(str(f) for f in files_list)
    files_to_index:list[list] = []

    # controlla che il file degli indici esista, altrimenti lo crea
    if index_table_csv.exists():
        df_indexes = pd.read_csv(index_table_csv)
    else:
        df_indexes = pd.DataFrame(
            columns=[
                'trap_distr',
                'e_sigma',
                'e_mid',
                'v_gf',
                'group',
                'file_path'
            ]
        )

    # rimuove le righe con file non esistenti
    df_indexes = df_indexes[df_indexes['file_path'].isin(files_list_str)]

    # add not indexed files to a list
    indexed_files = set(df_indexes['file_path'])
    for file in files_list:
        if str(file) not in indexed_files:
            if file is not index_table_csv:
                files_to_index.append(info_extract(file))

    # aggiunge i nuovi dati a df_indexes
    if files_to_index:
        df_to_add = pd.DataFrame(files_to_index, columns=['trap_distr', 'e_sigma', 'e_mid', 'v_gf', 'group', 'file_path'])
        df_indexes = pd.concat([df_indexes, df_to_add], ignore_index=True)

    # salva df_indexes
    df_indexes.to_csv(index_table_csv, index=False)

    return None

#   !! ISSUES !!
# fare in modo che la tabella degli indici sia sempre aggiornata -> controllo boot, controllo aggiunte, controllo file cancellati