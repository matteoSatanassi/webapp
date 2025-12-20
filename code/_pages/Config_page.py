from dash import register_page, dcc, html
import dash_bootstrap_components as dbc
from app_elements.configs_layouts import *

register_page(__name__, path='/configs', title='Configs')

## LAYOUT ##
layout = dbc.Container([
    dcc.Store(id="current-theme", data=None),
    dcc.Store(id="initial-config-loaded", data=False),

    dcc.Loading(
        id="loading-main-configs",
        fullscreen=True,
        children=[
            html.H1("⚙️ Centro Configurazione", className="mb-4 mt-3"),

            dbc.Tabs([
                # TAB 1: Impostazioni Generali (Tuo layout attuale)
                dbc.Tab(label="🖥️ Generali", tab_id="tab-general", children=[
                    html.Div([
                        app_configs_layout
                    ], className="mt-4")
                ]),

                # TAB 2: Struttura File (files_configs.json)
                dbc.Tab(label="📂 Struttura File", tab_id="tab-files-json", children=[
                    html.Div([
                        files_configs_layout
                    ], className="mt-2")
                ]),

                # TAB 3: Stili Grafici (PlotterConfigs.json)
                dbc.Tab(label="📊 Stili Grafici", tab_id="tab-plotter-json", children=[
                    html.Div([
                        plotter_configs_layout
                    ], className="mt-2")
                ]),
            ], id="main-config-tabs", active_tab="tab-general"),

            # Pulsanti di salvataggio globali (sempre visibili in fondo)
            dbc.Row([
                dbc.Col([
                    dbc.Button("Salva Tutto", id="save-config-button", color="success", size="lg"),
                    dbc.Button("Ripristina", id="reset-config-button", color="warning", className="ms-2"),
                ], width=12, className="mt-4 pb-5")
            ])
        ]
    )
], fluid=True)

