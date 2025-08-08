from dash import dcc, dash_table, html
import dash_bootstrap_components as dbc
import plotly.io as pio
from Common import *

## PARAMS ##
index_table_csv = Path('../IdVd_data/index_table.csv')
df = pd.read_csv(index_table_csv)
exp_mode_dict = df.to_dict('records')

## DERIVED PARAMS ##
group_first_only_indexes = df.drop_duplicates(subset='group', keep='first').index.tolist()  # restituisce una lista degli indici delle prime occorrenze di ogni gruppo
group_mode_dict = df.iloc[group_first_only_indexes].to_dict('records')

## PAGE ELEMENTS ##
def my_table(table_id:str):
    return dash_table.DataTable(
        id=table_id,
        data=exp_mode_dict,
        columns=[
            {'name': 'Trap Distribution', 'id': 'trap_distr'},
            {'name': "E_mid", 'id': 'e_mid'},
            {'name': 'E_σ', 'id': 'e_sigma'},
            {'name': 'V_gf', 'id': 'v_gf'},
            {'name': 'file_path', 'id': 'file_path'},
            {'name': 'group', 'id': 'group'},
        ],
        sort_action='native',
        filter_action='native',
        filter_options={"placeholder_text": "Filter column..."},
        row_selectable='multi',
        selected_rows=[],
        hidden_columns=['file_path', 'group'],
        page_size=10,
        style_cell={'textAlign': 'right'},
        style_cell_conditional=[
            {
                'if': {'column_id': 'trap_distr'},
                'textAlign': 'left'
            }
        ],
        style_data={
            'color': 'black',
            'backgroundColor': 'white'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold'
        },
        css=[{"selector": ".show-hide", "rule": "display: none"}]
    )

    ## CALLBACK FUNCTIONS ##

def mode_options(radio_id:str):
    return dcc.RadioItems(
        options=['Group mode','Exp mode'],
        value='Exp mode',
        id=radio_id,
        inline=True,
    )

def curves_options(checklist_id:str):
    return dcc.Checklist(
        id=checklist_id,
        options=[
            {'label': '(0,0)', 'value': 'v0'},
            {'label': '(-7,0)', 'value': '0'},
            {'label': '(-7,15)', 'value': '15'},
            {'label': '(-7,30)', 'value': '30'},
        ],
        value=['v0','0','15','30'],  # all’inizio tutte selezionate
        labelStyle={'display': 'inline-block'},
    )

export_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Export")),
        dbc.ModalBody(
            dbc.Row([
                dbc.Col(my_table('export-table')),
                dbc.Col(
                    [
                        html.Div(mode_options('export-mode-toggle')),
                        html.Div(curves_options('export-curves'))
                    ]
                )
            ])
        ),
        dbc.ModalFooter(
            [
                dbc.Button("Close", id="close-button", className="ms-auto", n_clicks=0),
                dbc.Button("Export Selected", id="export-button", className="ms-auto", n_clicks=0)
            ]
        ),
    ],
    id="modal-export",
    is_open=False,
)

## CALLBACKS FUNCTIONS ##
def update_tabs(n_clicks, curr_mode, selected_rows, table_data, curr_tab, tabs):
    labels = {'exponential':'exp', 'gaussian':'gauss', 'uniform':'unif'}
    tabs = tabs or []
    if not n_clicks or not selected_rows:
        return tabs,[],curr_tab

    open_tabs = [tab['props']['value'] for tab in tabs]

    for selected_index in selected_rows:
        row = table_data[selected_index]
        if curr_mode == 'Exp mode':
            file = row['file_path']
            if file not in open_tabs:
                tabs.append(
                    dcc.Tab(
                        label=f"Exp - {labels[row['trap_distr']]}/{row['e_mid']}/{row['e_sigma']}/{row['v_gf']}",
                        value=file
                    )
                )
        else:
            group = row['group']
            if group not in open_tabs:
                tabs.append(
                    dcc.Tab(
                        label=f"Group - {labels[row['trap_distr']]}/{row['e_mid']}/{row['e_sigma']}",
                        value=group
                    )
                )

    if not open_tabs:
        if curr_mode == 'Exp mode':
            return tabs,[],table_data[selected_rows[0]]['file_path']    # se non c'è alcun tab già aperto, apro il primo tab
        else:
            return tabs,[],table_data[selected_rows[0]]['group']
    else:
        return tabs,[],curr_tab     # altrimenti lascio aperto il tab già selezionato

def update_graph_content(tab, checked_curves):
    if not tab:
        return "nulla di selezionato"
    if '.csv' not in tab:
        df_group = df.loc[df['group']==tab]
        g = Group()
        for file in df_group['file_path']:
            g.add_path(Path(file))
        g_plot = GroupPlot(g).plot(checked_curves)
        return dcc.Graph(figure=g_plot.fig)
    else:
        exp = Exp(tab).fill()
        exp_plot = ExpPlot(exp).plot(checked_curves)
        return dcc.Graph(figure=exp_plot.fig)

def update_table(mode):
    if mode == 'Exp mode':
        return exp_mode_dict,['file_path', 'group'],[]
    else:
        return group_mode_dict,['file_path', 'group', 'v_gf'],[]

def export_selected(n_clicks, mode, selected_curves, selected_rows, data_table):     # AGGIUNGERE BOX PER SCELTA DOWNLOAD_PATH, ESTENSIONE, CURVE DA PLOTTARE
    if not n_clicks or not selected_rows:
        return selected_rows
    export_path = find_export_path()
    figs,exp_file_paths = [],[]
    match mode:
        case 'Exp mode':
            exps:list[Exp] = [Exp(data_table[row_i]['file_path']).fill() for row_i in selected_rows]        # lista di esperimenti corrispondente alle righe selezionate
            plots:list[ExpPlot] = [ExpPlot(exp).plot(selected_curves) for exp in exps]                 # lista di ExpPlot corrispondente
            figs:list[go.Figure] = [plot.fig for plot in plots]
            exp_file_paths:list[Path] = [export_path/Path(f"{plot.exp_curves.exp}.png") for plot in plots]  #estensioni possibili .png, .svg, .pdf
        case 'Group mode':
            groups_files:list[list[str]] = [df.loc[df.group==data_table[row_i]['group']]['file_path'].tolist() for row_i in selected_rows]
            groups:list[Group] = [Group().add_paths(group_files) for group_files in groups_files]
            plots:list[GroupPlot] = [GroupPlot(g).plot(selected_curves) for g in groups]
            figs:list[go.Figure] = [plot.fig for plot in plots]
            exp_file_paths:list[Path] = [export_path/Path(f"{plot.group_curves.group}.png") for plot in plots]
    pio.write_images(
        fig=figs,
        file=exp_file_paths
    )
    return False

def toggle_modal(n_clicks, is_open):
    if not n_clicks:
        return is_open
    return not is_open