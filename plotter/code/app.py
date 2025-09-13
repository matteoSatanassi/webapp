from dash import Dash, html
import dash
import dash_bootstrap_components as dbc
from common import indexer
from app_elements import *

indexer(data_dir)

app = Dash(
    __name__,
    assets_folder='assets',
    external_stylesheets=[getattr(dbc.themes,load_configs()['theme'])],
    use_pages=True,
    # suppress_callback_exceptions=True
)

## LAYOUT ##
app.layout = dbc.Container(
    children=[
        html.H1('Multi-page app with Dash Pages'),
        dbc.NavbarSimple(
            children=[
                dbc.DropdownMenu(
                    children=[
                    dbc.DropdownMenuItem(f'{page['name']}', href=page['relative_path']) for page in dash.page_registry.values()
                    ],
                    nav=True,
                    in_navbar=True
                ),
            ],
            brand='IdVd',
            brand_href='/IdVd-plotter',
        ),
        dash.page_container
    ],
    fluid=True,
)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)