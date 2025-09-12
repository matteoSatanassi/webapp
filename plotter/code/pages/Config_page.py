import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import json
from plotter.code.app_elements import load_configs, config_path

dash.register_page(__name__, path='/configs', title='configs')

## PARAMS ##
config_dict = load_configs()

## FUNC ##
def save_config(config):
    """Salva la configurazione aggiornata"""
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

## LAYOUT ##
layout = dbc.Container([
    html.H1("Configurazione Applicazione", className="mb-4"),

    dbc.Card([
        dbc.CardHeader("Impostazioni Esportazione"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Cartella di Esportazione"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="config-export-path",
                            value=config_dict["export_directory"],
                            type="text"
                        ),
                        dbc.Button(
                            "Sfoglia",
                            id="browse-button",
                            color="secondary"
                        )
                    ]),
                    dbc.FormText("Cartella dove salvare i file esportati")
                ], width=6),

                dbc.Col([
                    dbc.Label("Formato di Esportazione"),
                    dcc.Dropdown(
                        id="config-export-format",
                        options=[
                            {'label': 'PNG', 'value': 'png'},
                            {'label': 'SVG', 'value': 'svg'},
                            {'label': 'PDF', 'value': 'pdf'},
                            {'label': 'JPEG', 'value': 'jpeg'}
                        ],
                        value=config_dict
                        ["export_format"],
                        clearable=False
                    )
                ], width=6)
            ])
        ])
    ], className="mb-4"),

    dbc.Card([
        dbc.CardHeader("Impostazioni Grafiche"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Tema Grafico"),
                    dcc.Dropdown(
                        id="config-theme",
                        options=[
                            {'label': 'Superhero', 'value': 'SUPERHERO'},
                            {'label': 'Bootstrap', 'value': 'BOOTSTRAP'},
                            {'label': 'Material', 'value': 'MATERIAL'}
                        ],
                        value=config_dict["theme"],
                        clearable=False
                    )
                ], width=6)
            ])
        ])
    ], className="mb-4"),

    dbc.Button("Salva Configurazione",
               id="save-config-button",
               color="primary",
               className="me-2"),

    dbc.Button("Ripristina Predefiniti",
               id="reset-config-button",
               color="warning",
               className="me-2"),

    html.Div(id="config-status-message", className="mt-3")
])