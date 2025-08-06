from dash import Dash, Input, Output, callback, State
from definitions import *

app = Dash(
    __name__,
    assets_folder='assets',
    external_stylesheets=[dbc.themes.SUPERHERO]
)

## LAYOUT ##
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
            children=[          #ogni riga ha dimensione 12 orizzontalmente
                dbc.Col(
                    children=[
                        mode_options('group-mode-toggle'),
                        my_table('table')
                    ],
                    width=4,    #larghezza colonna
                    style={'textAlign': 'center'},
                ),  #ELENCO FILE
                dbc.Col(
                    html.Div(
                        children=[
                            dbc.Button("Plot ->", id="plot-button", className="me-15", color="primary"),
                            dbc.Button("Export!", id='export-button', className="me-15", color="primary"),
                            # export_modal
                        ],
                        style={"textAlign": "center"}
                    ),
                    className="d-flex justify-content-center",
                    width=1     #larghezza colonna
                ),  #BOTTONI
                dbc.Col(
                    children=[
                        dcc.Tabs(id="tabs", value=None),
                        html.Div(id="tabs-content"),
                        curves_options('curve-checklist')   # checklist curve visualizzate
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

## CALLBACKS ##
 #aggiorna la lista dei tab al click del bottone, in base agli esperimenti selezionati nella tabella
callback(
    [
        Output('tabs', 'children'),
        Output('table','selected_rows'),
        Output('tabs', 'value')
    ],  #output
    [
        Input('plot-button', 'n_clicks')    #n_clicks (plot button)
    ],  #input
    [
        State('group-mode-toggle', 'value'),        #curr_mode: modo corrente della tabella (Exp/Group)
        State('table','derived_virtual_selected_rows'), #selected_rows: indici delle righe selezionate (considerati filtri vari colonne)
        State('table','derived_virtual_data'),      #table_data: dati della tabella (considerati filtri vari colonne)
        State('tabs','value'),                      #curr_tab: tab attualmente aperto (se nessuno None)
        State('tabs','children'),                   #tabs: lista dei tab disponibili
     ]  #states
)(update_tabs)
 # aggiorna il grafico in base al tab e alle curve selezionati da visualizzare
callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    Input('curve-checklist', 'value')
)(update_graph_content)
# aggiorna la tabella in base alla modalità selezionata
callback(
    Output('table', 'data'),
    Output('table', 'hidden_columns'),
    Output('table', 'selected_rows',allow_duplicate=True),
    Input('group-mode-toggle', 'value'),
    prevent_initial_call=True
)(update_table)
#esporta righe selezionate in tabella
callback(
    Output('table', 'selected_rows', allow_duplicate=True),
    Input('export-button', 'n_clicks'),
    [
        State('group-mode-toggle', 'value'),
        State('table', 'derived_virtual_selected_rows'),
        State('table', 'derived_virtual_data')
     ],
    prevent_initial_call=True
)(export_selected)
# @app.callback(
#     Output('modal', 'is_open'),
#     Input('modal-show', 'n_clicks'),
#     State('modal', 'is_open'),
# )
# def toggle_modal(n_clicks, is_open):
#     if not n_clicks:
#         return is_open
#     return not is_open

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)