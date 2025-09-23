from dash import dcc, html, Input, Output, State, callback, register_page, no_update
from pathlib import Path
from dash_bootstrap_templates import ThemeChangerAIO
import dash_bootstrap_components as dbc
import json
from plotter.code.app_elements import load_configs, config_path

register_page(__name__, path='/configs', title='configs')

## FUNC ##
def save_config(conf):
    """Salva la configurazione aggiornata"""
    with open(config_path, 'w') as f:
        json.dump(conf, f, indent=4)

## LAYOUT ##
layout = dbc.Container([
    dcc.Store(id="current-theme", data=None),
    dcc.Store(id="initial-config-loaded", data=False),

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
                            value="",
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
                        value='png',
                        clearable=False,
                        style={"width": "100%"},
                    ),
                    dbc.FormText("Formato dei file esportati")
                ], width=6)
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Checklist(
                        id='config-legend-colors-checklist',
                        options=[
                            {"label": "Mostra Legenda", "value": "show_legend"},
                            {"label": "Grafico a Colori", "value": "colors"}
                        ],
                        value=["show_legend", "colors"],
                        switch=True
                    ),
                ], width=6, className="vertical-center"),
                dbc.Col([
                    dbc.Label("Risoluzione (DPI)"),
                    dcc.Dropdown(
                        id="config-DPI-selector",
                        options=[
                            {"label": "72 DPI (Bassa)", "value": 72},
                            {"label": "150 DPI (Media)", "value": 150},
                            {"label": "300 DPI (Alta)", "value": 300},
                            {"label": "600 DPI (Altissima)", "value": 600}
                        ],
                        value=150,
                        clearable=False,
                        style={"width": "100%"},
                        className="custom-dropdown",
                    ),
                    dbc.FormText("Qualità dell'immagine esportata")
                ], width=6)
            ])
        ])
    ], className="mb-4"),

    dbc.Card([
        dbc.CardHeader("Impostazioni Grafiche"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Tema Applicazione"),
                    dcc.Dropdown(
                        id="config-theme",
                        options=[
                            {'label': 'Cerulean', 'value': 'CERULEAN'},
                            {'label': 'Cosmo', 'value': 'COSMO'},
                            {'label': 'Cyborg', 'value': 'CYBORG'},
                            {'label': 'Journal', 'value': 'JOURNAL'},
                            {'label': 'Lux', 'value': 'LUX'},
                            {'label': 'Materia', 'value': 'MATERIA'},
                            {'label': 'Minty', 'value': 'MINTY'},
                            {'label': 'Pulse', 'value': 'PULSE'},
                            {'label': 'Quartz', 'value': 'QUARTZ'},
                            {'label': 'Simplex', 'value': 'SIMPLEX'},
                            {'label': 'Superhero', 'value': 'SUPERHERO'},
                            {'label': 'Zephyr', 'value': 'ZEPHYR'},
                        ],
                        value=None,
                        clearable=False
                    ),
                    html.Div(
                        ThemeChangerAIO(aio_id="theme", radio_props={"value": getattr(dbc.themes, load_configs()["theme"])}),
                        style={'display': 'none'}
                    ),
                ], width=6)
            ])
        ])
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Button("Salva Configurazione",
                       id="save-config-button",
                       color="primary",
                       className="me-2"),
        ], width="auto"),

        dbc.Col([
            dbc.Button("Ripristina Predefiniti",
                       id="reset-config-button",
                       color="warning",
                       className="me-2"),
        ], width="auto"),

        dbc.Col([
            html.Div(id="config-status-message",
                     style={
                         'marginLeft': '15px',
                         'padding': '10px',
                         'minHeight': '38px',
                         'display': 'flex',
                         'alignItems': 'center',
                         'fontWeight': 'bold'
                     })
        ], width=True)
    ], align="center", className="mt-4"),

    html.Div(className="mt-3")
])


## CALLBACKS ##
@callback(
    Output("config-export-path", "value"),
    Output("config-export-format", "value"),
    Output("config-theme", "value"),
    Output("current-theme", "data"),
    Output(ThemeChangerAIO.ids.radio("theme"), "value"),

    Output("config-legend-colors-checklist", "value"),
    Output("config-DPI-selector", "value"),

    Output("initial-config-loaded", "data"),
    Input("initial-config-loaded", "data"),
)
def initialize_config_values(is_loaded):
    """Inizializza i valori della pagina e non permette ulteriori aggiornamenti"""
    if is_loaded:
        return no_update, no_update, no_update, no_update, no_update, no_update

    config = load_configs()

    checklist_values = []
    if bool(config['legend']):
        checklist_values.append('show_legend')
    if bool(config['colors']):
        checklist_values.append('colors')

    return (
        config["export_directory"],
        config["export_format"],
        config["theme"],
        config["theme"],
        checklist_values,
        int(config['DPI']),
        getattr(dbc.themes, config["theme"]),
        True  # Marca come caricato
    )

@callback(
    Output("config-status-message", "children", allow_duplicate=True),
    Output("current-theme", "data", allow_duplicate=True),
    Output(ThemeChangerAIO.ids.radio("theme"), "value", allow_duplicate=True),
    Output("config-export-path", "value", allow_duplicate=True),
    Output("config-export-format", "value", allow_duplicate=True),
    Output("config-theme", "value", allow_duplicate=True),
    Input("save-config-button", "n_clicks"),
    State("config-export-path", "value"),
    State("config-export-format", "value"),
    State("config-theme", "value"),
    State("current-theme", "data"),
    prevent_initial_call=True
)
def save(n_clicks, export_path, export_format, theme, current_theme):
    if not n_clicks:
        return "", current_theme, getattr(dbc.themes, current_theme), export_path, export_format, theme
    try:
        path = Path(export_path)
    except (OSError, ValueError):
        return ("L'indirizzo di esportazione fornito non è valido", current_theme, getattr(dbc.themes, current_theme),
                export_path, export_format, theme)
    configs = {
        "export_directory": export_path,
        "export_format": export_format,
        "theme": theme
    }
    save_config(configs)
    current_theme = theme
    return "Impostazioni salvate!", current_theme, getattr(dbc.themes, current_theme), export_path, export_format, theme

@callback(
    Output("config-status-message", "children", allow_duplicate=True),
    Output("current-theme", "data", allow_duplicate=True),
    Output(ThemeChangerAIO.ids.radio("theme"), "value", allow_duplicate=True),
    Output("config-export-path", "value", allow_duplicate=True),
    Output("config-export-format", "value", allow_duplicate=True),
    Output("config-theme", "value", allow_duplicate=True),
    Input("reset-config-button", "n_clicks"),
    State("config-export-path", "value"),
    State("config-export-format", "value"),
    State("config-theme", "value"),
    State("current-theme", "data"),
    prevent_initial_call=True
)
def reset(n_clicks, export_path, export_format, theme, current_theme):
    if not n_clicks:
        return "", current_theme, getattr(dbc.themes, current_theme), export_path, export_format, theme
    try:
        config_path.unlink(missing_ok=True)
    except Exception as e:
        return (f"Errore reset config_file: {e}", current_theme, getattr(dbc.themes, current_theme),
                export_path, export_format, theme)
    config = load_configs()
    return ("Impostazioni resettate!", config["theme"], getattr(dbc.themes, config["theme"]),
            config["export_directory"], config["export_format"], config["theme"])
