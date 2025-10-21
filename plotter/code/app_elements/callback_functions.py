from pathlib import Path
import plotly.io as pio
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, State, callback, callback_context, MATCH, ALL, no_update
from .common import *
from .parameters import indexes_file, affinity_file, load_configs

## PARAMS ##
labels = {'exponential':'exp', 'gaussian':'gauss', 'uniform':'unif'}

## DYNAMIC CALLBACKS ##

@callback(
    Output({'page':MATCH, 'item':'button-close-current-tab'}, 'style'),
    Output({'page':MATCH, 'item':'menu-tab-management'}, 'style'),
    Output({'page':MATCH, 'item':'menu-tab-management'}, 'children'),
    Input({'page':MATCH, 'item':'tabs'}, 'children'),
    State({'page':MATCH, 'item':'tabs'}, 'id'),
)
def tab_managers_displayer(tabs:list[dcc.Tab], tabs_id:dict[str,str]):
    """Callback che permette di visualizzare i pulsanti di gestione dei tab"""
    if not tabs:
        return {'display': 'none'}, {'display': 'none'}, None
    if len(tabs) == 1:
        return {'display': 'block'}, {'display': 'none'}, None
    else:
        page = tabs_id['page']
        dropdown_elems = [
            dbc.DropdownMenuItem(
            f"❌ {tab['props']['label']}",
            id={'page':page, 'item':'dd-button', 'tab-index':i},
            ) for i, tab in enumerate(tabs)]
        return {'display': 'block'}, {'display': 'block'}, dropdown_elems

@callback(
    Output({'page':MATCH, 'item':'tabs-content'}, 'children'),
    Input({'page':MATCH, 'item':'tabs'}, 'value')
)
def update_graph_content(tab: str) -> dcc.Graph:
    """Aggiorna il grafico in base al tab aperto e alle curve selezionate nella checklist"""
    if not tab:
        return "nulla di selezionato"

    df_IdVd = pd.read_excel(indexes_file, sheet_name='IdVd')

    if '.csv' not in tab:
        df_group = df_IdVd.loc[df_IdVd['group'] == tab]
        g = ExpCurves(*df_group['file_path']).import_data
        return dcc.Graph(figure=plot(g, all_c=True))
    else:
        e = ExpCurves(tab).import_data
        return dcc.Graph(figure=plot(e, all_c=True), style={'height':'100vh'})

@callback(
    Output({'page':MATCH, 'item':'graph-controls'}, 'style'),
    Input({'page':MATCH, 'item':'tabs'}, 'value'),
)
def show_graph_button(curr_tab):
    if not curr_tab:
        return {'display': 'none'}
    return {'display': 'block'}

@callback(
    Output({'page':'IdVd', 'item':'table', 'location':MATCH}, 'data'),
    Output({'page':'IdVd', 'item':'table', 'location':MATCH}, 'hidden_columns'),
    Output({'page':'IdVd', 'item':'table', 'location':MATCH}, 'selected_rows', allow_duplicate=True),
    Input({'page':'IdVd', 'item':'radio-mode-toggle', 'location':MATCH}, 'value'),
    State({'page':'IdVd', 'item':'radio-mode-toggle', 'location':MATCH}, 'id'),
    State({'page':'IdVd', 'item':'table', 'location':MATCH}, 'columns'),
    prevent_initial_call=True
)
def update_table(mode:str,radio_id:dict[str,str],table_columns:list[dict[str,str]]):
    """Aggiorna la tabella nel caso venga cambiata la modalità di visualizzazione esperimenti"""

    cols_to_hide = ['file_path', 'group']

    df_IdVd = pd.read_excel(indexes_file, sheet_name='IdVd')

    if mode == 'ExpMode':
        data = df_IdVd
    else:
        data = df_IdVd.iloc[
            df_IdVd.drop_duplicates(subset='group', keep='first').index.tolist()
        ]
        cols_to_hide.append('v_gf')

    if radio_id['location']=='affinity_page':
        if mode == 'ExpMode':
            data = pd.merge(
                data,
                pd.read_excel(affinity_file, sheet_name='exp'),
                on='file_path')
        else:
            data = pd.merge(
                data,
                pd.read_excel(affinity_file, sheet_name='groups'),
                on='group'
            )

    columns = pd.DataFrame(table_columns)
    for col in columns.loc[columns['type'] == 'numeric']['id']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data.fillna('-', inplace=True)

    return data.to_dict('records'), cols_to_hide, []

@callback(
    Output({'page': MATCH, 'item': 'modal'}, 'is_open'),
    Input({'page': MATCH, 'item': 'button-open-modal'}, 'n_clicks'),
    Input({'page': MATCH, 'item': 'button-close-modal'}, 'n_clicks'),
    State({'page': MATCH, 'item': 'modal'}, 'is_open'),
)
def open_close_modal(n_clicks_open: int, n_clicks_close: int, is_open: bool):
    """Apre/chiude il pop-up di esportazione nel caso venga premuto il pulsante di export/di chiusura"""
    ctx = callback_context
    if not ctx.triggered:
        return is_open

    triggered_id = ctx.triggered_id
    if triggered_id != '.':
        if 'open' in triggered_id['item']:
            return True
        elif 'close' in triggered_id['item']:
            return False

    return is_open

@callback(
    Output({'page':MATCH, 'item':'check-legend', 'location':'modal'}, 'value'),
    Output({'page':MATCH, 'item':'check-colors', 'location':'modal'}, 'value'),
    Output({'page':MATCH, 'item':'selector-dpi', 'location':'modal'}, 'value'),
    Output({'page':MATCH, 'item':'selector-format', 'location':'modal'}, 'value'),
    Input({'page':MATCH, 'item': 'modal'}, 'is_open'),
)
def initialize_values(is_open: bool):
    if not is_open:
        return no_update, no_update, no_update, no_update
    config = load_configs()
    return (['show_legend'] if bool(config['legend']) else [],
            ['colors'] if bool(config['colors']) else [],
            int(config['DPI']), config['export_format'])

@callback(
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows', allow_duplicate=True),
    Input({'page':MATCH, 'item':'modal'}, 'is_open'),
    State({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows'),
    prevent_initial_call=True
)
def unselect_rows_modal_callback(is_open:bool, selected_rows:list[int]):
    """Deseleziona le righe quando viene chiuso il pop-up"""
    if not is_open:
        return []
    return selected_rows

@callback(
    Output({'page':MATCH, 'item':'button-export'}, "disabled"),
    Input({'page':MATCH, 'item':'table', 'location':'modal'}, "derived_virtual_selected_rows"),
    prevent_initial_call=True
)
def enable_export_button(selected_rows:list[int]):
    """Attiva il pulsante di esportazione alla selezione di almeno un esperimento/gruppo"""
    if not selected_rows:
        return True
    return False

@callback(
    Output({'page': MATCH, 'item': 'modal'}, 'is_open', allow_duplicate=True),
    Output({'page':MATCH, 'item':'store-loading-placeholder', 'location':'modal'}, 'data'),
    Input({'page': MATCH, 'item': 'button-export'}, 'n_clicks'),
    # checklist delle curve da esportare
    State({'page': MATCH, 'item': 'checklist-curves', 'location': 'modal'}, 'value'),
    # lista di indici delle righe selezionate, considerando i filtri ecc...
    State({'page': MATCH, 'item': 'table', 'location': 'modal'}, 'derived_virtual_selected_rows'),
    # lista dei dati della tabella, considerando i filtri ecc...
    State({'page': MATCH, 'item': 'table', 'location': 'modal'}, 'derived_virtual_data'),
    # mostrare legenda (True/False)
    State({'page': MATCH, 'item': 'check-legend', 'location': 'modal'}, 'value'),
    # figure esportate a colori o no
    State({'page': MATCH, 'item': 'check-colors', 'location': 'modal'}, 'value'),
    # dpi figura esportata
    State({'page': MATCH, 'item': 'selector-dpi', 'location': 'modal'}, 'value'),
    # formato file esportato
    State({'page': MATCH, 'item': 'selector-format', 'location': 'modal'}, 'value'),
    # table-mode: ExpMode/GroupMode
    State({'page': MATCH, 'item': 'radio-mode-toggle', 'location': 'modal'}, 'value'),
    prevent_initial_call=True
)
def export_selected(n_clicks:int, selected_curves:list[str], selected_rows:list[int],data_table:list[dict],
                    legend:list, colors:list, dpi_img:int, file_format:str, mode:str='ExpMode'):
    """Esporta le righe selezionate nella tabella del pop-up, premuto il bottone di export, e a fino processo chiude il pop-up"""
    if not n_clicks or not selected_rows:
        return no_update, no_update

    df_IdVd = pd.read_excel(indexes_file, sheet_name='IdVd')

    export_path = find_export_path()
    figs, exp_file_paths = [], []
    match mode:
        case 'ExpMode':
            exps: list[ExpCurves] = [ExpCurves(data_table[row_i]['file_path']).import_data for row_i in selected_rows]  # lista di esperimenti corrispondente alle righe selezionate
            figs: list[go.Figure] = [plot(curves=exp, c_to_plot=selected_curves,
                                          to_export=True, legend=bool(legend), colored=bool(colors)) for exp in exps]
            exp_file_paths: list[Path] = [export_path / Path(f"{exp}.{file_format}") for exp in exps]  # estensioni possibili .png, .svg, .pdf
        case 'GroupMode':
            groups_files: list[list[str]] = [
                df_IdVd.loc[df_IdVd.group == data_table[row_i]['group']]['file_path'].tolist() for row_i in selected_rows
            ]  # lista contenente liste di indirizzi di file appartenenti ai gruppi selezionati
            groups_curves: list[ExpCurves] = [ExpCurves(*group_files).import_data for group_files in groups_files]
            figs: list[go.Figure] = [
                plot(curves=group_curves, c_to_plot=selected_curves, to_export=True, legend=bool(legend), colored=bool(colors)) for group_curves in groups_curves]
            exp_file_paths: list[Path] = [export_path / Path(f"{group_curves}.{file_format}") for group_curves in groups_curves]

    try:
        pio.write_images(fig=figs, file=exp_file_paths, format=file_format, scale=dpi_img/72)
        return False, "export finished"
    except Exception as e:
        return no_update, f"export failed: {e}"

@callback(
    Output({'page':MATCH, 'item':'store-loading-placeholder', 'location':'page'}, 'data'),
    Input({'page': MATCH, 'item': 'button-export-current-graph'}, 'n_clicks'),
    State({'page':MATCH, 'item':'tabs'}, 'value'),
    prevent_initial_call=True
)
def export_current(n_clicks:int, curr_tab:str):
    if not n_clicks or not curr_tab:
        return no_update, no_update

    df_IdVd = pd.read_excel(indexes_file, sheet_name='IdVd')

    configs = load_configs()
    export_dir = find_export_path()

    if ".csv" in curr_tab:
        curves = ExpCurves(curr_tab)
    else:
        df_group = df_IdVd.loc[df_IdVd['group'] == curr_tab]
        curves = ExpCurves(*df_group['file_path'])

    fig = plot(curves=curves, all_c=True, to_export=True,
               legend=bool(configs['legend']), colored=bool(configs['colors']))
    try:
        fig.write_image(f"{export_dir}/{curves}.{configs['export_format']}")
        return "export finished"
    except Exception as e:
        return f"export failed: {e}"

@callback(
    Output({'page':MATCH, 'item':'tabs'}, 'children'),
    Output({'page':MATCH, 'item':'table', 'location':'page'}, 'selected_rows'),
    Output({'page':MATCH, 'item':'tabs'}, 'value'),
    # n_clicks (plot button)
    Input({'page': MATCH, 'item': 'button-plot'}, 'n_clicks'),
    # selected_rows: indici delle righe selezionate (considerati filtri vari colonne)
    State({'page': MATCH, 'item': 'table', 'location': 'page'}, 'derived_virtual_selected_rows'),
    # table_data: dati della tabella (considerati filtri vari colonne)
    State({'page': MATCH, 'item': 'table', 'location': 'page'}, 'derived_virtual_data'),
    # curr_tab: tab attualmente aperto (se nessuno None)
    State({'page': MATCH, 'item': 'tabs'}, 'value'),
    # tabs: lista dei tab disponibili
    State({'page': MATCH, 'item': 'tabs'}, 'children'),
    # curr_mode: modo corrente della tabella (ExpMode/GroupMode)
    State({'page': MATCH, 'item': 'radio-mode-toggle', 'location': 'page'}, 'value')
)
def update_tabs(n_clicks:int, selected_rows:list[int], table_data:dict, curr_tab:str,
                tabs:list[dcc.Tab], curr_mode='ExpMode')->list[dcc.Tab]|list|str:
    """
    Aggiorna la lista dei tab al click del bottone, in base agli esperimenti selezionati nella tabella
    :return: la lista dei tab aggiornata, azzera la lista delle righe selezionate e imposta il tab da visualizzare dopo la callback
    """
    tabs = tabs or []
    if not n_clicks or not selected_rows:
        return tabs, [], curr_tab

    open_tabs = [tab['props']['value'] for tab in tabs]

    for selected_index in selected_rows:
        row = table_data[selected_index]

        if ((row['file_path'] not in open_tabs and curr_mode == 'ExpMode') or
            (row['group'] not in open_tabs and curr_mode == 'GroupMode')):
            exp_type=None
            if 'group' in row:
                exp_type = 'Exp' if curr_mode == 'ExpMode' else 'Group'
            elif 'start_cond' in row:
                exp_type = 'Trap'

            if exp_type:
                tabs.append(create_tab(row, tab_type=exp_type))

    if not open_tabs:
        # se non c'è alcun tab già aperto, apro il primo tab aggiunto
        return tabs, [], table_data[selected_rows[0]]['file_path' if curr_mode == 'ExpMode' else 'group']
    else:
        return tabs, [], curr_tab  # altrimenti lascio aperto il tab già selezionato

@callback(
    Output({'page':MATCH, 'item':'main-tabs'}, 'active_tab'),
    Input({'page':MATCH, 'item':'button-plot'}, 'n_clicks'),
    State({'page': MATCH, 'item': 'table', 'location':'page'}, 'selected_rows'),
    prevent_initial_call=True
)
def switch_to_graphs_tab(n_clicks, selected_rows):
    """Passa alla tab dei grafici quando si clicca su 'Genera Grafico'"""
    if n_clicks and selected_rows:
        return "tab-graphs"
    return "tab-table"

@callback(
    Output({'page':MATCH, 'item':'tabs'}, 'children', allow_duplicate=True),
    Output({'page':MATCH, 'item':'tabs'}, 'value', allow_duplicate=True),
    Input({'page':MATCH, 'item':'button-close-current-tab'}, 'n_clicks'),
    State({'page':MATCH, 'item':'tabs'}, 'value'),
    State({'page':MATCH, 'item':'tabs'}, 'children'),
    prevent_initial_call=True
)
def close_current_tab(n_clicks:int, active_tab:str, tabs:list[dcc.Tab]):
    if not n_clicks or not tabs or not active_tab:
        return tabs, None
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

@callback(
    Output({'page':MATCH, 'item':'tabs'}, 'children', allow_duplicate=True),
    Output({'page':MATCH, 'item':'tabs'}, 'value', allow_duplicate=True),
    Input({'page':MATCH, 'item':'dd-button', 'tab-index':ALL}, 'n_clicks'),
    State({'page':MATCH, 'item':'tabs'}, 'children'),
    State({'page':MATCH, 'item':'tabs'}, 'value'),
    prevent_initial_call=True
)
def pop_tab(n_clicks_list:list[int], tabs:list[dcc.Tab], open_tab:str):
    """Callback che gestisce la chiusura di un tab da parte di un pulsante del dropdown menu"""
    ctx = callback_context
    if not ctx.triggered or not tabs or not open_tab:
        return tabs

    if not any(n_clicks_list):
        return tabs, open_tab

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
                tabs.pop(tab_index)
                return tabs, open_tab
        except (KeyError, IndexError):
            pass
    return tabs, open_tab

@callback(
    Output({'page':'IdVd', 'item':'table', 'location':'affinity_page'}, 'data', allow_duplicate=True),
    Input({'page': 'IdVd', 'item': 'button-calculate-affinity'}, 'n_clicks'),
    State({'page':'IdVd', 'item':'radio-mode-toggle', 'location':'affinity_page'}, 'value'),
    prevent_initial_call=True
)
def affinity_calc(n_clicks:int, mode:str):
    if not n_clicks:
        return no_update

    df_IdVd = pd.read_excel(indexes_file, sheet_name='IdVd')

    df_affinity = pd.read_excel(affinity_file, sheet_name='exp')
    df_affinity_groups = pd.read_excel(affinity_file, sheet_name='groups')

    rows_exp_sheet = []
    rows_group_sheet = []
    for group in df_affinity_groups['group']:
        g = ExpCurves(*df_affinity.loc[df_affinity['group'] == group]['file_path']).import_data.affinity_calc

        for a, e in zip(g.affinities, g.exp):
            row = a.copy()
            row['file_path'], row['group'] = str(e.path), group
            rows_exp_sheet.append(row)

        row = g.group_affinity.copy()
        row['group'] = group
        rows_group_sheet.append(row)

    df_affinity = pd.DataFrame(rows_exp_sheet)[df_affinity.columns]
    df_affinity_groups = pd.DataFrame(rows_group_sheet)[df_affinity_groups.columns]

    with pd.ExcelWriter(affinity_file) as writer:
        df_affinity.to_excel(writer, sheet_name='exp', index=False)
        df_affinity_groups.to_excel(writer, sheet_name='groups', index=False)

    if mode == 'ExpMode':
        data = pd.merge(df_IdVd, df_affinity, on='file_path')
    else:
        data = df_IdVd.iloc[
            df_IdVd.drop_duplicates(subset='group', keep='first').index.tolist()
        ]
        data = pd.merge(
            data,
            df_affinity_groups,
            on='group'
        )

    return data.to_dict('records')

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
    export_dir = Path(load_configs()['export_directory'])
    i=0
    while True:
        export_path = try_mkdir(export_dir/'export' if i==0 else export_dir/f'export-{i}')
        if export_path:
          return export_path
        i+=1

def create_tab(row: dict, tab_type: str) -> dcc.Tab:
    """Crea la label di ogni tab in base al tipo richiesto"""
    if tab_type not in ['Exp', 'Group', 'Trap']:
        raise ValueError(f'{tab_type} non è un tipo valido per un tab')
    if tab_type in ['Exp', 'Group']:
        label = 'EXP' if tab_type == 'Exp' else 'GROUP'
        label += f' - {labels[row['trap_distr']]}, Em:{row['e_mid']}, Es:{row['e_sigma']}, Vgf:{row['v_gf']}'
    else:
        label = f'{labels[row['trap_distr']]}, Em:{row['e_mid']}, Es:{row['e_sigma']}, Vgf:{row['v_gf']},  {row['start_cond']}'
    return dcc.Tab(
        label=label,
        value=row['file_path'] if tab_type in ('Exp', 'Trap') else row['group'],
        style={'fontSize': 10, 'left-margin': '2px'},
    )