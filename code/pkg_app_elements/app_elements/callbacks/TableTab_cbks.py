from dash import Input, Output, State, callback, MATCH, no_update, dcc
from app_elements.callbacks._helper_funcs import update_table


## DYNAMIC CALLBACKS ##

callback([
    Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'data'),
    Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'hidden_columns'),
    Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'selected_rows', allow_duplicate=True)],
    Input({'page':MATCH, 'item':'radio-table-mode', 'location':'dashboard'}, 'value'),
    [State({'page':MATCH, 'item':'menu-grouping-features', 'location':'dashboard'}, 'value'),
    State({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'hidden_columns'),
    State({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'data'),
    State({'page': MATCH, 'item': 'table', 'location': 'dashboard'}, 'id')],
    prevent_initial_call=True
)(update_table)


@callback([
    Output({'page':MATCH, 'item': 'graph-tabs'}, 'children'),
    Output({'page':MATCH, 'item': 'graph-tabs'}, 'value'),
    Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'selected_rows'),
    Output({'page': MATCH, 'item': 'main-tabs'}, 'active_tab')],
    Input({'page': MATCH, 'item': 'button-plot'}, 'n_clicks'),
    [State({'page': MATCH, 'item': 'table', 'location': 'dashboard'}, 'derived_virtual_selected_rows'),
    State({'page': MATCH, 'item': 'table', 'location': 'dashboard'}, 'derived_virtual_data'),
    State({'page': MATCH, 'item': 'graph-tabs'}, 'children'),
])
def add_tabs(n_clicks:int, selected_rows:list[int], table_data:dict, tabs:list[dcc.Tab]):
    """
    Aggiorna la lista dei tab al click del bottone, in base agli esperimenti selezionati nella tabella,
    e alla modalità di visualizzazione selezionata.

    I nuovi dati dei tab sono salvati nella memoria cache, CACHE_GLOBAL

    :return: la lista dei tab aggiornata, azzera la lista delle righe selezionate e imposta il tab da
    visualizzare dopo la callback
    """
    tabs = tabs or []
    if not n_clicks or not selected_rows:
        return no_update,no_update,no_update,no_update

    from app_resources.AppCache import GLOBAL_CACHE

    open_tabs = [tab['props']['value'] for tab in tabs]

    for selected_index in selected_rows:
        row = table_data[selected_index]

        if row['file_path'] not in open_tabs:
            # salvo il nuovo valore Tab nella cache e ritorno l'oggetto dcc.Tab di cui ho bisogno
            tab = GLOBAL_CACHE.tab(row['file_path']).build_dcc_tab()
            tabs.append(tab)

    return tabs, table_data[selected_rows[0]]['file_path'], [], "tab-graphs"


@callback(
    [Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'data', allow_duplicate=True),
     Output({'page': MATCH, 'item': 'table', 'location': 'dashboard'}, 'hidden_columns', allow_duplicate=True)],
    Input({'page': MATCH, 'item': 'button-calculate-affinity'}, 'n_clicks'),
    [State({'page': MATCH, 'item': 'table', 'location':'dashboard'}, 'id'),
     State({'page':MATCH, 'item':'radio-table-mode', 'location':'dashboard'}, 'value'),
     State({'page':MATCH, 'item':'menu-grouping-features', 'location':'dashboard'}, 'value')],
    prevent_initial_call=True
)
def affinity_calc(n_clicks:int, table_id:dict, mode:str, grouping_feature:str):
    """
    Calcola le percentuali di affinità di ogni esperimento presente nei dati, salva i dati ricavati
    nel file preposto e li visualizza direttamente nella tabella di pagina,
    in base alla modalità di visualizzazione attuale.
    """
    if not n_clicks:
        return no_update, no_update

    from app_resources.AppCache import GLOBAL_CACHE

    file_type = table_id['page']
    page_df_out = GLOBAL_CACHE.calculate_affinities(file_type)

    if mode=="normal":
        cols_to_hide = GLOBAL_CACHE.cols_to_hide(page_df_out)
    elif mode=="grouped":
        page_df_out, hidden_cols = GLOBAL_CACHE.group_df(file_type,
                                                         grouping_feature)
    else:
        raise ValueError(f"Il valore passato dal radio selector [{mode}], non è tra quelli supportati")

    # noinspection PyUnboundLocalVariable
    return page_df_out.to_dict('records'), cols_to_hide


## DEBUG ##
if __name__ == '__main__':
    pass
    # df = get_table({'page':"IDVD", 'item':'table', 'location':'dashboard'}, only_df=True)
    #
    # cols = [col for col in df.columns if "aff_" not in col]
    #
    # data = FileCurves.from_df(df[cols])
    #
    # df_out = pd.DataFrame(data.calculate_affinities(autosave=True))
    #
    # print("ciao")