import pandas as pd
from dash import Input, Output, State, callback, MATCH, no_update, dcc
from app_elements.page_elements import get_table, add_overall_aff
from app_elements.callbacks._helper_funcs import explode_group_paths, update_table, group_table
from common import FileCurves, plot
from params import *


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
    State({'page': MATCH, 'item': 'menu-grouping-features', 'location': 'dashboard'}, 'value'),
])
def add_tabs(n_clicks:int, selected_rows:list[int], table_data:dict, tabs:list[dcc.Tab], grouping_feature:str):
    """
    Aggiorna la lista dei tab al click del bottone, in base agli esperimenti selezionati nella tabella,
    e alla modalità di visualizzazione selezionata
    :return: la lista dei tab aggiornata, azzera la lista delle righe selezionate e imposta il tab da
    visualizzare dopo la callback
    """
    tabs = tabs or []
    if not n_clicks or not selected_rows:
        return no_update,no_update,no_update, no_update

    open_tabs = [tab['props']['value'] for tab in tabs]

    for selected_index in selected_rows:
        row = table_data[selected_index]

        if row['file_path'] not in open_tabs:
            path_list = explode_group_paths(row['file_path'])
            tab = create_tab(
                row['file_path'],
                FileCurves.from_paths(*path_list,
                                      grouping_feature=grouping_feature if len(path_list) > 1 else None)
            )
            tabs.append(tab)

    return tabs, table_data[selected_rows[0]]['file_path'], [], "tab-graphs"


@callback(
    [Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'data', allow_duplicate=True),
     Output({'page': MATCH, 'item': 'table', 'location': 'dashboard'}, 'hidden_columns', allow_duplicate=True)],
    Input({'page': MATCH, 'item': 'button-calculate-affinity'}, 'n_clicks'),
    [State({'page': MATCH, 'item': 'table', 'location':'dashboard'}, 'id'),
     State({'page': MATCH, 'item': 'table', 'location': 'dashboard'}, 'hidden_columns'),
     State({'page':MATCH, 'item':'radio-table-mode', 'location':'dashboard'}, 'value'),
     State({'page':MATCH, 'item':'menu-grouping-features', 'location':'dashboard'}, 'value')],
    prevent_initial_call=True
)
def affinity_calc(n_clicks:int, table_id:dict, hidden_cols:list, mode:str, grouping_feature:str):
    """
    Calcola le percentuali di affinità di ogni esperimento presente nei dati, salva i dati ricavati
    nel file preposto e li visualizza direttamente nella tabella di pagina,
    in base alla modalità di visualizzazione attuale.
    """
    if not n_clicks:
        return no_update, no_update

    # recupero la tabella dal file di indicizzazione
    page_df = get_table(table_id, only_df=True)

    feature_cols = [col for col in page_df.columns if "aff_" not in col]

    # carico il df in un'istanza FileCurves, in modo da calcolarmi le affinità
    page_data = FileCurves.from_df(page_df[feature_cols])

    page_df_out = pd.DataFrame(page_data.calculate_affinities(autosave=True))
    page_df_out['file_path'] = page_df_out['file_path'].astype(str)

    aff_cols = [col for col in page_df_out.columns if "aff_" in col]
    for col in aff_cols:
        if col in hidden_cols: hidden_cols.remove(col)

    # salvo il df risultante, con i valori delle affinità, nel file degli indici
    with pd.ExcelWriter(indexes_file) as writer:
        page_df_out.to_excel(writer, sheet_name=table_id['page'], index=False)

    page_df_out = add_overall_aff(page_df_out)

    if mode=="normal":
        pass
    elif mode=="grouped":
        page_df_out, hidden_cols = group_table(page_df_out.to_dict('records'),
                                               grouping_feature=grouping_feature,
                                               table_id=table_id)
    else:
        raise ValueError(f"Il valore passato dal radio selector [{mode}], non è tra quelli supportati")

    return page_df_out.to_dict('records'), hidden_cols


## HELPER FUNCS ##
def create_tab(tab_value:str, tab_data:FileCurves)->dcc.Tab:
    """
    Dati i parametri richiesti, crea il corrispondete Tab.

    Il valore del Tab sarà il path del file, nel caso tab_data ne contenga solo uno,
    mentre, nel caso ne contenga più di uno, gli indirizzi saranno concatenati e divisi
    da caratteri '#'
    """
    return dcc.Tab(
        value=tab_value,
        label=tab_data.get_tab_label(),
        children=dcc.Graph(figure=plot(tab_data)),
        style={'fontSize': 8, 'left-margin': '2px'},
    )

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