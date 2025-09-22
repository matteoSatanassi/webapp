import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from plotter.code.app_elements import *

dash.register_page(__name__, path='/IdVd-plotter')

## PARAMS ##
PAGE = 'IdVd'

## LAYOUT ##
layout = dbc.Container([
    # INTESTAZIONE
    dbc.Row([
        dbc.Col([
            html.H1("IdVd Plotter", className="text-center mb-4",
                    style={'color': '#2c3e50', 'fontWeight': 'bold'}),
        ], width=12)
    ], className="mb-4"),

    # TABS PRINCIPALI (per alternare tra visualizzazioni)
    dbc.Tabs([
        # TAB 1: VISUALIZZAZIONE TABELLA
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    # Card per la tabella
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("📋 Esperimenti Disponibili", className="mb-0"),
                            html.Small("Seleziona gli esperimenti da analizzare",
                                       style={'color': '#6c757d'})
                        ]),
                        dbc.CardBody([
                            # Opzioni di visualizzazione
                            mode_options({'page':PAGE, 'item':'radio-mode-toggle', 'location':'page'}),
                            html.Div(style={'height': '15px'}),

                            # Tabella
                            html.Div(
                                my_table_template({'page':PAGE, 'item':'table', 'location':'page'}),
                                style={
                                    'overflowY': 'auto',
                                    'border': '1px solid #dee2e6',
                                    'borderRadius': '5px'
                                }
                            ),

                            # Bottoni sotto tabella
                            dbc.Container([
                                    dbc.Button(
                                        "📊 Genera Grafico",
                                        id={'page':PAGE, 'item':'button-plot'},
                                        color="primary",
                                        className="w-100 mt-3",
                                        size="lg"
                                    ),
                                    dbc.Button(
                                        "💾 Esporta",
                                        id={'page':PAGE, 'item':'button-open-modal'},
                                        color="success",
                                        className="w-100 mt-3",
                                        size="lg"
                                    )
                            ]),
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ])
        ], label="📋 Tabella Esperimenti", tab_id="tab-table"),

        # TAB 2: VISUALIZZAZIONE GRAFICI
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    # Card per i grafici
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                # Titolo e sottotitolo allineati a sinistra
                                html.Div([
                                    html.H5("📈 Visualizzazione Grafici", className="mb-0"),
                                    html.Small("Interagisci con i grafici generati",
                                               style={'color': '#6c757d'})
                                ], className="me-auto"),

                                # Pulsanti allineati a destra
                                html.Div([
                                    dbc.Button(
                                        "❌ Chiudi corrente",
                                        id={'page':PAGE, 'item':'button-close-current-tab'},
                                        #f"{PAGE_PREFIX}-close-current-tab-button",
                                        color="outline-warning",
                                        size="sm",
                                        className="me-2",
                                        style={'display': 'none'}
                                    ),
                                    dbc.DropdownMenu(
                                        label="⚙️ Gestione tab",
                                        children=[],
                                        color="outline-secondary",
                                        size="sm",
                                        id={'page':PAGE, 'item':'menu-tab-management'},
                                        style={'display': 'none'}
                                    )
                                ], className="d-flex align-items-center")
                            ], className="d-flex justify-content-between align-items-center w-100")
                        ], className="py-2"),
                        dbc.CardBody([
                            # Tabs dei grafici
                            dcc.Tabs(
                                id={'page':PAGE, 'item':'tabs'},
                                value=None,
                                className="custom-tabs",
                                children=[],
                            ),
                            # Contenitore grafico tab selezionato
                            html.Div(
                                id={'page':PAGE, 'item':'tabs-content'},
                                style={'minHeight': '600px', 'padding': '15px'}
                            ),
                            # Controlli grafici
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "📥 Scarica Immagine",
                                            id={'page':PAGE, 'item':'button-download-current-plot'},
                                            color="outline-success",
                                            size="md",
                                            className="w-100"
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Button(
                                            "➕ Aggiungi a 'da esportare'",
                                            id={'page':PAGE, 'item':'button-add-current-to-export'},
                                            color="outline-secondary",
                                            size="md",
                                            className="w-100"
                                        )
                                    ], width=4)
                                ], className="mt-3")
                            ],
                                id={'page':PAGE, 'item':'graph-controls'},
                                style={'display': 'none'}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ])
        ], label="📈 Grafici", tab_id="tab-graphs"),
    ], id={'page':PAGE, 'item':'main-tabs'}, active_tab="tab-table"),

    # MODAL ESPORTAZIONE
    export_modal({'page':PAGE, 'item':'modal'}),

    # LOADING SPINNER
    dcc.Loading(
        id={'page':PAGE, 'item':'loading'},
        type="circle",
        children=html.Div(id={'page':PAGE, 'item':'loading-output'}),
        fullscreen=False
    )
],
    fluid=True,
    className='IdVd_dashboard py-4',
    style={
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh'
    }
)