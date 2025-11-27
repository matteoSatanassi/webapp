from pathlib import Path
from params import *


## COMMON CALLBACKS ##
def update_table(mode:str, grouping_feature:str, hidden_cols:list, table_data:dict, table_id:dict) -> dict:
    """
    Updater della tabella di visualizzazione dei file.

    Nel caso venga richiesto il raggruppamento dei dati da parte dell selettore, ricrea la tabella, raggruppando gli
    esperimenti secondo la feature grouping_feature, e calcolando le medie delle affinità, se presenti. Nella colonna
    degli indirizzi verranno salvate degli indirizzi dei file che fanno parte del gruppo sotto forma di stringhe, divisi
    da cancelletti (#).
    :param mode:
    :param grouping_feature:
    :param hidden_cols:
    :param table_data:
    :param table_id:
    :return:
    """
    if mode == "grouped":       # se l'impostazione era normal, posso anche usare i dati già caricati nella tabella
        df = pd.DataFrame(table_data)
        type_configs = load_files_info()[table_id["page"]]

        hidden_cols.append(grouping_feature)

        # Costruisco chiave del gruppo
        group_cols = [col for col in df.columns if col not in hidden_cols and "aff_" not in col]
        df["group_key"] = df[group_cols].astype(str).agg("_".join, axis=1)

        # Raggruppo
        groups = df.groupby("group_key")

        # Prendo una riga per gruppo
        df_out = groups.first().reset_index(drop=True)

        # raggruppo gli indirizzi dei file del gruppo in un'unica stringa
        df_out["file_path"] = groups["file_path"].agg(lambda x: "#".join(map(str, x))).values

        # Calcolo medie delle colonne affinità se presenti
        if type_configs["TargetCurves"] == 1:
            for curve in type_configs["AllowedCurves"]:
                aff_col = f"aff_{curve}"
                if aff_col in df.columns:
                    df_out[aff_col] = groups[aff_col].mean().values

        # Rimuovo colonna temporanea
        df_out = df_out.drop(columns=["group_key"])

        return df_out.to_dict("records"), hidden_cols, []
    elif mode == "grouped":
        df_out,_,cols_to_hide = get_table(table_id)
        return df_out.to_dict('records'), cols_to_hide, []
    elif not mode:
        return no_update, no_update, no_update
    else:
        raise ValueError(f"Il valore passato dal radio selector [{mode}], non è tra quelli supportati")


## HELPER FUNC ##
def explode_group_paths(string:str):
    """
    Data una stringa di indirizzi raggruppati, li esplode in una lista di oggetti Path

    Se la lista contiene un solo elemento ritorna cmq una lista con quell'unico elemento
    """
    from pathlib import Path
    return [Path(p) for p in string.split('#')]

def try_mkdir(path:Path)->Path:
    """
    Prova a creare la directory specificata
    :param path: indirizzo della directory da creare
    :type path: pathlib.Path
    :return: l'indirizzo della directory creata o None nel caso esistesse già
    :rtype: pathlib.Path or None
    :raises RuntimeError: Nel caso fosse impossibile creare la directory specificata
    """
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        return None
    except:
        raise RuntimeError(f"Impossibile creare {path}")
    return path

def find_export_path()->Path:
    """
    Crea un indirizzo di esportazione valido
    :return: Indirizzo di esportazione creato
    :rtype: pathlib.Path
    """
    export_dir = Path(load_configs()['export_directory'])
    i=0
    while True:
        export_path = try_mkdir(export_dir/'export' if i==0 else export_dir/f'export-{i}')
        if export_path:
          return export_path
        i+=1