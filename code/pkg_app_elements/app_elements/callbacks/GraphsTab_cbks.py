"""
Questo modulo contiene tutte le funzioni callback che agiscono sugli elementi del tab
grafici, all'interno dell'applicazione
"""

from dash import dcc, Input, Output, State, callback, MATCH, ALL, no_update, callback_context
from app_resources.AppCache import GLOBAL_CACHE
import dash_bootstrap_components as dbc

## DYNAMIC CALLBACKS ##
@callback(
    [Output({'page':MATCH, 'item':'graph-tabs'}, 'children', allow_duplicate=True),
    Output({'page': MATCH, 'item': 'graph-tabs'}, 'value', allow_duplicate=True)],
    Input({'page':MATCH, 'item':'main-tabs'}, 'active_tab'),
    [State({'page':MATCH, 'item':'graph-tabs'}, 'children'),
    State({'page':MATCH, 'item':'graph-tabs'}, 'id')],
    prevent_initial_call=True
)
def reload_tabs(main_tab:str, tabs:list[dcc.Tab], tabs_id:dict[str,str]):
    """Ricarica i tab dalla memoria cache, in caso non siano più visualizzati"""
    if not main_tab or main_tab == "tab-table":
        return no_update, no_update

    file_type = tabs_id['page']

    tabs_values = {tab['props']['value'] for tab in tabs}

    cached_tabs_values = set(GLOBAL_CACHE.open_tabs[file_type].tabs_values)

    if tabs_values == cached_tabs_values:
        return no_update, no_update

    return ([GLOBAL_CACHE.open_tabs[file_type].tab(path_val).build_dcc_tab()
             for path_val in cached_tabs_values if path_val not in tabs_values],
            list(cached_tabs_values)[0])


@callback([
    Output({'page' :MATCH, 'item' :'button-close-current-tab'}, 'style'),
    Output({'page': MATCH, 'item': 'graph-controls'}, 'style'),
    Output({'page' :MATCH, 'item' :'menu-tab-management'}, 'style'),
    Output({'page' :MATCH, 'item' :'menu-tab-management'}, 'children')],
    Input({'page' :MATCH, 'item': 'graph-tabs'}, 'children'),
    State({'page' :MATCH, 'item': 'graph-tabs'}, 'id'),
)
def graph_buttons_displayer(tabs :list[dcc.Tab], tabs_id :dict[str ,str]):
    """
    Callback che permette di visualizzare i pulsanti di gestione dei tab.

    Quando è presente un unico tab viene visualizzato il pulsante di
    chiusura del tab corrente.

    Quando sono presenti più tab viene visualizzato anche il menù di
    chiusura a tendina con tutti i tab presenti al momento.
    """
    if not tabs:
        return no_update, no_update, no_update, no_update
    if len(tabs) == 1:
        return {'display': 'block'}, {'display': 'block'}, {'display': 'none'}, None

    page = tabs_id['page']
    dropdown_elems = [
        dbc.DropdownMenuItem(
            f"❌ {tab['props']['label']}",
            id={'page' :page, 'item' :'dd-button', 'tab-index' :i},
        ) for i, tab in enumerate(tabs)]
    return {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, dropdown_elems


@callback([
    Output({'page':MATCH, 'item': 'graph-tabs'}, 'children', allow_duplicate=True),
    Output({'page':MATCH, 'item': 'graph-tabs'}, 'value', allow_duplicate=True)],
    Input({'page':MATCH, 'item':'button-close-current-tab'}, 'n_clicks'),
    [State({'page':MATCH, 'item': 'graph-tabs'}, 'value'),
     State({'page':MATCH, 'item': 'graph-tabs'}, 'children'),
     State({'page':MATCH, 'item': 'graph-tabs'}, 'id')],
    prevent_initial_call=True
)
def close_current_tab(n_clicks:int, active_tab:str, tabs:list[dcc.Tab], tabs_id:dict[str,str]):
    """Chiude il tab correntemente aperto"""
    if not n_clicks or not tabs or not active_tab:
        return no_update, no_update

    file_type = tabs_id['page']

    # elimino i dati del tab dalla memoria cache
    GLOBAL_CACHE.open_tabs[file_type].del_tab(active_tab)

    if len(tabs) == 1:
        return [], None

    tab_values = [tab['props']['value'] for tab in tabs]
    tab_index = tab_values.index(active_tab)
    try:
        next_tab = tab_values[tab_index + 1]
    except IndexError:
        next_tab = tab_values[tab_index-1]

    tabs = [tab for tab in tabs if tab['props']['value']!=active_tab]

    return tabs, next_tab


@callback([
    Output({'page':MATCH, 'item': 'graph-tabs'}, 'children', allow_duplicate=True),
    Output({'page':MATCH, 'item': 'graph-tabs'}, 'value', allow_duplicate=True)],
    Input({'page':MATCH, 'item':'dd-button', 'tab-index':ALL}, 'n_clicks'),
    [State({'page':MATCH, 'item': 'graph-tabs'}, 'children'),
     State({'page':MATCH, 'item': 'graph-tabs'}, 'value'),
     State({'page':MATCH, 'item': 'graph-tabs'}, 'id')],
    prevent_initial_call=True
)
def pop_tab(n_clicks_list:list[int], tabs:list[dcc.Tab], open_tab:str, tabs_id:dict[str,str]):
    """Callback che gestisce la chiusura di un tab da parte di un pulsante del dropdown menu"""
    ctx = callback_context
    if not ctx.triggered or not tabs or not open_tab:
        return no_update, no_update

    if not any(n_clicks_list):
        return no_update, no_update

    triggered_id = ctx.triggered_id  # Trova l'id del pulsante appena cliccato
    if triggered_id != '.': # controlla che un componente abbia effettivamente chiamato la callback
        try:
            tab_index = triggered_id['tab-index']
            if len(tabs)>1:
                try:
                    open_tab = tabs[tab_index+1]['props']['value']
                except IndexError:
                    open_tab = tabs[tab_index-1]['props']['value']

            # se è presente un solo tab non devo specificare nulla perchè il
            # menù di chiusura non compare nella schermata

            if 0 <= tab_index < len(tabs):
                tabs.pop(tab_index)

                file_type = tabs_id['page']
                GLOBAL_CACHE.open_tabs[file_type].del_tab(tabs[tab_index]['props']['value'])

                return tabs, open_tab

        except (KeyError, IndexError):
            pass
    return tabs, open_tab


@callback(
    Output({'page':MATCH, 'item': 'store-placeholder-graph-tab'}, 'data'),
    Input({'page': MATCH, 'item': 'button-export-current-graph'}, 'n_clicks'),
    [State({'page':MATCH, 'item': 'graph-tabs'}, 'value'),
     State({'page':MATCH, 'item': 'graph-tabs'}, 'id'), ],
    prevent_initial_call=True
)
def export_current(n_clicks:int, curr_tab:str, tabs_id:dict[str,str]):
    """Esporta il grafico contenuto nel tab aperto, con parametri di esportazione come da config"""
    if not n_clicks or not curr_tab:
        return no_update, no_update

    file_type = tabs_id['page']
    out = GLOBAL_CACHE.open_tabs[file_type].save_tab(curr_tab)

    return out


@callback(
    Output({'page':MATCH, 'item': 'graph-tab', 'tab':ALL}, 'figure'),
    Input({'page':MATCH, 'item':'button-target-visualize'}, 'n_clicks'),
    [State({'page':MATCH, 'item': 'graph-tabs'}, 'value'),
     State({'page':MATCH, 'item': 'graph-tabs'}, 'id'),
     State({'page':MATCH, 'item': 'graph-tab', 'tab':ALL}, 'id'),
     State({'page':MATCH, 'item': 'graph-tab', 'tab':ALL}, 'figure')],
    prevent_initial_call=True
)
def plot_targets(n_clicks:int, curr_tab:str, tabs_id:dict[str,str],
                 graphs_ids:list[dict[str,str]], graphs_figs:list):
    """
    La callback si occupa di stampare le curve target nel tab aperto,
    in caso non siano già presenti, alla pressione dell'apposito pulsante.

    Nel caso fossero già state stampate, le toglie dalla figura.
    """
    if not n_clicks or not curr_tab:
        return no_update

    file_type = tabs_id['page']
    tab = GLOBAL_CACHE.open_tabs[file_type].tab(curr_tab)

    for graph_id,fig in zip(graphs_ids, graphs_figs):
        if graph_id['tab']==curr_tab:
            graphs_figs[graphs_figs.index(fig)] = tab.switch_fig().figure
            break

    return graphs_figs
