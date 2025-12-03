from pathlib import Path


## COMMON CALLBACKS ##
def update_table(mode:str,
                 grouping_feature:str,
                 table_id:dict) -> list[dict]:
    """
    Updater della tabella di visualizzazione dei file.

    Nel caso venga richiesto il raggruppamento dei dati da parte dell selettore, ricrea la tabella, raggruppando gli
    esperimenti secondo la feature grouping_feature, e calcolando le medie delle affinità, se presenti. Nella colonna
    degli indirizzi verranno salvate degli indirizzi dei file che fanno parte del gruppo sotto forma di stringhe, divisi
    da cancelletti (#).
    :param mode:
    :param grouping_feature:
    :param table_id:
    :return:
    """
    from app_elements.page_elements import get_table
    from dash import no_update

    try:
        page = table_id['page']
    except KeyError:
        raise KeyError("Nell'id passato noon è specificata una pagina")

    if mode == "grouped":       # se l'impostazione era normal, posso anche usare i dati già caricati nella tabella
        df_out,_,cols_to_hide = get_table(table_id, grouping_feat=grouping_feature)
    elif mode == "normal":
        df_out,_,cols_to_hide = get_table(table_id)
    elif not mode:
        return no_update, no_update, no_update
    else:
        raise ValueError(f"Il valore passato dal radio selector [{mode}], non è tra quelli supportati")

    return df_out.to_dict('records'), cols_to_hide, []


## HELPER FUNC ##
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
    from app_resources import GLOBAL_CACHE

    export_dir = GLOBAL_CACHE.configs.export_dir
    i=0
    while True:
        export_path = try_mkdir(export_dir/'export' if i==0 else export_dir/f'export-{i}')
        if export_path:
          return export_path
        i+=1


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