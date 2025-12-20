"""
Il modulo contiene le definizioni di alcuni elementi che compaiono all'interno dell'applicazione
"""

from dash import  dcc, html
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from common.PlotterConfigs import PlotterConfigs
from app_resources.AppCache import GLOBAL_CACHE, TablesCache


## PAGE ELEMENTS ##
def my_table_template(table_id:dict[str,str]) -> dag.AgGrid:
    """
    Template custom per la visualizzazione dei file.

    I dati sono presi automaticamente a partire dal file di indicizzazione
    nella cartella dei dati, in base al data_type passato all'interno dell'id.

    Vengono nascoste le colonne vuote e la colonna degli indirizzi.
    Le celle vuote vengono riempite con "-".
    :param table_id:
    :return:
    """

    data, columns_defs, _ = get_table(table_id)

    return dag.AgGrid(
        id=table_id,
        rowData=data.to_dict('records'),
        columnDefs=columns_defs,
        resetColumnState=False,
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "minWidth": 100,
            # "headerClass": "center-header",  # CSS custom per allineamento header
            "cellStyle": {"display": "flex", "alignItems": "center", "justifyContent": "right"},
            "valueFormatter": {"function": "params.value == null || params.value === '' ? '-' : params.value"}
        },
        dashGridOptions={
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,  # Seleziona solo tramite checkbox
            "pagination": True,
            "paginationPageSize": 20,
            "suppressCellFocus": True,
            "animateRows": True,
            "domLayout": "autoHeight",
            "suppressColumnVirtualisation": True,
        },
        columnSize="sizeToFit",
        className="ag-theme-alpine",
        style={
            "height": "auto",
            "width": "100%",
            "fontSize": "13px",
            "fontFamily": "Arial, sans-serif"
        },
    )

    # return dash_table.DataTable(
    #     sort_action='native',
    #     filter_action='native',
    #     filter_options={"placeholder_text": "Filter column..."},
    #     row_selectable='multi',
    #     selected_rows=[],
    #     hidden_columns=cols_to_hide,
    #     page_size=10,
    #     style_cell={
    #         'textAlign': 'right',
    #         'padding': '8px 12px',
    #         'fontFamily': 'Arial, sans-serif',
    #         'fontSize': '13px',
    #         'minWidth': '80px',
    #         'maxWidth': '150px',
    #         'whiteSpace': 'normal'
    #     },
    #     style_cell_conditional=[
    #         {
    #             'if': {'column_id': 'trap_distr'},
    #             'textAlign': 'left',
    #             'minWidth': '120px',
    #             'fontWeight': '500'
    #         },
    #         {
    #             'if': {'column_id': 'e_mid'},
    #             'minWidth': '90px'
    #         },
    #         {
    #             'if': {'column_id': 'e_sigma'},
    #             'minWidth': '90px'
    #         },
    #         {
    #             'if': {'column_id': 'v_gf'},
    #             'minWidth': '80px'
    #         }
    #     ],
    #     style_data={
    #         'color': 'black',
    #         'backgroundColor': 'white',
    #         'border': '1px solid #f0f0f0'
    #     },
    #     style_data_conditional=[
    #         {
    #             'if': {'row_index': 'odd'},
    #             'backgroundColor': 'rgb(240, 240, 240)',
    #         }
    #     ],
    #     style_header={
    #         'backgroundColor': 'rgb(100, 100, 100)',
    #         'color': 'white',
    #         'fontWeight': 'bold',
    #         'fontSize': '14px',
    #         'padding': '12px 15px',
    #         'textAlign': 'center',
    #         'whiteSpace': 'normal',
    #         'height': 'auto'
    #     },
    #     css=[{"selector": ".show-hide", "rule": "display: none"}],
    #     fixed_rows={'headers': True},
    #     tooltip_data=[],
    #     tooltip_duration=None,
    #     style_table={
    #         'minWidth': '100%',
    #         'overflowX': 'auto'
    #     }
    # )

def grouping_selector(selector_id:dict[str,str]):
    """
    Crea un DropDown menu e una lista di scelta.

    Il primo serve per selezionare la feature secondo cui raggruppare tra quelle possibili;
    La seconda per decidere se visualizzare la tabella secondo i raggruppamenti o esplosa.
    """
    try:
        file_type = selector_id['page']
    except KeyError:
        raise KeyError("Valore di pagina non specificato nell'id")

    features = PlotterConfigs.files_configs[file_type].has_grouping_configuration
    if not features:
        # se non è supportata nemmeno una feature di raggruppamento,
        # non ritorno nulla
        return None

    # nasconderò le colonne vuote e la colonna dei file_path
    f_to_pop = TablesCache.cols_to_hide(
        GLOBAL_CACHE.tables.get(file_type)
    )
    f_to_pop.append("file_path")

    features = [f for f in features if f not in f_to_pop]

    # elems ids
    radio_id = selector_id.copy()
    radio_id["item"] = "radio-table-mode"

    menu_id = selector_id.copy()
    menu_id["item"] = "menu-grouping-features"

    selectors = dbc.Container([
        dbc.Row([
            dbc.Col(
                dcc.RadioItems(
                    options=[
                        {"label": "📊 files", "value": "normal"},
                        {"label": "👥 gruppi", "value": "grouped"}
                    ],
                    value='normal',
                    id=radio_id,
                    inline=True,
                    className='d-flex justify-content-around',
                    labelStyle={'margin-bottom': '15px'},
                ),
                width=5
            ),
            dbc.Col(
                dcc.Dropdown(
                    options=features,
                    value="Vgf" if "Vgf" in features else features[0],
                    id=menu_id,
                ),
                width=3,
            )
        ])
    ])

    return selectors

def custom_spinner(message:str=""):
    if not message:
        return dbc.Spinner(color="primary", size='md', spinner_class_name="ms-3")
    return html.H1([message, dbc.Spinner(color="primary", size='md', spinner_class_name="ms-3")])

def export_modal(modal_id:dict[str,str])->dbc.Modal:
    """Crea una finestra pop-up in cui selezionare le curve da esportare e i parametri di esportazione"""
    try:
        file_type = modal_id['page']
    except KeyError:
        raise KeyError("Valore di pagina non specificato nell'id")

    type_configs = GLOBAL_CACHE.files_configs[file_type]

    curves_checklist_opt = [
        {
            "value":acronym,
            "label":label
        } for acronym,label in type_configs.allowed_curves.items()
    ]

    return dbc.Modal([

        dbc.ModalHeader(dbc.ModalTitle("🖨️ Esportazione Grafici")),

        dbc.ModalBody(
            dcc.Loading(
                id={'page': file_type, 'item': 'modal-loading'},
                custom_spinner=custom_spinner("Esportando!"),
                overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                delay_show=700,
                style={"height": "100%", "overflow": "auto"},
                children=[
                    # serve come target delle callback, nel caso non ne avessero nel modal, per
                    # attivare il loading
                    dcc.Store(id={'page': file_type, 'item': 'store-placeholder-modal'}),

                    dbc.Container([
                        # Riga 1: Tabella e selezione impostazioni esportazione
                        dbc.Row([
                            # Colonna con tabella, mode selector
                            dbc.Col([
                                grouping_selector({'page':file_type, 'item':'radio-mode-toggle', 'location':'modal'}),

                                html.Div(
                                    my_table_template({'page':file_type, 'item':'table', 'location':'modal'}),
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
                                            id={'page':file_type, 'item':'checklist-curves', 'location':'modal'},
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
                                            id={'page':file_type, 'item':'check-legend', 'location':'modal'},
                                            options=[
                                                {"label": "Mostra Legenda", "value": "show_legend"}
                                            ],
                                            value=["show_legend"],
                                            switch=True,
                                            style={"margin-bottom": "10px"}
                                        ),

                                        # Colori
                                        dbc.Checklist(
                                            id={'page':file_type, 'item':'check-colors', 'location':'modal'},
                                            options=[
                                                {"label": "Grafico a Colori", "value": "colors"}
                                            ],
                                            value=["colors"],
                                            switch=True,
                                            style={"margin-bottom": "15px", 'display': 'none' if file_type!="IDVD" else 'inline-block'}
                                        ),

                                        # DPI
                                        dbc.Row([
                                            dbc.Col(
                                                dbc.Label("DPI Immagine:"),
                                                width=6
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id={'page':file_type, 'item':'selector-dpi', 'location':'modal'},
                                                    options=[
                                                        {"label": "72 DPI (Bassa)", "value": 72},
                                                        {"label": "150 DPI (Media)", "value": 150},
                                                        {"label": "300 DPI (Alta)", "value": 300},
                                                        {"label": "600 DPI (Altissima)","value": 600}
                                                    ],
                                                    value=150,
                                                    clearable=False,
                                                    style={"width": "100%"},
                                                    className="custom-dropdown"
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
                                                    id={'page':file_type, 'item':'selector-format', 'location':'modal'},
                                                    options=[
                                                        {"label": "PNG", "value": "png"},
                                                        {"label": "SVG", "value": "svg"},
                                                        {"label": "PDF", "value": "pdf"},
                                                        {"label": "JPEG", "value": "jpeg"},
                                                        {"label": "WEBP", "value": "webp"}
                                                    ],
                                                    value='png',
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
                    ], fluid=True)
                ]
            )
        ),

        dbc.ModalFooter([
            dbc.Button(
                "❌ Annulla", id={'page':file_type, 'item':'button-close-modal'}, color="secondary", class_name="me-2", n_clicks=0
            ),
            html.Div(style={'flex':'1'}),
            dbc.Button(
                "💾 Esporta Selezionati", id={'page':file_type, 'item':'button-export'}, color="primary", disabled=True, n_clicks=0
            )

        ])
    ],
        id = modal_id,
        is_open = False,
        size='xl',
        scrollable=True,
        backdrop='static'   # Previene la chiusura cliccando fuori
    )


## HELPER FUNC ##
def get_table(table_id:dict[str,str],
              only_df=False,
              grouping_feat:str=None):
    """
    Ritorna i dati per costruire la AgGrid specificata dall'id nella visualizzazione normal.
    I valori nulli sono riempiti con "-".

    :param table_id: ID della tabella di cui sono richiesti i valori.
    :param only_df: Default False. Se True la funzione ritorna solo il df letto in memoria.
    :param grouping_feat: Default None. Se diverso la funzione ritorna il df degli indici
        raggruppato secondo questo parametro.
    :return: In ordine data, il df della tabella, columns, ossia il dizionario con le informazioni di colonna
     da passare a dash, e cols_to_hide, la lista delle colonne da nascondere.
    """
    try:
        file_type = table_id['page']
    except KeyError:
        raise KeyError("Valore di pagina non specificato nell'id")

    # page è anche il nome del data_type dei file da visualizzare

    if not grouping_feat:
        data = GLOBAL_CACHE.tables.get(file_type)
        # nasconderò le colonne vuote e la colonna dei file_path
        cols_to_hide = TablesCache.cols_to_hide(data)
    else:
        data, cols_to_hide = GLOBAL_CACHE.tables.group_df(file_type, grouping_feat)

    if only_df:
        return data

    type_configs = GLOBAL_CACHE.files_configs[file_type]
    columns_defs = type_configs.get_dash_table_cols

    for col in columns_defs:
        col["hide"] = True if col["field"] in cols_to_hide else False

    return data, columns_defs, cols_to_hide

# if __name__ == '__main__':
#     datas, columnss, cols_to_hidee = get_table({'page':'IDVD', 'item':'table', 'location':'dashboard'})
#
#     print(columnss)
#     print(cols_to_hidee)