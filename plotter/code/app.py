from dash import Dash, page_container,html
from app_elements.callback_functions import *

indexer(data_dir)   # indexing data files at the start
affinities_updater(indexes_file, affinity_file)  # updating affinities table

app = Dash(
    __name__,
    assets_folder='assets',
    external_stylesheets=[getattr(dbc.themes, load_configs()["theme"])],
    use_pages=True,
    # suppress_callback_exceptions=True
)

## LAYOUT ##
nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink(html.Div(["I",html.Sub("D"),"-V",html.Sub("D")," Plotter"]), href="/", active='exact',
                                id={'item':'nav-link', 'link':'IdVd'})),
        dbc.NavItem(dbc.NavLink('Traps data Plotter', href='/TrapData-plotter', active='exact',
                                id={'item':'nav-link', 'link':'Traps'})),
        dbc.NavItem(dbc.NavLink('Config Page', href='/configs', active='exact',
                                id={'item':'nav-link', 'link':'configs'})),
    ],
    pills=True,
)

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),

    dbc.Row(
        dbc.Col([
            dbc.Card(
                dbc.CardBody(nav, className="d-flex justify-content-center"),
                className="border-0 shadow-sm bg-dark mt-2 mb-2",
            )
        ], width=12),
    ),

    page_container
],
    fluid=True,
    style={'backgroundColor': 'var(--bs-body-bg)', 'minHeight': '100vh'}
)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)