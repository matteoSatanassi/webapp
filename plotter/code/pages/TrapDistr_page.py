import dash
from dash import Input, Output, callback, State, dcc, html
import dash_bootstrap_components as dbc
from plotter.code.app_elements import *

dash.register_page('TrapPlotter', path='/TrapData-plotter')

## PARAMS ##
PAGE_PREFIX = 'TrapData-'

## LAYOUT ##
layout = dbc.Container(
    children=[
        dbc.Row(
            children=[          #ogni riga ha dimensione 12 orizzontalmente
                dbc.Col(
                    children=[
                        my_table_template(PAGE_PREFIX+'table','TrapData')
                    ],
                    width=4,    #larghezza colonna
                    style={'textAlign': 'center'},
                ),  #ELENCO FILE
                dbc.Col(
                    html.Div(
                        children=[
                            dbc.Button("Plot ->", id=PAGE_PREFIX+"plot-button", className="me-15", color="primary"),
                            dbc.Button("Export!", id=PAGE_PREFIX+"modal-button", className="me-15", color="primary"),
                            export_modal(PAGE_PREFIX+'export-modal','TrapData')
                        ],
                        style={"textAlign": "center"}
                    ),
                    className="d-flex justify-content-center",
                    width=1     #larghezza colonna
                ),  #BOTTONI
                dbc.Col(
                    children=[
                        dcc.Tabs(id=PAGE_PREFIX+"tabs", value=None),
                        html.Div(id=PAGE_PREFIX+"tabs-content"),
                        curves_checklist(PAGE_PREFIX+'curve-checklist', 'TrapData')   # checklist curve visualizzate
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
    className='TrapDistr_dashboard'
)

## CALLBACKS ##
callback(
    Output('tabs', 'children'),
    Output('table','selected_rows'),
    Output('tabs','value'),
    Input('plot-button', 'n_clicks'),
    State('tabs', 'derived_virtual_selected_rows'),
    State('tabs', 'derived_virtual_data'),
    State('tabs', 'value'),
    State('tabs', 'children'),
)(update_tabs_trapdata)

callback(
    Output('tabs-content', 'children'),
    Input('tabs','value'),
    Input('curve-checklist','value')
)(update_graph_content)

callback(
    Output('modal-export', 'is_open'),
    Input('modal-button', 'n_clicks'),
    State('modal-export', 'is_open'),
)(toggle_modal)
callback(
    Output('modal-export', 'is_open', allow_duplicate=True),
    Input('close-button', 'n_clicks'),
    State('modal-export', 'is_open'),
    prevent_initial_call=True,
)(toggle_modal)

