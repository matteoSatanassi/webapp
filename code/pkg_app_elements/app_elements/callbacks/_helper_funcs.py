from pathlib import Path
from params import *


## COMMON CALLBACKS ##
def update_table(mode:str,
                 grouping_feature:str,
                 hidden_cols:list,
                 table_data:list[dict],
                 table_id:dict) -> list[dict]:
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
    from app_elements.page_elements import get_table
    from dash import no_update

    if mode == "grouped":       # se l'impostazione era normal, posso anche usare i dati già caricati nella tabella
        df_out, cols_to_hide = group_table(table_data, grouping_feature, table_id)
        return df_out.to_dict('records'), cols_to_hide, []
    elif mode == "normal":
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

def group_table(table_data:list[dict],
                grouping_feature:str,
                table_id:dict[str,str])->tuple:
    """
    Funzione chiamata per raggruppare i dati di una tabella in base alla feature di raggruppamento passata

    Ritorna anche la lista aggiornata delle colonne da nascondere
    """
    import pandas as pd

    df = pd.DataFrame(table_data)

    # ricavo le colonne da nascondere
    cols_to_hide = ["file_path", grouping_feature, *df.columns[df.isna().all()].tolist()]

    # Costruisco chiave del gruppo
    group_cols = [col for col in df.columns if col not in cols_to_hide and "aff_" not in col]
    df["group_key"] = df[group_cols].astype(str).agg("_".join, axis=1)

    # Raggruppo
    groups = df.groupby("group_key")

    # Prendo una riga per gruppo
    df_out = groups.first().reset_index(drop=True)

    # raggruppo gli indirizzi dei file del gruppo in un'unica stringa
    df_out["file_path"] = groups["file_path"].agg(lambda x: "#".join(map(str, x))).values

    # Calcolo medie delle colonne affinità se presenti
    type_configs = load_files_info()[table_id["page"]]
    if type_configs["TargetCurves"] == 1:
        for curve in type_configs["AllowedCurves"]:
            aff_col = f"aff_{curve}"
            if aff_col in df.columns:
                df_out[aff_col] = groups[aff_col].mean().values

    return df_out, cols_to_hide


# if __name__ == '__main__':
#     from app_elements.page_elements import get_table
#
#     table_id = {'page':'IDVD', 'item':'table', 'location':'dashboard'}
#     datas = get_table(table_id,
#                       only_df=True)
#
#     df_outt, cols_to_hidee, _ = update_table("grouped",
#                                              "Vgf",
#                                              [],
#                                              table_data=datas.to_dict('records'),
#                                              table_id=table_id)
#
#     print(df_outt)
#     print(cols_to_hidee)