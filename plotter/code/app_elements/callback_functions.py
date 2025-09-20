from pathlib import Path
import plotly.io as pio
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, State, callback
from plotter.code.common import *
from .parameters import IdVd_df, IdVd_table_exp_mode, IdVd_table_group_mode, load_configs

## PARAMS ##
labels = {'exponential':'exp', 'gaussian':'gauss', 'uniform':'unif'}
PAGES = ('TrapData','IdVd')

## CALLBACK FACTORIES ##
def _create_tabs_callback(page:str):
    """Crea la callback che aggiorna i tab nella pagina selezionata, alla pressione del pulsante di plot"""
    if page not in PAGES:
        raise ValueError(f"{page} non è una pagina valida")
    def callback_args():
        """Genera dinamicamente gli argomenti della callback"""
        args = [
            Input(f'{page}-plot-button', 'n_clicks'),                   # n_clicks (plot button)
            State(f'{page}-table', 'derived_virtual_selected_rows'),    # selected_rows: indici delle righe selezionate (considerati filtri vari colonne)
            State(f'{page}-table', 'derived_virtual_data'),             # table_data: dati della tabella (considerati filtri vari colonne)
            State(f'{page}-tabs', 'value'),                             # curr_tab: tab attualmente aperto (se nessuno None)
            State(f'{page}-tabs', 'children'),                          # tabs: lista dei tab disponibili
        ]
        if page == 'IdVd':
            args.append(State(f'{page}-mode-toggle', 'value'))        # curr_mode: modo corrente della tabella (Exp/Group)
        return args
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
    @callback(
        Output(f'{page}-tabs', 'children'),
        Output(f'{page}-table', 'selected_rows'),
        Output(f'{page}-tabs', 'value'),
        *callback_args()
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
            if page == 'IdVd':
                if ((row['file_path'] not in open_tabs and curr_mode == 'ExpMode')
                        or (row['group'] not in open_tabs and curr_mode == 'GroupMode')):
                    tabs.append(
                        create_tab(row, tab_type='Exp' if curr_mode == 'ExpMode' else 'Group')
                    )
            else:
                if row['file_path'] not in open_tabs:
                    tabs.append(
                        create_tab(row, tab_type='Trap')
                    )

        if not open_tabs:
            return tabs, [], table_data[selected_rows[0]]['file_path' if curr_mode == 'ExpMode' else 'group']  # se non c'è alcun tab già aperto, apro il primo tab
        else:
            return tabs, [], curr_tab  # altrimenti lascio aperto il tab già selezionato
    @callback(
        Output(f'{page}-close-current-tab-button', 'style'),
        Output(f'{page}-tab-management-menu', 'style'),
        Output(f'{page}-tab-management-menu', 'children'),
        Input(f'{page}-tabs', 'children')
    )
    def tab_manager_backend(tabs:list[dcc.Tab]):
        if not tabs:
            return {'display': 'none'}, {'display': 'none'}, None
        if len(tabs) == 1:
            return {'display': 'block'}, {'display': 'none'}, None
        else:
            dropdown_elems = [dbc.DropdownMenuItem(
                f"❌ {tab['props']['label']}", id=f"close-{tab['props']['value']}"
            ) for tab in tabs]
            return {'display': 'block'}, {'display': 'block'}, dropdown_elems
    return update_tabs, tab_manager_backend

def _create_graph_callback(page:str):
    """Crea la callback che aggiorna il grafico all'apertura di un nuovo tab"""
    if page not in PAGES:
        raise ValueError(f"{page} non è una pagina valida")
    @callback(
        Output(f'{page}-tabs-content', 'children'),
        Input(f'{page}-tabs', 'value')
    )
    def update_graph_content(tab: str) -> dcc.Graph:
        """Aggiorna il grafico in base al tab aperto e alle curve selezionate nella checklist"""
        if not tab:
            return "nulla di selezionato"
        if '.csv' not in tab:
            df_group = IdVd_df.loc[IdVd_df['group'] == tab]
            g = ExpCurves(*df_group['file_path']).import_data()
            return dcc.Graph(figure=plot(g, all_c=True))
        else:
            e = ExpCurves(tab).import_data()
            return dcc.Graph(figure=plot(e, all_c=True))
    return update_graph_content

def _create_tables_callbacks(page:str):
    """Crea le callbacks che aggiornano le tabelle(la principale e quella nel pop-up) nella pagina IdVd Plotter"""
    if page != 'IdVd':
        raise ValueError(f"{page} non è una pagina valida")
    def callback_args(is_modal_callback:bool=False)->list[Output|Input]:
        """genera dinamicamente gli argomenti delle callbacks"""
        prefix = f'{page}-modal' if is_modal_callback else f'{page}'
        args = [
            Output(f'{prefix}-table', 'data'),
            Output(f'{prefix}-table', 'hidden_columns'),
            Output(f'{prefix}-table', 'selected_rows', allow_duplicate=True),
            Input(f'{prefix}-mode-toggle', 'value'),
        ]
        return args
    def update_table(mode:str)->list[dict]|list[str]|list:
        """aggiorna la tabella in base alla modalità selezionata"""
        if mode == 'ExpMode':
            return IdVd_table_exp_mode, ['file_path', 'group'], []
        else:
            return IdVd_table_group_mode, ['file_path', 'group', 'v_gf'], []
    @callback(
        *callback_args(),
        prevent_initial_call=True
    )
    def update_table_callback(mode:str):
        """Aggiorna la tabella nel caso venga cambiata la modalità di visualizzazione esperimenti"""
        return update_table(mode)
    @callback(
        *callback_args(is_modal_callback=True),
        prevent_initial_call=True
    )
    def update_table_modal_callback(mode:str):
        """Aggiorna la tabella nel caso venga cambiata la modalità di esportazione esperimenti"""
        return update_table(mode)

    return update_table_callback, update_table_modal_callback

def _create_modal_callbacks(page:str):
    """Crea le due callbacks sel pop-up i esportazione: quella di apertura e quella di chiusura"""
    if page not in PAGES:
        raise ValueError(f'{page} non è una pagina valida')
    def toggle_modal(n_clicks:int, is_open:bool)->bool:
        """Mostra/nasconde il pop-up per l'esportazione"""
        if not n_clicks:
            return is_open
        return not is_open

    @callback(
        Output(f'{page}-modal', 'is_open'),
        Input(f'{page}-open-modal-button', 'n_clicks'),
        State(f'{page}-modal', 'is_open'),
    )
    def open_modal_callback(n_clicks:int, is_open:bool):
        """Apre il pop-up di esportazione nel caso venga premuto il bottone di export"""
        return toggle_modal(n_clicks, is_open)

    @callback(
        Output(f'{page}-modal', 'is_open', allow_duplicate=True),
        Input(f'{page}-modal-close-button', 'n_clicks'),
        State(f'{page}-modal', 'is_open'),
        prevent_initial_call=True,
    )
    def close_modal_callback(n_clicks:int, is_open:bool):
        """Chiude il pop-up di esportazione nel caso venga premuto il bottone di chiusura"""
        return toggle_modal(n_clicks, is_open)

    @callback(
        Output(f'{page}-modal-table', 'selected_rows', allow_duplicate=True),
        Input(f'{page}-modal', 'is_open'),
        State(f'{page}-modal-table', 'selected_rows'),
        prevent_initial_call=True
    )
    def unselect_rows_modal_callback(is_open:bool, selected_rows:list[int]):
        """Deseleziona le righe quando viene chiuso il pop-up"""
        if not is_open:
            return selected_rows
        return []

    @callback(
        Output(f"{page}-modal-export-button", "disabled"),
        Input(f"{page}-modal-table", "derived_virtual_selected_rows"),
        prevent_initial_call=True
    )
    def enable_export_button(selected_rows:list[int]):
        """Attiva il pulsante di esportazione alla selezione di almeno un esperimento/gruppo"""
        if not selected_rows:
            return True
        return False

    return open_modal_callback, close_modal_callback, unselect_rows_modal_callback

def _create_export_callback(page:str):
    """Crea la callback di esportazione dei grafici selezionati del pop-up"""
    if page not in PAGES:
        raise ValueError(f"{page} non è una pagina valida")
    def callback_args()->list[Output|Input|State]:
        args = [
            Output(f'{page}-modal', 'is_open', allow_duplicate=True),
            Input(f'{page}-modal-export-button', 'n_clicks'),  # n_clicks
            State(f'{page}-modal-curves-checklist', 'value'),  # checklist delle curve da esportare
            State(f'{page}-modal-table', 'derived_virtual_selected_rows'), # lista di indici delle righe selezionate, considerando i filtri ecc...
            State(f'{page}-modal-table', 'derived_virtual_data'),  # lista dei dati della tabella, considerando i filtri ecc...
            State(f'{page}-modal-legend-toggle', 'switch'), # mostrare legenda (True/False)
            State(f'{page}-modal-color-toggle', 'switch'),  # figure esportate a colori o no
            State(f'{page}-modal-dpi-selector', 'value'),   # dpi figura esportata
            State(f'{page}-modal-format-selector', 'value'),    # formato file esportato
        ]
        if page == 'IdVd':
            args.append(State(f'{page}-modal-mode-toggle', 'value'))  # mode: ExpMode/GroupMode
        return args
    @callback(
        *callback_args(),
        prevent_initial_call=True
    )
    def export_selected(n_clicks:int, selected_curves:list[str], selected_rows:list[int],data_table:list[dict],
                        legend:bool, colored_img:bool, dpi_img:int, file_format:str, mode:str='ExpMode')->bool:
        """Esporta le righe selezionate nella tabella del pop-up, premuto il bottone di export, e a fino processo chiude il pop-up"""
        if not n_clicks or not selected_rows:
            return selected_rows
        export_path = find_export_path()
        figs, exp_file_paths = [], []
        match mode:
            case 'ExpMode':
                exps: list[ExpCurves] = [ExpCurves(data_table[row_i]['file_path']).import_data() for row_i in selected_rows]  # lista di esperimenti corrispondente alle righe selezionate
                figs: list[go.Figure] = [
                    plot(curves=exp, c_to_plot=selected_curves, to_export=True, legend=legend, colored=colored_img) for exp in exps]
                exp_file_paths: list[Path] = [export_path / Path(f"{exp}.{file_format}") for exp in exps]  # estensioni possibili .png, .svg, .pdf
            case 'GroupMode':
                groups_files: list[list[str]] = [
                    IdVd_df.loc[IdVd_df.group == data_table[row_i]['group']]['file_path'].tolist() for row_i in selected_rows
                ]  # lista contenente liste di indirizzi di file appartenenti ai gruppi selezionati
                groups_curves: list[ExpCurves] = [ExpCurves(*group_files).import_data() for group_files in groups_files]
                figs: list[go.Figure] = [
                    plot(curves=group_curves, c_to_plot=selected_curves, to_export=True, legend=legend, colored=colored_img) for group_curves in groups_curves]
                exp_file_paths: list[Path] = [export_path / Path(f"{group_curves}.{file_format}") for group_curves in groups_curves]
        pio.write_images(fig=figs, file=exp_file_paths, format=file_format, scale=dpi_img/72)
        return False
    return export_selected

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