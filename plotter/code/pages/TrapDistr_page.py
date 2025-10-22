import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from app_elements import *

dash.register_page(__name__, path='/TrapData-plotter', name='TrapData')

## PARAMS ##
PAGE = "TrapData"

## LAYOUT ##
layout = dbc.Container([
    # TABS PRINCIPALI
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
                        ], className="py-2 bg-info"),
                        dbc.CardBody([
                            # Opzioni di visualizzazione
                            mode_options({'page':PAGE, 'item':'radio-mode-toggle', 'location':'main-page'}),

                            # Tabella
                            html.Div(
                                my_table_template({'page':PAGE, 'item':'table', 'location':'main-page'}),
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
                                        id={'page':PAGE, 'item':'button-plot', 'location':'main-page'},
                                        color="secondary",
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
        dbc.Tab(
            dcc.Loading(
                id={'page':PAGE, 'item':'loading-graph-tab'},
                fullscreen=True,
                custom_spinner=custom_spinner("Esportando!"),
                overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                delay_show=500,
                children=[
                    dbc.Row([
                        dbc.Col([
                            dcc.Store(id={'page': PAGE, 'item': 'store-loading-placeholder', 'location': 'page'},
                                      data=None),

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
                                                color="outline-danger",
                                                size="sm",
                                                className="me-2",
                                                style={'display': 'none'}
                                            ),
                                            dbc.DropdownMenu(
                                                label="⚙️ Gestione tab",
                                                children=[],
                                                color="warning",
                                                size="sm",
                                                id={'page':PAGE, 'item':'menu-tab-management'},
                                                style={'display': 'none'}
                                            )
                                        ], className="d-flex align-items-center")
                                    ], className="d-flex justify-content-between align-items-center w-100")
                                ], className="py-2 bg-info"),
                                dbc.CardBody([
                                    # Tabs dei grafici
                                    dcc.Tabs(
                                        id={'page':PAGE, 'item': 'graph-tabs'},
                                        value=None,
                                        className="custom-tabs",
                                        children=[],
                                    ),
                                    # Contenitore grafico tab selezionato
                                    html.Div(
                                        id={'page':PAGE, 'item': 'graph-tabs-content'},
                                        className="p-0 m-0"
                                    ),
                                    # Controlli grafici
                                    html.Div([
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button(
                                                    "📥 Scarica Immagine",
                                                    id={'page':PAGE, 'item':'button-export-current-graph'},
                                                    color="outline-success",
                                                    size="md",
                                                    className="w-100"
                                                )
                                            ], width=4),
                                            # dbc.Col([
                                            #     dbc.Button(
                                            #         "➕ Aggiungi a 'da esportare'",
                                            #         id={'page':PAGE, 'item':'button-add-current-to-export'},
                                            #         color="outline-secondary",
                                            #         size="md",
                                            #         className="w-100"
                                            #     )
                                            # ], width=4)
                                        ], className="d-flex flex-row-reverse")
                                    ],
                                        id={'page':PAGE, 'item':'graph-controls'},
                                        style={'display': 'none'}
                                    )
                                ])
                            ], className="shadow-sm")
                        ], width=12)
                    ])
                ]
            ), label="📈 Grafici", tab_id="tab-graphs"),
    ], id={'page':PAGE, 'item':'main-tabs'}, active_tab="tab-table"),

    # MODAL ESPORTAZIONE
    export_modal({'page':PAGE, 'item':'modal'}),
],
    fluid=True,
    className='IdVd_dashboard py-4',
    style={
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh'
    }
)