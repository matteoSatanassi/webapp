import pandas as pd
from dash import  dcc, dash_table, html
import dash_bootstrap_components as dbc
from params import *

## PAGE ELEMENTS ##
def my_table_template(table_id:dict[str,str]) -> dash_table.DataTable:
    """
    Template custom per la visualizzazione dei file.

    I dati sono presi automaticamente a partire dal file di indicizzazione nella cartella dei dati,
    in base al data_type passato all'interno dell'id.

    Vengono nascoste le colonne vuote e la colonna degli indirizzi. Le celle vuote vengono riempite con "-".
    :param table_id:
    :return:
    """

    data, columns, cols_to_hide = get_table(table_id)

    return dash_table.DataTable(
        id=table_id,
        data=data,
        columns=columns,
        sort_action='native',
        filter_action='native',
        filter_options={"placeholder_text": "Filter column..."},
        row_selectable='multi',
        selected_rows=[],
        hidden_columns=cols_to_hide,
        page_size=10,
        style_cell={
            'textAlign': 'right',
            'padding': '8px 12px',
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '13px',
            'minWidth': '80px',
            'maxWidth': '150px',
            'whiteSpace': 'normal'
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'trap_distr'},
                'textAlign': 'left',
                'minWidth': '120px',
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
            'border': '1px solid #f0f0f0'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(240, 240, 240)',
            }
        ],
        style_header={
            'backgroundColor': 'rgb(100, 100, 100)',
            'color': 'white',
            'fontWeight': 'bold',
            'fontSize': '14px',
            'padding': '12px 15px',
            'textAlign': 'center',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        fixed_rows={'headers': True},
        tooltip_data=[],
        tooltip_duration=None,
        style_table={
            'minWidth': '100%',
            'overflowX': 'auto'
        }
    )

def grouping_selector(selector_id:dict[str,str]):
    """
    Crea un DropDown menu e una lista di scelta.

    Il primo serve per selezionare la feature secondo cui raggruppare tra quelle possibili;
    La seconda per decidere se visualizzare la tabella secondo i raggruppamenti o esplosa.
    """
    try:
        page = selector_id['page']
    except KeyError:
        raise KeyError("Valore di pagina non specificato nell'id")

    type_configs = load_files_info()[page]

    try:
        data = pd.read_excel(indexes_file, sheet_name=page)
    except Exception:
        raise FileNotFoundError(
            f"""Non è stato possibile trovare il file di indicizzazione necessario
            data_type specificato = {page}"""
        )

    features = type_configs["AllowedFeatures"].keys()

    # nasconderò le colonne vuote e la colonna dei file_path
    f_to_pop = data.columns[data.isna().all()].tolist()
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
                )
            ),
            dbc.Col(
                dcc.Dropdown(
                    options=features,
                    value="Vgf" if "Vgf" in features else features[0],
                    id=menu_id,
                )
            )
        ])
    ])

    return None

def custom_spinner(message:str=""):
    if not message:
        return dbc.Spinner(color="primary", size='md', spinner_class_name="ms-3")
    return html.H1([message, dbc.Spinner(color="primary", size='md', spinner_class_name="ms-3")])

def export_modal(modal_id:dict[str,str])->dbc.Modal:
    """Crea una finestra pop-up in cui selezionare le curve da esportare e i parametri di esportazione"""
    try:
        page = modal_id['page']
    except KeyError:
        raise KeyError("Valore di pagina non specificato nell'id")

    type_configs = load_files_info()[page]

    curves_checklist_opt = [
        {
            "value":acronym,
            "label":label
        } for acronym,label in type_configs["AllowedCurves"].items()
    ]

    return dbc.Modal([

        dbc.ModalHeader(dbc.ModalTitle("🖨️ Esportazione Grafici")),

        dbc.ModalBody(
            dcc.Loading(
                id={'page': page, 'item': 'modal-loading'},
                custom_spinner=custom_spinner("Esportando!"),
                overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                delay_show=500,
                style={"height": "100%", "overflow": "auto"},
                children=[
                    dbc.Container([
                        dcc.Store(id={'page': page, 'item': 'store-loading-placeholder', 'location': 'modal'},
                                  data=None),

                        # Riga 1: Tabella e selezione impostazioni esportazione
                        dbc.Row([
                            # Colonna con tabella, mode selector
                            dbc.Col([
                                grouping_selector({'page':page, 'item':'radio-mode-toggle', 'location':'modal'}),
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
                                                {"label": "Grafico a Colori", "value": "colors"}
                                            ],
                                            value=["colors"],
                                            switch=True,
                                            style={"margin-bottom": "15px", 'display': 'none' if page=='TrapData' else 'inline-block'}
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
                                                    id={'page':page, 'item':'selector-format', 'location':'modal'},
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


## HELPER FUNC ##
def get_table(table_id:dict[str,str], only_df=False):
    """
    Ritorna i dati per costruire la DataTable specificata dall'id nella visualizzazione normal.
    I valori nulli sono riempiti con "-".

    :param table_id: id della tabella di cui sono richiesti i valori.
    :param only_df: default False. Se True la funzione ritorna solo il df letto in memoria.
    :return: In ordine data, il df della tabella, columns, ossia il dizionario con le informazioni di colonna
     da passare a dash, e cols_to_hide, la lista delle colonne da nascondere.
    """
    try:
        page = table_id['page']
    except KeyError:
        raise KeyError("Valore di pagina non specificato nell'id")

    type_configs = load_files_info()[page]
    aff_cols = type_configs["TargetCurves"]==1

    # page è anche il nome del data_type dei file da visualizzare
    try:
        data = pd.read_excel(indexes_file, sheet_name=page)
        if only_df:
            return data
    except Exception:
        raise FileNotFoundError(
            f"""Non è stato possibile trovare il file di indicizzazione necessario
            data_type specificato = {page}"""
        )

    columns = [
        {"name":f_name,
         "id":f_name,
         "type":"numeric" if f_type in ("integer", "float") else None}
        for f_name,f_type in type_configs["AllowedFeatures"].items()
    ]
    aff_cols_ids = []
    if aff_cols:
        for curve_id,curve_label in type_configs["TargetCurves"].items():
            columns.append({
                "name":f"Aff {curve_label}",
                "id":f"aff_{curve_id}",
                "type":"numeric",
                "format":dash_table.FormatTemplate.percentage(2)
            })
            aff_cols_ids.append(f"aff_{curve_id}")

    # nasconderò le colonne vuote e la colonna dei file_path
    cols_to_hide = ["file_path", *data.columns[data.isna().all()].tolist()]
    if aff_cols_ids:
        cols_to_hide.append(*aff_cols_ids)

    # riempio le celle vuote con un trattino placeholder
    data.fillna("-")

    return data, columns, cols_to_hide