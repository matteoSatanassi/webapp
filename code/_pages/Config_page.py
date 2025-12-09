from dash import register_page, dcc, html
from app_elements.callbacks.ConfigPage_cbks import *

register_page(__name__, path='/configs', title='Configs')

## LAYOUT ##
layout = dbc.Container([
    dcc.Store(id="current-theme", data=None),
    dcc.Store(id="initial-config-loaded", data=False),

    dcc.Loading(
        id="main-loading",
        fullscreen=True,
        custom_spinner=custom_spinner("Config Page"),
        overlay_style={"visibility": "visible", "filter": "blur(2px)"},
        delay_show=800,
        delay=500,
        children=[
            html.H1("Configurazione Applicazione", className="mb-4 mt-3"),

            dbc.Card([
                dbc.CardHeader("Impostazioni Esportazione", className="bg-info"),
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
                dbc.CardHeader("Impostazioni Dati", className="bg-info"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Cartella Dati"),
                            dbc.InputGroup([
                                dbc.Input(
                                    id="config-data-path",
                                    value="",
                                    type="text"
                                ),
                            ]),
                            dbc.FormText("Cartella contenente i file da visualizzare")
                        ], width=6),
                    ])
                ])
            ], className="mb-4"),

            dbc.Card([
                dbc.CardHeader("Impostazioni Grafiche", className="bg-info"),
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
                                ThemeChangerAIO(
                                    aio_id="theme",
                                    radio_props={
                                        "value": getattr(dbc.themes, GLOBAL_CACHE.app_configs.theme)
                                    }),
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
                ], width="auto")
            ], align="center", className="mt-4"),

            html.Div(className="mb-4"),
        ])
])
