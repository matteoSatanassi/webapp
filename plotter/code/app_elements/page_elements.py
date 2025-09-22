from dash import  dcc, dash_table, html
import dash_bootstrap_components as dbc
from .parameters import IdVd_table_exp_mode,TrapData_table, load_configs

## PARAMS ##
CURVE_CHECKLIST_IDVD = [
    {'label': 'Curva (0,0)', 'value': 'v0'},
    {'label': 'Curva (-7,0)', 'value': '0'},
    {'label': 'Curva (-7,15)', 'value': '15'},
    {'label': 'Curva (-7,30)', 'value': '30'},
]
CURVE_CHECKLIST_TRAPDATA = [
    {'label': 'trap_density', 'value': 'trap_density'},
    {'label': 'x=0.5µm', 'value': '0.5000'},
    {'label': 'x=0.616µm', 'value': '0.6160'},
    {'label': 'x=0.766µm', 'value': '0.7660'},
    {'label': 'x=0.783µm', 'value': '0.7830'},
    {'label': 'x=0.95µm', 'value': '0.9500'},
    {'label': 'x=0.967µm', 'value': '0.9670'},
    {'label': 'x=0.984µm', 'value': '0.9840'},
    {'label': 'x=1.184µm', 'value': '1.1840'},
    {'label': 'x=1.334µm', 'value': '1.3340'},
    {'label': 'x=1.834µm', 'value': '1.8340'}
]
TABLE_COLUMNS_IDVD = [
    {'name': 'Trap Distribution', 'id': 'trap_distr'},
    {'name': 'E_mid', 'id': 'e_mid'},
    {'name': 'E_σ', 'id': 'e_sigma'},
    {'name': 'V_gf', 'id': 'v_gf'},
    {'name': 'file_path', 'id': 'file_path'},
    {'name': 'group', 'id': 'group'},
]
TABLE_COLUMNS_TRAPDATA = [
    {'name': 'Trap Distribution', 'id': 'trap_distr'},
    {'name': 'E_mid', 'id': 'e_mid'},
    {'name': 'E_σ', 'id': 'e_sigma'},
    {'name': 'V_gf', 'id': 'v_gf'},
    {'name': 'file_path', 'id': 'file_path'},
    {'name': 'Start Condition', 'id': 'start_cond'},
]

## PAGE ELEMENTS ##
def my_table_template(table_id:dict[str,str]) -> dash_table.DataTable:
    try:
        page = table_id['page']
    except KeyError:
        raise KeyError('valore di pagina non trovato')

    if page=='IdVd':
        columns = TABLE_COLUMNS_IDVD
    elif page=='TrapData':
        columns = TABLE_COLUMNS_TRAPDATA
    else:
        raise ValueError('Non supportati modi diversi da IdVd o TrapData')

    return dash_table.DataTable(
        id=table_id,
        data=IdVd_table_exp_mode if page=='IdVd' else TrapData_table,
        columns=columns,
        sort_action='native',
        filter_action='native',
        filter_options={"placeholder_text": "Filter column..."},
        row_selectable='multi',
        selected_rows=[],
        hidden_columns=['file_path', 'group' if page == 'IdVd' else None],
        page_size=10,
        # ✅ MIGLIORATO: Stili per migliore leggibilità
        style_cell={
            'textAlign': 'right',
            'padding': '8px 12px',  # ✅ Più padding
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '13px',     # ✅ Dimensione font leggermente aumentata
            'minWidth': '80px',     # ✅ Larghezza minima garantita
            'maxWidth': '150px',    # ✅ Larghezza massima
            'whiteSpace': 'normal'  # ✅ Testo che va a capo
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'trap_distr'},
                'textAlign': 'left',
                'minWidth': '120px',  # ✅ Più spazio per i nomi
                'fontWeight': '500'
            },
            {
                'if': {'column_id': 'e_mid'},
                'minWidth': '90px'
            },
            {
                'if': {'column_id': 'e_sigma'},
                'minWidth': '90px'
            },
            {
                'if': {'column_id': 'v_gf'},
                'minWidth': '80px'
            }
        ],
        style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'border': '1px solid #f0f0f0'  # ✅ Bordi più sottili
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(240, 240, 240)',  # ✅ Contrasto migliore
            }
        ],
        style_header={
            'backgroundColor': 'rgb(100, 100, 100)',  # ✅ Header più scuro
            'color': 'white',
            'fontWeight': 'bold',
            'fontSize': '14px',      # ✅ Font header più grande
            'padding': '12px 15px',  # ✅ Più padding per header
            'textAlign': 'center',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        fixed_rows={'headers': True},
        # ✅ Nuove proprietà per migliore esperienza
        tooltip_data=[],
        tooltip_duration=None,
        style_table={
            'minWidth': '100%',     # ✅ Occupa tutto lo spazio disponibile
            'overflowX': 'auto'     # ✅ Scroll orizzontale se necessario
        }
    )

def mode_options(radio_id:dict[str,str])->dcc.RadioItems:
    """
    Crea una lista in cui scegliere l'opzione di visualizzazione delle tabelle nella pagina IdVd

    Le opzioni sono Exp mode e Group mode
    """
    try:
        page = radio_id['page']
    except KeyError:
        raise KeyError('valore di pagina non trovato')
    return dcc.RadioItems(
        [
            {"label": "📊 Modalità Esperimento", "value": "ExpMode"},
            {"label": "👥 Modalità Gruppo", "value": "GroupMode"}
         ],
        value='ExpMode',
        id=radio_id,
        inline=True,
        className='spaced-radio-items',
        labelStyle={'margin-bottom': '15px'},
        style={'display': 'none' if page!='IdVd' else 'block'},
    )

def export_modal(modal_id:dict[str,str])->dbc.Modal:
    """Crea una finestra pop-up in cui selezionare la curve da esportare"""
    try:
        page = modal_id['page']
    except KeyError:
        raise KeyError('valore di pagina non trovato')

    if page not in ('IdVd', 'TrapData'):
        raise ValueError('Non supportati pagine diverse da IdVd o TrapData')

    curves_checklist_opt = CURVE_CHECKLIST_IDVD if page=='IdVd' else CURVE_CHECKLIST_TRAPDATA

    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("🖨️ Esportazione Grafici")),
        dbc.ModalBody(
            dbc.Container([
                # Riga 1: Tabella e selezione impostazioni esportazione
                dbc.Row([
                    # Colonna con tabella, mode selector
                    dbc.Col([
                        mode_options({'page':page, 'item':'radio-mode-toggle', 'location':'modal'}),
                        html.Div(
                            my_table_template({'page':page, 'item':'table', 'location':'modal'}),
                            style={"overflow-y": "auto"}
                        )
                    ],
                        width=7
                    ),

                    # Colonna opzioni di esportazione
                    dbc.Col([
                        # Checklist curve
                        dbc.Card([
                            dbc.CardHeader("📈 Curve da Esportare"),
                            dbc.CardBody(
                                dbc.Checklist(
                                    id={'page':page, 'item':'checklist-curves', 'location':'modal'},
                                    options=curves_checklist_opt,
                                    value=[curve['value'] for curve in curves_checklist_opt],
                                    inline=False,
                                    switch=True,
                                    style={"margin-bottom": "15px"}
                                )
                            )
                        ],
                            style={"margin-bottom": "15px"},
                        ),

                        # Opzioni avanzate
                        dbc.Card([
                            dbc.CardHeader("⚙️ Opzioni Avanzate"),
                            dbc.CardBody([
                                # Legenda
                                dbc.Checklist(
                                    id={'page':page, 'item':'check-legend', 'location':'modal'},
                                    options=[
                                        {"label": "Mostra Legenda", "value": "show_legend"}
                                    ],
                                    value=["show_legend"],
                                    switch=True,
                                    style={"margin-bottom": "10px"}
                                ),

                                # Colori
                                dbc.Checklist(
                                    id={'page':page, 'item':'check-colors', 'location':'modal'},
                                    options=[
                                        {"label": "Grafico a Colori", "value": "color"}
                                    ],
                                    value=["color"],
                                    switch=True,
                                    style={"margin-bottom": "15px"}
                                ),

                                # DPI
                                dbc.Row([
                                    dbc.Col(
                                        dbc.Label("DPI Immagine:"),
                                        width=6
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id={'page':page, 'item':'selector-dpi', 'location':'modal'},
                                            options=[
                                                {"label": "72 DPI (Bassa)", "value": 72},
                                                {"label": "150 DPI (Media)", "value": 150},
                                                {"label": "300 DPI (Alta)", "value": 300},
                                                {"label": "600 DPI (Altissima)","value": 600}
                                            ],
                                            value=150,
                                            clearable=False,
                                            style={"width": "100%"}
                                        ),
                                        width=6
                                    )
                                ],
                                    style={"margin-bottom": "15px"},
                                ),

                                # Formato file
                                dbc.Row([
                                    dbc.Col(
                                        dbc.Label("Formato File:"),
                                        width=6
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id={'page':page, 'item':'selector-format', 'location':'modal'},
                                            options=[
                                                {"label": "PNG", "value": "png"},
                                                {"label": "SVG", "value": "svg"},
                                                {"label": "PDF", "value": "pdf"},
                                                {"label": "JPEG", "value": "jpeg"},
                                                {"label": "WEBP", "value": "webp"}
                                            ],
                                            value=load_configs()["export_format"],
                                            clearable=False,
                                            style={"width": "100%"}
                                        ),
                                        width=6
                                    )
                                ])
                            ])
                        ])
                    ],
                        width=5
                    )
                ]),

                # Riga 2: Anteprima e Statistiche
                # dbc.Row([
                #     dbc.Col([
                #         dbc.Card([
                #             dbc.CardHeader("📊 Riepilogo Esportazione"),
                #             dbc.CardBody([
                #                 html.Div(
                #                     id=f"{page}-modal-export-summary",
                #                     children="Seleziona gli esperimenti per vedere il riepilogo",
                #                     style={
                #                         "font-size": "14px",
                #                         "padding": "10px",
                #                         "background-color": "#f8f9fa",
                #                         "border-radius": "5px"
                #                     }
                #                 )
                #             ])
                #         ])
                #     ],
                #         width=12
                #     )
                # ],
                #     style={"margin-top": "15px"},
                # )
            ],
                fluid=True,
            )
        ),

        dbc.ModalFooter([
            dbc.Button(
                "❌ Annulla", id={'page':page, 'item':'button-close-modal'}, color="secondary", class_name="me-auto", n_clicks=0
            ),
            dbc.Button(
                "💾 Esporta Selezionati", id={'page':page, 'item':'button-export'}, color="primary", disabled=True, n_clicks=0
            )

        ])
    ],
        id = modal_id,
        is_open = False,
        size='xl',
        scrollable=True,
        backdrop='static'   # Previene la chiusura cliccando fuori
    )