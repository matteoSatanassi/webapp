from dash import  dcc, dash_table, html
import dash_bootstrap_components as dbc
from .parameters import IdVd_table_exp_mode,TrapData_table

## PARAMS ##
CURVE_CHECKLIST_IDVD = [
    {'label': '(0,0)', 'value': 'v0'},
    {'label': '(-7,0)', 'value': '0'},
    {'label': '(-7,15)', 'value': '15'},
    {'label': '(-7,30)', 'value': '30'},
]
CURVE_CHECKLIST_TRAPDATA = [
    {'label': 'trap_density', 'value': 'trap_density'},
    {'label': '0.5000', 'value': '0.5000'},
    {'label': '0.6160', 'value': '0.6160'},
    {'label': '0.7660', 'value': '0.7660'},
    {'label': '0.7830', 'value': '0.7830'},
    {'label': '0.9500', 'value': '0.9500'},
    {'label': '0.9670', 'value': '0.9670'},
    {'label': '0.9840', 'value': '0.9840'},
    {'label': '1.1840', 'value': '1.1840'},
    {'label': '1.3340', 'value': '1.3340'},
    {'label': '1.8340', 'value': '1.8340'}
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
def my_table_template(table_id:str,page:str)->dash_table.DataTable:
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
        style_cell={'textAlign': 'right'},
        style_cell_conditional=[
            {
                'if': {'column_id': 'trap_distr'},
                'textAlign': 'left'
            }
        ],
        style_data={
            'color': 'black',
            'backgroundColor': 'white'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'whiteSpace': 'normal',
            'height': 'auto',
            'textAlign': 'center'
        },
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        fixed_rows={'headers': True},
    )

def mode_options(radio_id:str)->dcc.RadioItems:
    """
    Crea una lista in cui scegliere l'opzione di visualizzazione delle tabelle nella pagina IdVd

    Le opzioni sono Exp mode e Group mode
    """
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
    )

def curves_checklist(checklist_id:str, page:str)->dcc.Checklist:
    """
    Crea una checklist in cui selezionare la curve da visualizzare
    :param checklist_id: id dell'oggetto dcc.Checklist che verrà utilizzato
    :param page: 'IdVd'/'TrapData', in base alla lista di curve da visualizzare
    """
    if page == 'IdVd':
        options = CURVE_CHECKLIST_IDVD
    elif page == 'TrapData':
        options = CURVE_CHECKLIST_TRAPDATA
    else:
        raise ValueError('Non supportati modi diversi da IdVd o TrapData')
    start_value = [element['value'] for element in options]
    return dcc.Checklist(
        id=checklist_id,
        options=options,
        value=start_value,  # all’inizio tutte selezionate
        labelStyle={'display': 'inline-block'},
    )

def export_modal(modal_id:str, page:str)->dbc.Modal:
    """
        Crea una finestra pop-up in cui selezionare la curve da visualizzare
        :param modal_id: id dell'oggetto dbc.Modal che verrà utilizzato
        :param page: 'IdVd'/'TrapData', in base alla lista di curve da visualizzare
        """
    if page!='IdVd' and page!='TrapData':
        raise ValueError('Non supportati pagine diverse da IdVd o TrapData')
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("🖨️ Esportazione Grafici")),
        dbc.ModalBody(
            dbc.Container([
                # Riga 1: Tabella e selezione impostazioni esportazione
                dbc.Row([
                    dbc.Col([
                        mode_options(f"{page}-modal-mode-toggle"),
                        html.Div(
                            my_table_template(f"{page}-modal-table",page),
                            style={"height": "300px", "overflow-y": "auto"}
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
                                    id=f"{page}-modal-curve-checklist",
                                    options=[
                                        {"label": "Curva (0,0)", "value": "v0"},
                                        {"label": "Curva (-7,0)", "value": "0"},
                                        {"label": "Curva (-7,15)", "value": "15"},
                                        {"label": "Curva (-7,30)", "value": "30"}
                                    ],
                                    value=["v0", "0", "15", "30"],
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
                                    id=f"{page}-modal-legend-toggle",
                                    options=[
                                        {"label": "Mostra Legenda", "value": "show_legend"}
                                    ],
                                    value=["show_legend"],
                                    switch=True,
                                    style={"margin-bottom": "10px"}
                                ),

                                # Colori
                                dbc.Checklist(
                                    id=f"{page}-modal-color-toggle",
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
                                            id=f"{page}-modal-dpi-selector",
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
                                            id=f"{page}-modal-format-selector",
                                            options=[
                                                {"label": "PNG", "value": "png"},
                                                {"label": "SVG", "value": "svg"},
                                                {"label": "PDF", "value": "pdf"},
                                                {"label": "JPEG", "value": "jpeg"},
                                                {"label": "WEBP", "value": "webp"}
                                            ],
                                            value="png",
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
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("📊 Riepilogo Esportazione"),
                            dbc.CardBody([
                                html.Div(
                                    id=f"{page}-modal-export-summary",
                                    children="Seleziona gli esperimenti per vedere il riepilogo",
                                    style={
                                        "font-size": "14px",
                                        "padding": "10px",
                                        "background-color": "#f8f9fa",
                                        "border-radius": "5px"
                                    }
                                )
                            ])
                        ])
                    ],
                        width=12
                    )
                ],
                    style={"margin-top": "15px"},
                )
            ],
                fluid=True,
            )
        ),

        dbc.ModalFooter([
            dbc.Button(
                "❌ Annulla", id=f"{page}-modal-close-button", color="secondary", class_name="me-auto", n_clicks=0
            ),
            dbc.Button(
                "💾 Esporta Selezionati", id=f"{page}-modal-export-button", color="primary", disabled=True, n_clicks=0
            )

        ])
    ],
        id = modal_id,
        is_open = False,
        size='xl',
        scrollable=True,
        backdrop='static'   # Previene la chiusura cliccando fuori
    )

# dbc.ModalBody(
#             dbc.Row([
#                 dbc.Col(my_table_template(f'{page}-modal-table', page)),
#                 dbc.Col([
#                         mode_options(f'{page}-modal-mode-toggle') if page=='IdVd' else None,
#                         curves_checklist(f'{page}-modal-curves-checklist', page)
#                 ])
#             ])
#         ),
#         dbc.ModalFooter([
#                 dbc.Button("Close", id=f"{page}-modal-close-button", className="ms-auto", n_clicks=0),
#                 dbc.Button("Export Selected", id=f"{page}-modal-export-button", className="ms-auto", n_clicks=0)
#         ])