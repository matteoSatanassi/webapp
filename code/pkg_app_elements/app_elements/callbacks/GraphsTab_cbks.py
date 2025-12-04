import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, State, callback, MATCH, ALL, no_update, callback_context


## DYNAMIC CALLBACKS ##
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
    else:
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
    State({'page':MATCH, 'item': 'graph-tabs'}, 'children')],
    prevent_initial_call=True
)
def close_current_tab(n_clicks:int, active_tab:str, tabs:list[dcc.Tab]):
    """Chiude il tab correntemente aperto"""
    if not n_clicks or not tabs or not active_tab:
        return no_update, no_update

    from app_resources.AppCache import GLOBAL_CACHE

    # elimino i dati del tab dalla memoria cache
    GLOBAL_CACHE.del_tab(active_tab)

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
    State({'page':MATCH, 'item': 'graph-tabs'}, 'value')],
    prevent_initial_call=True
)
def pop_tab(n_clicks_list:list[int], tabs:list[dcc.Tab], open_tab:str):
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
            if 0 <= tab_index < len(tabs):
                from app_resources.AppCache import GLOBAL_CACHE

                tabs.pop(tab_index)
                GLOBAL_CACHE.del_tab(tabs[tab_index]['props']['value'])

                return tabs, open_tab
        except (KeyError, IndexError):
            pass
    return tabs, open_tab


@callback(
    Output({'page':MATCH, 'item': 'store-placeholder-graph-tab'}, 'data'),
    Input({'page': MATCH, 'item': 'button-export-current-graph'}, 'n_clicks'),
    State({'page':MATCH, 'item': 'graph-tabs'}, 'value'),
    prevent_initial_call=True
)
def export_current(n_clicks:int, curr_tab:str):
    """Esporta il grafico contenuto nel tab aperto, con parametri di esportazione come da config"""
    if not n_clicks or not curr_tab:
        return no_update, no_update

    from app_resources.AppCache import GLOBAL_CACHE

    out = GLOBAL_CACHE.save_tab(curr_tab)

    return out


@callback(
    Output({'page':MATCH, 'item': 'graph-tabs'}, 'children', allow_duplicate=True),
    Input({'page':MATCH, 'item':'button-target-visualize'}, 'n_clicks'),
    [State({'page':MATCH, 'item': 'graph-tabs'}, 'value'),
     State({'page':MATCH, 'item': 'graph-tabs'}, 'children')],
    prevent_initial_call=True
)
def plot_targets(n_clicks:int, curr_tab:str, tabs:list[dcc.Tab]):
    """
    La callback si occupa di stampare le curve target nel tab aperto,
    in caso non siano già presenti, alla pressione dell'apposito pulsante.

    Nel caso fossero già state stampate, le toglie dalla figura.
    """
    if not n_clicks or not tabs or not curr_tab:
        return no_update

    from app_resources.AppCache import GLOBAL_CACHE

    tab_values = [tab['props']['value'] for tab in tabs]
    tab_index = tab_values.index(curr_tab)

    tabs[tab_index] = GLOBAL_CACHE.tab(curr_tab).use_targets(
        True if n_clicks%2==1 else False
    ).build_dcc_tab()

    return tabs