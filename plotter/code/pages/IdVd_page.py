import dash
from dash import Input, Output, callback, State, dcc, html
import dash_bootstrap_components as dbc
from plotter.code.app_elements import *

dash.register_page('IdVd Plotter', path='/IdVd-plotter')

## LAYOUT ##
layout = dbc.Container(
    children=[
        dbc.Row(
            dbc.Col(
                children=html.H1('IdVd Plotter'),
                style={'textAlign': 'center'}
            ),
            style={'height':'12vh'}
        ),  #TITOLO
        dbc.Row(
            children=[          #ogni riga ha dimensione 12 orizzontalmente
                dbc.Col(
                    children=[
                        mode_options('mode-toggle'),
                        my_table_template('table','IdVd')
                    ],
                    width=4,    #larghezza colonna
                    style={'textAlign': 'center'},
                ),  #ELENCO FILE
                dbc.Col(
                    html.Div(
                        children=[
                            dbc.Button("Plot ->", id="plot-button", className="me-15", color="primary"),
                            dbc.Button("Export!", id='open-modal-button', className="me-15", color="primary"),
                            export_modal('modal','IdVd')
                        ],
                        style={"textAlign": "center"}
                    ),
                    className="d-flex justify-content-center",
                    width=1     #larghezza colonna
                ),  #BOTTONI
                dbc.Col(
                    children=[
                        dcc.Tabs(id="tabs", value=None),
                        html.Div(id="tabs-content"),
                        curves_checklist('curve-checklist', 'IdVd')   # checklist curve visualizzate
                    ],
                    style={'textAlign': 'center'},
                    width=7     #larghezza colonna
                ),  #GRAFICI e checklist
            ],
            align="center",
            style={'height':'60vh'}
        ),  #GRAFICO+TABELLA
    ],
    fluid=True,
    className='IdVd_dashboard'
)

## CALLBACKS ##
callback(
    [
        Output('tabs', 'children'),
        Output('table','selected_rows'),
        Output('tabs', 'value')
    ],  #output
    [
        Input('plot-button', 'n_clicks')    #n_clicks (plot button)
    ],  #input
    [
        State('mode-toggle', 'value'),        #curr_mode: modo corrente della tabella (Exp/Group)
        State('table','derived_virtual_selected_rows'), #selected_rows: indici delle righe selezionate (considerati filtri vari colonne)
        State('table','derived_virtual_data'),      #table_data: dati della tabella (considerati filtri vari colonne)
        State('tabs','value'),                      #curr_tab: tab attualmente aperto (se nessuno None)
        State('tabs','children'),                   #tabs: lista dei tab disponibili
     ]  #states
)(update_tabs_idvd)

callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    Input('curve-checklist', 'value')
)(update_graph_content)

callback(
    Output('table', 'data'),
    Output('table', 'hidden_columns'),
    Output('table', 'selected_rows',allow_duplicate=True),
    Input('mode-toggle', 'value'),
    prevent_initial_call=True
)(update_table)

callback(
    Output('export-table', 'data'),
    Output('export-table', 'hidden_columns'),
    Output('export-table', 'selected_rows',allow_duplicate=True),
    Input('export-mode-toggle', 'value'),
    prevent_initial_call=True
)(update_table)

callback(
    Output('modal', 'is_open'),
    Input('modal-button', 'n_clicks'),
    State('modal', 'is_open'),
)(toggle_modal)

 #chiude il pop-up al cliccare di close
callback(
    Output('modal', 'is_open', allow_duplicate=True),
    Input('close-button', 'n_clicks'),
    State('modal', 'is_open'),
    prevent_initial_call=True,
)(toggle_modal)

callback(
    Output('modal', 'is_open', allow_duplicate=True),
    Input('export-button', 'n_clicks'),                 #n_clicks
    [
        State('export-mode-toggle', 'value'),           #mode (Exp mode-Group mode)
        State('export-curves-checklist', 'value'),
        State('export-table', 'derived_virtual_selected_rows'), #selected_rows virtuali, considerando i filtri ecc...
        State('export-table', 'derived_virtual_data')
     ],
    prevent_initial_call=True
)(export_selected)