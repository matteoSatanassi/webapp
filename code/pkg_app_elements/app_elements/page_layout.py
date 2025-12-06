from app_elements.page_elements import *
from app_resources.AppCache import GLOBAL_CACHE

def layout(PAGE:str):
    ## PARAMS ##
    targets_present = GLOBAL_CACHE.files_configs[PAGE].targets_presents

    ## LAYOUT ELEMS ##
    table_tab = dbc.Tab([
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
                        dbc.Container(
                            grouping_selector({'page': PAGE, 'item': 'grouping-selectors', 'location': 'dashboard'}),
                        ),

                        # Tabella
                        dbc.Container(
                            dcc.Loading(
                                children=my_table_template({'page':PAGE, 'item':'table', 'location':'dashboard'}),
                                custom_spinner=custom_spinner(),
                                overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                                delay_show=500,  # aspetta mezzo secondo prima di mostrare lo spinner
                            ),
                            style={
                                'overflowY': 'auto',
                                'borderRadius': '5px'
                            }
                        )
                    ])
                ], className="shadow-sm")
            ], width=12)
        ]),
        # Bottoni sotto tabella
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "📊 Mostra Grafico",
                                    id={'page': PAGE, 'item': 'button-plot'},
                                    color="secondary",
                                    className="w-100 mt-3",
                                    size="lg"
                                )
                            ], md=4 if targets_present else 6),
                            dbc.Col([
                                dbc.Button(
                                    "💾 Esporta",
                                    id={'page': PAGE, 'item': 'button-open-modal'},
                                    color="success",
                                    className="w-100 mt-3",
                                    size="lg"
                                )
                            ], md=4 if targets_present else 6),
                            dbc.Col([
                                dbc.Button(
                                    "🧮 Calcola Affinità",
                                    id={'page': PAGE, 'item': 'button-calculate-affinity'},
                                    color="primary",
                                    className="w-100 mt-3",
                                    size="lg"
                                )
                            ], md=4, style={'display': 'block' if targets_present else 'none'}),
                        ])
                    ])
                ], className="mt-3 shadow-sm")
            ])
        ])
    ],
        label="📋 Tabella Esperimenti", tab_id="tab-table"
    )

    graphs_tab = dbc.Tab([
        dcc.Loading(
            id={'page':PAGE, 'item':'loading-graph-tab'},
            fullscreen=True,
            custom_spinner=custom_spinner("Esportando!"),
            overlay_style={"visibility": "visible", "filter": "blur(2px)"},
            delay_show=500, # aspetta mezzo secondo prima di mostrare lo spinner
            children=[
                # Questo store serve da output per callback che non ne hanno,
                # in modo da attivare lo spinner di loading (es. Quando esporto il grafico corrente)
                dcc.Store(id={'page':PAGE, 'item':'store-placeholder-graph-tab'}),

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
                                    ], className="py-2 me-auto"),

                                    # Pulsanti allineati a destra
                                    html.Div([
                                        dbc.Button(
                                            "❌ Chiudi corrente",
                                            id={'page': PAGE, 'item': 'button-close-current-tab'},
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
                                            id={'page': PAGE, 'item': 'menu-tab-management'},
                                            style={'display': 'none'}
                                        )
                                    ], className="d-flex align-items-center")
                                ], className="d-flex justify-content-between align-items-center w-100")
                            ], className="py-2 bg-info"),

                            dbc.CardBody([
                                # Tabs dei grafici
                                dcc.Tabs(
                                    id={'page': PAGE, 'item': 'graph-tabs'},
                                    value=None,
                                    className="custom-tabs",
                                    children=[],
                                ),

                                # Controlli grafici
                                html.Div([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button(
                                                "📥 Scarica Immagine",
                                                id={'page': PAGE, 'item': 'button-export-current-graph'},
                                                color="outline-success",
                                                size="md",
                                                className="w-100",
                                            )
                                        ], width=4),
                                        dbc.Col([
                                            dbc.Button(
                                                "👀 Visualizza target",
                                                id={'page': PAGE, 'item': 'button-target-visualize'},
                                                color="outline-secondary",
                                                size="md",
                                                className="w-100"
                                            )
                                        ], width=4, style={'display': 'block' if targets_present else 'none'}),
                                    ], className="d-flex flex-row-reverse")
                                ],
                                    id={'page': PAGE, 'item': 'graph-controls'},
                                    style={'display': 'none'}
                                )
                            ])
                        ], className="shadow-sm")
                    ], width=12)
            ])
            ]
        )
    ],
        label="📈 Grafici", tab_id="tab-graphs"
    )

    ## LAYOUT ##
    page_layout = dbc.Container(
        [
        # TABS PRINCIPALI
        dbc.Tabs([
            # TAB 1: VISUALIZZAZIONE TABELLA
            table_tab,

            # TAB 2: VISUALIZZAZIONE GRAFICI
            graphs_tab,
        ], id={'page':PAGE, 'item':'main-tabs'}, active_tab="tab-table",),

        # MODAL ESPORTAZIONE
        export_modal({'page':PAGE, 'item':'modal'}),
        ],
        fluid=True,
        className='dashboard py-4',
        style={
            'backgroundColor': 'var(--bs-light, #f8f9fa)',
            'minHeight': '100vh'
        }
    )

    return page_layout