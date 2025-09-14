from dash import dcc, html, Input, Output, State, callback, register_page
from pathlib import Path
import dash_bootstrap_components as dbc
import json
from plotter.code.app_elements import load_configs, config_path

register_page(__name__, path='/configs', title='configs')

## PARAMS ##
config = load_configs()

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
                            value=config["export_directory"],
                            type="text"
                        ),
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
                        value=config["export_format"],
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
                            {'label': 'Materia', 'value': 'MATERIA'}
                        ],
                        value=config["theme"],
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

@callback(
    Output("config-status-message", "children"),
    Output("config-export-path", "value"),
    Output("config-export-format", "value"),
    Output("config-theme", "value"),
    Input("save-config-button", "n_clicks"),
    State("config-export-path", "value"),
    State("config-export-format", "value"),
    State("config-theme", "value"),
)
def save(n_clicks, export_path, export_format, theme):
    if not n_clicks:
        return "", export_path, export_format, theme
    try:
        path = Path(export_path)
    except (OSError, ValueError):
        return "L'indirizzo di esportazione fornito non è valido", load_configs()["export_directory"]
    global config, app
    config = {
        "export_directory": export_path,
        "export_format": export_format,
        "theme": theme
    }
    save_config(config)
    return "Impostazioni salvate!", config["export_directory"], config["export_format"], config["theme"]

@callback(
    Output("config-status-message", "children", allow_duplicate=True),
    Output("config-export-path", "value", allow_duplicate=True),
    Output("config-export-format", "value", allow_duplicate=True),
    Output("config-theme", "value", allow_duplicate=True),
    Input("reset-config-button", "n_clicks"),
    State("config-export-path", "value"),
    State("config-export-format", "value"),
    State("config-theme", "value"),
    prevent_initial_call=True
)
def reset(n_clicks, export_path, export_format, theme):
    global config, app
    if not n_clicks:
        return "", export_path, export_format, theme
    try:
        config_path.unlink(missing_ok=True)
    except Exception as e:
        return f"Errore reset config_file: {e}", config["export_directory"], config["export_format"], config["theme"]
    config = load_configs()
    return f"Impostazioni resettate!", config["export_directory"], config["export_format"], config["theme"]
