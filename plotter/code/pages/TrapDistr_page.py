import dash
from dash import Input, Output, callback, State, dcc, html
import dash_bootstrap_components as dbc
from plotter.code.IdVd import *

dash.register_page(__name__, path='/TrapDistr-plotter')

## LAYOUT ##
layout = dbc.Container(
    children=[
        dbc.Row(
            children=[          #ogni riga ha dimensione 12 orizzontalmente
                dbc.Col(
                    children=[
                        my_table_template('table','TrapData')
                    ],
                    width=4,    #larghezza colonna
                    style={'textAlign': 'center'},
                ),  #ELENCO FILE
                dbc.Col(
                    html.Div(
                        children=[
                            dbc.Button("Plot ->", id="plot-button", className="me-15", color="primary"),
                            dbc.Button("Export!", id='modal-button', className="me-15", color="primary"),
                            export_modal('export-modal','TrapData')
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
                        curves_checklist('curve-checklist', 'TrapData')   # checklist curve visualizzate
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