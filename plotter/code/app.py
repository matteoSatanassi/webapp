from dash import Dash, html
import dash
from pathlib import Path
import dash_bootstrap_components as dbc
from common import indexer

indexer(Path('../data'))

app = Dash(
    __name__,
    assets_folder='assets',
    external_stylesheets=[dbc.themes.SUPERHERO],
    use_pages=True
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
    ]
)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)