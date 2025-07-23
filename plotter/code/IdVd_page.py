from dash import Dash, html, dcc, Input, Output, callback, dash_table, State
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
                    ),
                    width=4     #larghezza colonna
                ),  #ELENCO FILE
                dbc.Col(
                    # children=html.P('spazio vuoto'),
                    html.Div(
                        children=[dbc.Button("Plot ->", id="plot-button", color="primary")],
                        style={"textAlign": "center"}
                    ),
                    className="d-flex justify-content-center",
                    width=1     #larghezza colonna
                ),  #spazio vuoto
                dbc.Col(
                    children=[
                        dcc.Tabs(id="tabs", value=None),
                        html.Div(id="tabs-content"),
                        dcc.Checklist(
                            id='curve-checklist',
                            options=[
                                {'label': '(0,0)', 'value': 'v0'},
                                {'label': '(-7,0)', 'value': '0'},
                                {'label': '(-7,15)', 'value': '15'},
                                {'label': '(-7,30)', 'value': '30'},
                            ],
                            value=['v0','0','15','30'],  # all’inizio tutte selezionate
                            labelStyle={'display': 'inline-block'}
                        )
                    ],
                    style={'textAlign': 'center'},
                    width=7     #larghezza colonna
                ),  #GRAFICI e checklist
            ],
            align="center",
            style={'height':'60vh'}
        ),  #GRAFICO+TABELLA
    ],
    fluid=True,
    className='IdVd_dashboard'
)

#aggiorna la lista dei tab al click del bottone, in base agli esperimenti selezionati nella tabella
@callback(
    Output('tabs', 'children'),
    Output('table','selected_rows'),
    Output('tabs', 'value'),
    Input('plot-button', 'n_clicks'),
    State('table','derived_virtual_selected_rows'),
    State('table','derived_virtual_data'),
    State('tabs','value'),
    State('tabs','children')
)
def update_tabs(n_clicks, selected_rows, table_data, curr_tab, tabs):
    labels = {'exponential':'exp', 'gaussian':'gauss', 'uniform':'unif'}
    tabs = tabs or []
    if not n_clicks or not selected_rows:
        return tabs,[],curr_tab

    open_tabs = [tab['props']['value'] for tab in tabs]
    first_new_tab_value = None

    for i in selected_rows:
        row = table_data[i]
        file = row['file_path']
        if file not in open_tabs:
            tabs.append(
                dcc.Tab(
                    label=f"{labels[row['trap_distr']]}/{row['e_mid']}/{row['e_sigma']}/{row['v_gf']}",
                    value=file
                )
            )
            if first_new_tab_value is None:
                first_new_tab_value = file  # salva il primo tab aggiunto

    if not open_tabs:
        return tabs,[],first_new_tab_value
    else:
        return tabs,[],curr_tab

@callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    Input('curve-checklist', 'value')
)
def update_graph_content(tab, checked):
    if not tab:
        return "nulla di selezionato"
    exp = Exp(Path(tab))
    exp.fill()
    plot = ExpPlots(exp)
    plot.plot(checked)
    return dcc.Graph(figure=plot.fig)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)