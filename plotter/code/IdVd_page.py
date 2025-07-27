from dash import Dash, html, dcc, Input, Output, callback, dash_table, State
import dash_bootstrap_components as dbc
from Common import *

## PARAMS ##
index_table_csv = Path('../IdVd_data/index_table.csv')
df = pd.read_csv(index_table_csv)
exp_mode_dict = df.to_dict('records')

## DERIVED PARAMS ##
groups_first_only:dict={
    'groups':[],
    'indexes':[]
}
for i in range(len(df)):
    row = exp_mode_dict[i]
    if row['group'] in groups_first_only['groups']:
        pass
    else:
        groups_first_only['groups'].append(row['group'])
        groups_first_only['indexes'].append(i)
group_mode_dict = df.iloc[groups_first_only['indexes']].to_dict('records')

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
            children=[          #ogni riga ha dimensione 12 orizzontalmente
                dbc.Col(
                    children=[
                        dcc.RadioItems(
                            options=['Group mode','Exp mode'],
                            value='Exp mode',
                            id='group-mode-toggle',
                            inline=True,
                        ),
                        # html.Div(id='table')
                        dash_table.DataTable(
                                    id='table',
                                    data=exp_mode_dict,
                                    columns=[
                                        {'name': 'Trap Distribution', 'id': 'trap_distr'},
                                        {'name': "E_mid", 'id': 'e_mid'},
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
                                    }
                                )
                    ],
                    width=4,    #larghezza colonna
                    style={'textAlign': 'center'},
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
                        # checklist curve visualizzate
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
    Input('plot-button', 'n_clicks'),           #n_clicks (plot button)
    State('group-mode-toggle', 'value'),        #curr_mode: modo corrente della tabella (Exp/Group)
    State('table','derived_virtual_selected_rows'), #selected_rows: indici delle righe selezionate (considerati filtri vari colonne)
    State('table','derived_virtual_data'),      #table_data: dati della tabella (considerati filtri vari colonne)
    State('tabs','value'),                      #curr_tab: tab attualmente aperto (se nessuno None)
    State('tabs','children')                    #tabs: lista dei tab disponibili
)
def update_tabs(n_clicks, curr_mode, selected_rows, table_data, curr_tab, tabs):
    labels = {'exponential':'exp', 'gaussian':'gauss', 'uniform':'unif'}
    tabs = tabs or []
    if not n_clicks or not selected_rows:
        return tabs,[],curr_tab

    open_tabs = [tab['props']['value'] for tab in tabs]

    for selected_index in selected_rows:
        # row = table_data[selected_index]
        if curr_mode == 'Exp mode':
            file = table_data[selected_index]['file_path']
            if file not in open_tabs:
                tabs.append(
                    dcc.Tab(
                        label=f"Exp - {labels[row['trap_distr']]}/{row['e_mid']}/{row['e_sigma']}/{row['v_gf']}",
                        value=file
                    )
                )
        else:
            group = row['group']
            if group not in open_tabs:
                tabs.append(
                    dcc.Tab(
                        label=f"Group - {labels[row['trap_distr']]}/{row['e_mid']}/{row['e_sigma']}",
                        value=group
                    )
                )


    if not open_tabs:
        if curr_mode == 'Exp mode':
            return tabs,[],table_data[selected_rows[0]]['file_path']    # se non c'è alcun tab già aperto, apro il primo tab
        else:
            return tabs,[],table_data[selected_rows[0]]['group']
    else:
        return tabs,[],curr_tab     # altrimenti lascio aperto il tab già selezionato

# aggiorna il grafico in base al tab e alle curve selezionati da visualizzare
@callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    Input('curve-checklist', 'value')
)
def update_graph_content(tab, checked):
    if not tab:
        return "nulla di selezionato"
    if '.csv' not in tab:
        df_group = df.loc[df['group']==tab]
        g = Group()
        for file in df_group['file_path']:
            g.add_path(Path(file))
        return str(vars(g))
    else:
        exp = Exp(Path(tab))
        exp.fill()
        plot = ExpPlot(exp)
        plot.plot(checked)
        return dcc.Graph(figure=plot.fig)

# aggiorna la tabella in base alla modalità selezionata
@callback(
    Output('table', 'data'),
    Output('table', 'hidden_columns'),
    Input('group-mode-toggle', 'value')
)
def update_table(mode):
    if mode == 'Exp mode':
        return exp_mode_dict,['file_path', 'group']
    else:
        return group_mode_dict,['file_path', 'group', 'v_gf']

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)