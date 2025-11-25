import pandas as pd
from dash import Input, Output, State, callback, MATCH, no_update, dcc
from app_elements.page_elements import get_table
from params import *
from common import FileCurves, plot


## DYNAMIC CALLBACKS ##
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

callback(
    Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'data'),
    Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'hidden_columns'),
    Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'selected_rows', allow_duplicate=True),
    Input({'page':MATCH, 'item':'radio-table-mode', 'location':'dashboard'}, 'value'),
    State({'page':MATCH, 'item':'menu-grouping-features', 'location':'dashboard'}, 'value'),
    State({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'hidden_columns'),
    State({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'data'),
    State({'page': MATCH, 'item': 'table', 'location': 'dashboard'}, 'id'),
    prevent_initial_call=True
)(update_table)

callback(
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'data'),
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'hidden_columns'),
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows', allow_duplicate=True),
    Input({'page':MATCH, 'item':'radio-table-mode', 'location':'modal'}, 'value'),
    State({'page':MATCH, 'item':'menu-grouping-features', 'location':'modal'}, 'value'),
    State({'page':MATCH, 'item':'table', 'location':'modal'}, 'hidden_columns'),
    State({'page':MATCH, 'item':'table', 'location':'modal'}, 'data'),
    State({'page': MATCH, 'item': 'table', 'location': 'modal'}, 'id'),
    prevent_initial_call=True
)(update_table)


@callback([
    Output({'page':MATCH, 'item': 'graph-tabs'}, 'children'),
    Output({'page':MATCH, 'item': 'graph-tabs'}, 'value'),
    Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'selected_rows'),
    Input({'page': MATCH, 'item': 'button-plot'}, 'n_clicks'),
    State({'page': MATCH, 'item': 'table', 'location': 'dashboard'}, 'derived_virtual_selected_rows'),
    State({'page': MATCH, 'item': 'table', 'location': 'dashboard'}, 'derived_virtual_data'),
    State({'page': MATCH, 'item': 'graph-tabs'}, 'children'),
    State({'page': MATCH, 'item': 'menu-grouping-features', 'location': 'modal'}, 'value'),
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
        return no_update,no_update,no_update

    open_tabs = [tab['props']['value'] for tab in tabs]

    for selected_index in selected_rows:
        row = table_data[selected_index]

        if row['file_path'] not in open_tabs:
            path_list = explode_group_paths(row['file_path'])
            data = FileCurves.from_paths(*path_list,
                                         grouping_feature=grouping_feature if len(path_list)>1 else None)
            tabs.append(create_tab(row["file_path"],data))

    return tabs, table_data[selected_rows[0]]['file_path'], []


callback(
    Output({'page':MATCH, 'item':'main-tabs'}, 'active_tab'),
    Input({'page':MATCH, 'item':'button-plot', 'location':'dashboard'}, 'n_clicks'),
    State({'page': MATCH, 'item': 'table', 'location':'dashboard'}, 'selected_rows'),
    prevent_initial_call=True
)
def switch_to_graphs_tab(n_clicks, selected_rows):
    """
    Passa alla tab dei grafici quando si clicca su "Genera Grafico", se almeno
    una riga della tabella è stata selezionata
    """
    if n_clicks and selected_rows:
        return "tab-graphs"
    return "tab-table"


@callback(
    Output({'page':MATCH, 'item':'table', 'location':'dashboard'}, 'data', allow_duplicate=True),
    Input({'page': MATCH, 'item': 'button-calculate-affinity'}, 'n_clicks'),
    State({'page': MATCH, 'item': 'table', 'location':'dashboard'}, 'id'),
    State({'page':MATCH, 'item':'radio-table-mode', 'location':'dashboard'}, 'value'),
    prevent_initial_call=True
)
def affinity_calc(n_clicks:int, table_id:dict, mode:str):
    """
    Calcola le percentuali di affinità di ogni esperimento presente nei dati, salva i dati ricavati
    nel file preposto e li visualizza direttamente nella tabella di pagina.
    """
    if not n_clicks:
        return no_update

    # recupero la tabella dal file di indicizzazione
    page_df = get_table(table_id, only_df=True)

    # carico il df in un'istanza FileCurves, in modo da calcolarmi le affinità
    page_data = FileCurves.from_df(page_df)

    page_df_out = pd.DataFrame(page_data.calculate_affinities(autosave=True))

    # salvo il df risultante, con i valori delle affinità, nel file degli indici
    with pd.ExcelWriter(indexes_file) as writer:
        page_df_out.to_excel(writer, sheet_name=table_id['page'], index=False)

    return page_df_out.to_dict('records')


## HELPER FUNCS ##
def explode_group_paths(string:str):
    """
    Data una stringa di indirizzi raggruppati, li esplode in una lista di oggetti Path

    Se la lista contiene un solo elemento ritorna cmq una lista con quell'unico elemento
    """
    from pathlib import Path
    return [Path(p) for p in string.split('#')]

def create_tab(tab_value:str, data:FileCurves)->dcc.Tab:
    """Dati i parametri richiesti, crea il corrispondete Tab"""
    return dcc.Tab(
        value=tab_value,
        label=data.get_tab_label(),
        children=[plot(data)],
        style={'fontSize': 8, 'left-margin': '2px'},
    )

## DEBUG ##
if __name__ == '__main__':
    df = get_table({'page':"IDVD", 'item':'table', 'location':'dashboard'}, only_df=True)

    cols = [col for col in df.columns if "aff_" not in col]

    data = FileCurves.from_df(df[cols])

    df_out = pd.DataFrame(data.calculate_affinities(autosave=True))

    print("ciao")