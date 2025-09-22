import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from plotter.code.app_elements import *

# dash.register_page(__name__, path='/TrapData-plotter')
#
# ## PARAMS ##
# PAGE_PREFIX = 'TrapData'
#
# ## LAYOUT ##
# layout = dbc.Container([
#         dbc.Row([          #ogni riga ha dimensione 12 orizzontalmente
#             dbc.Col(
#                 my_table_template(f'{PAGE_PREFIX}-table','TrapData'),
#                 width=4,    #larghezza colonna
#                 style={'textAlign': 'center'},
#             ),  #ELENCO FILE
#             dbc.Col(
#                 html.Div(
#                     children=[
#                         dbc.Button("Plot ->", id=f'{PAGE_PREFIX}-plot-button', className="me-15", color="primary"),
#                         dbc.Button("Export!", id=f'{PAGE_PREFIX}-open-modal-button', className="me-15", color="primary"),
#                         export_modal(f'{PAGE_PREFIX}-modal','TrapData')
#                     ],
#                     style={"textAlign": "center"}
#                 ),
#                 className="d-flex justify-content-center",
#                 width=1     #larghezza colonna
#             ),  #BOTTONI
#             dbc.Col(
#                 children=[
#                     dcc.Tabs(id=f"{PAGE_PREFIX}-tabs", value=None),
#                     html.Div(id=f"{PAGE_PREFIX}-tabs-content"),
#                 ],
#                 style={'textAlign': 'center'},
#                 width=7     #larghezza colonna
#             ),  #GRAFICI e checklist
#         ],
#         align="center",
#         style={'height':'60vh', 'margin-top':'5vh'}
#     ),  #GRAFICO+TABELLA
# ],
#     fluid=True,
#     className='TrapDistr_dashboard'
# )
#
# ## CALLBACKS ##
# trapdata_cbs = _register_all_callbacks('TrapData')