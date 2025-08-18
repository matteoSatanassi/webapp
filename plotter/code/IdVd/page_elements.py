from dash import  dcc, dash_table, html
import dash_bootstrap_components as dbc
from .parameters import exp_mode_dict

## PAGE ELEMENTS ##
def my_table_template(table_id:str)->dash_table.DataTable:
    return dash_table.DataTable(
        id=table_id,
        data=exp_mode_dict,
        columns=[
            {'name': 'Trap Distribution', 'id': 'trap_distr'},
            {'name': 'E_mid', 'id': 'e_mid'},
            {'name': 'E_σ', 'id': 'e_sigma'},
            {'name': 'V_gf', 'id': 'v_gf'},
            {'name': 'file_path', 'id': 'file_path'},
            {'name': 'group', 'id': 'group'},
        ],
        sort_action='native',
        filter_action='native',
        filter_options={"placeholder_text": "Filter column..."},
        row_selectable='multi',
        selected_rows=[],
        hidden_columns=['file_path', 'group'],
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
            'fontWeight': 'bold'
        },
        css=[{"selector": ".show-hide", "rule": "display: none"}]
    )

def mode_options(radio_id:str)->dcc.RadioItems:
    return dcc.RadioItems(
        options=['Group mode','Exp mode'],
        value='Exp mode',
        id=radio_id,
        inline=True,
    )

def curves_options(checklist_id:str)->dcc.Checklist:
    return dcc.Checklist(
        id=checklist_id,
        options=[
            {'label': '(0,0)', 'value': 'v0'},
            {'label': '(-7,0)', 'value': '0'},
            {'label': '(-7,15)', 'value': '15'},
            {'label': '(-7,30)', 'value': '30'},
        ],
        value=['v0','0','15','30'],  # all’inizio tutte selezionate
        labelStyle={'display': 'inline-block'},
    )

export_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Export")),
        dbc.ModalBody(
            dbc.Row([
                dbc.Col(my_table_template('export-table')),
                dbc.Col(
                    [
                        html.Div(mode_options('export-mode-toggle')),
                        html.Div(curves_options('export-curves'))
                    ]
                )
            ])
        ),
        dbc.ModalFooter(
            [
                dbc.Button("Close", id="close-button", className="ms-auto", n_clicks=0),
                dbc.Button("Export Selected", id="export-button", className="ms-auto", n_clicks=0)
            ]
        ),
    ],
    id="modal-export",
    is_open=False,
)