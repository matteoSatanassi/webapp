from dash import Dash, html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly_express as px
from Common import *

## PARAMS ##
index_table_csv = Path('../IdVd_data/index_table.csv')
df = pd.read_csv(index_table_csv)

app = Dash(
    __name__,
    assets_folder='assets',
    external_stylesheets=[dbc.themes.SUPERHERO]
)

app.layout = dbc.Container(
    children=[
        dbc.Row(
            dbc.Col(
                children=html.H1('IdVd Plotter'),
                style={'textAlign': 'center'}
            ),
            style={'height':'12vh'}
        ),  #TITOLO
        dbc.Row(
            children=[          #ogni colonna ha dimensione 12
                dbc.Col(
                    # children=html.P('Elenco'),
                    # style={'textAlign': 'center', 'border': '1px solid white'},
                    # width=4
                    children=dash_table.DataTable(
                        id='table',
                        data=df.to_dict('records'),
                        columns=[
                            {'name':'Trap Distribution', 'id':'trap_distr'},
                            {'name':"E_mid", 'id':'e_mid'},
                            {'name':'E_σ', 'id':'e_sigma'},
                            {'name':'V_gf', 'id':'v_gf'},
                            {'name':'file_path', 'id':'file_path'},
                        ],
                        sort_action='native',
                        filter_action='native',
                        filter_options={"placeholder_text": "Filter column..."},
                        row_selectable='multi',
                        selected_rows=[],
                        hidden_columns=["file_path"],
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
                        }
                    )
                ),  #ELENCO FILE
                dbc.Col(
                    children=html.P('spazio vuoto'),
                    style={'textAlign': 'center', 'border': '1px solid white'},
                    width=1
                ),  #spazio vuoto
                dbc.Col(
                    children=html.P('GRAFICI'),
                    style={'textAlign': 'center', 'border': '1px solid white'},
                    width=7
                ),  #GRAFICI
            ],
            style={'height':'60vh'}
        ),  #GRAFICO+TABELLA
    ],
    fluid=True,
    className='IdVd_dashboard'
)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)