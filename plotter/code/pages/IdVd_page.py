import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from plotter.code.app_elements import *

dash.register_page(__name__, path='/IdVd-plotter')

## PARAMS ##
PAGE_PREFIX = 'IdVd'+'-'

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
                        mode_options(f'{PAGE_PREFIX}mode-toggle'),
                        my_table_template(f'{PAGE_PREFIX}table','IdVd')
                    ],
                    width=4,    #larghezza colonna
                    style={'textAlign': 'center'},
                ),  #ELENCO FILE
                dbc.Col(
                    html.Div(
                        children=[
                            dbc.Button("Plot ->", id=f'{PAGE_PREFIX}plot-button', className="me-15", color="primary"),
                            dbc.Button("Export!", id=f'{PAGE_PREFIX}open-modal-button', className="me-15", color="primary"),
                            export_modal(f'{PAGE_PREFIX}modal','IdVd')
                        ],
                        style={"textAlign": "center"}
                    ),
                    className="d-flex justify-content-center",
                    width=1     #larghezza colonna
                ),  #BOTTONI
                dbc.Col(
                    children=[
                        dcc.Tabs(id=f"{PAGE_PREFIX}tabs", value=None),
                        html.Div(id=f"{PAGE_PREFIX}tabs-content"),
                        curves_checklist(f'{PAGE_PREFIX}curve-checklist', 'IdVd')   # checklist curve visualizzate
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
idvd_cbs = _register_all_callbacks('IdVd')