import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from plotter.code.app_elements import *

dash.register_page(__name__, path='/IdVd-plotter')

## PARAMS ##
PAGE_PREFIX = 'IdVd'

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
                            mode_options(f'{PAGE_PREFIX}-mode-toggle'),
                            html.Div(style={'height': '15px'}),

                            # Tabella
                            html.Div(
                                my_table_template(f'{PAGE_PREFIX}-table', 'IdVd'),
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
                                        id=f'{PAGE_PREFIX}-plot-button',
                                        color="primary",
                                        className="w-100 mt-3",
                                        size="lg"
                                    ),
                                    dbc.Button(
                                        "💾 Esporta",
                                        id=f'{PAGE_PREFIX}-open-modal-button',
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
                        # dbc.CardHeader([
                        #     html.Div([
                        #         html.H5("📈 Visualizzazione Grafici", className="mb-0"),
                        #         html.Small("Interagisci con i grafici generati",
                        #                    style={'color': '#6c757d'})
                        #     ], className="mb-4 me-auto"),
                        #     html.Div([
                        #         dbc.Row([
                        #             dbc.Col([
                        #                 dbc.Button(
                        #                     "❌ Chiudi tab corrente",
                        #                     id=f"{PAGE_PREFIX}-close-current-tab-button",
                        #                     color="outline-warning",
                        #                     size="sm",
                        #                 )
                        #             ]),
                        #             dbc.Col([
                        #                 dbc.DropdownMenu(
                        #                     label="⚙️ Gestione Tab",
                        #                     color="outline-secondary",
                        #                     id=f"{PAGE_PREFIX}-tab-management-menu",
                        #                     size="sm",
                        #                 )
                        #             ])
                        #         ])
                        #     ], className="float-end")#, style={'display': 'none'}),
                        # ], className="d-flex align-items-center w-100"),
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
                                        id=f"{PAGE_PREFIX}-close-current-tab-button",
                                        color="outline-warning",
                                        size="sm",
                                        className="me-2",
                                        style={'display': 'none'}
                                    ),
                                    dbc.DropdownMenu(
                                        label="⚙️ Gestione",
                                        children=[
                                            dbc.DropdownMenuItem("🗑️ Chiudi tutti tranne corrente",
                                                                 id=f"{PAGE_PREFIX}-close-other-tabs"),
                                            dbc.DropdownMenuItem(divider=True),
                                            dbc.DropdownMenuItem("🔄 Ripristina tab",
                                                                 id=f"{PAGE_PREFIX}-restore-tabs"),
                                        ],
                                        color="outline-secondary",
                                        size="sm",
                                        id=f"{PAGE_PREFIX}-tab-management-menu",
                                        style={'display': 'none'}
                                    )
                                ], className="d-flex align-items-center")
                            ], className="d-flex justify-content-between align-items-center w-100")
                        ], className="py-2"),
                        dbc.CardBody([
                            # Tabs dei grafici
                            dcc.Tabs(
                                id=f"{PAGE_PREFIX}-tabs",
                                value=None,
                                className="custom-tabs",
                                children=[]
                            ),
                            # Contenitore grafico tab selezionato
                            html.Div(
                                id=f"{PAGE_PREFIX}-tabs-content",
                                style={'minHeight': '600px', 'padding': '15px'}
                            ),
                            # Controlli grafici
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "🔄 Aggiorna Vista",
                                            id=f"{PAGE_PREFIX}-refresh-view",
                                            color="outline-primary",
                                            size="md",
                                            className="w-100"
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Button(
                                            "📥 Scarica Immagine",
                                            id=f"{PAGE_PREFIX}-download-plot",
                                            color="outline-success",
                                            size="md",
                                            className="w-100"
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Button(
                                            "⚙️ Personalizza",
                                            id=f"{PAGE_PREFIX}-customize-plot",
                                            color="outline-secondary",
                                            size="md",
                                            className="w-100"
                                        )
                                    ], width=4)
                                ], className="mt-3")
                            ],
                                id=f"{PAGE_PREFIX}-graph-controls",
                                style={'display': 'none'}
                            )]
                        )
                    ], className="shadow-sm")
                ], width=12)
            ])
        ], label="📈 Grafici", tab_id="tab-graphs"),
    ], id=f"{PAGE_PREFIX}-main-tabs", active_tab="tab-table"),

    # MODAL ESPORTAZIONE
    export_modal(f'{PAGE_PREFIX}-modal', 'IdVd'),

    # LOADING SPINNER
    dcc.Loading(
        id=f"{PAGE_PREFIX}-loading",
        type="circle",
        children=html.Div(id=f"{PAGE_PREFIX}-loading-output"),
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

## CALLBACKS ##
idvd_cbs = _register_all_callbacks('IdVd')

from dash import callback, Input, Output

@callback(
    Output(f"{PAGE_PREFIX}-main-tabs", "active_tab"),
    Input(f'{PAGE_PREFIX}-plot-button', 'n_clicks'),
    prevent_initial_call=True
)
def switch_to_graphs_tab(n_clicks):
    """Passa alla tab dei grafici quando si clicca su 'Genera Grafico'"""
    if n_clicks:
        return "tab-graphs"
    return "tab-table"