import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from plotter.code.app_elements import *

dash.register_page(__name__, path='/IdVd-plotter')

## PARAMS ##
PAGE_PREFIX = 'IdVd'

## LAYOUT ##
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
                mode_options(f'{PAGE_PREFIX}-mode-toggle'),
                my_table_template(f'{PAGE_PREFIX}-table','IdVd')
            ],
            width=4,    #larghezza colonna
            style={'textAlign': 'center'},
        ),  #ELENCO FILE

        dbc.Col(
            html.Div([
                dbc.Button(
                    "Plot ->",
                    id=f'{PAGE_PREFIX}-plot-button',
                    className="me-2",
                    color="primary"
                ),

                dbc.Button(
                    "Export!",
                    id=f'{PAGE_PREFIX}-open-modal-button',
                    className="me-2",
                    color="primary"
                ),

                export_modal(f'{PAGE_PREFIX}-modal','IdVd'),
            ]),
            style={'textAlign': 'center'},
            class_name="d-flex justify-content-center",
            width=1
        ),  #BOTTONI

        dbc.Col([
                dcc.Tabs(id=f"{PAGE_PREFIX}-tabs", value=None),
                html.Div(id=f"{PAGE_PREFIX}-tabs-content")
        ],
            style={'textAlign': 'center'},
            width=7     #larghezza colonna
        ),  #TABS GRAFICI E CHECKLIST CURVE
        ],
            align="center",
            style={'height':'60vh', 'margin':'5vh'}
        ),  #GRAFICO+TABELLA
],
    fluid=True,
    className='IdVd_dashboard'
)

## CALLBACKS ##
idvd_cbs = _register_all_callbacks('IdVd')