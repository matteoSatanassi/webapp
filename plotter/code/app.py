from dash import Dash, html, page_registry, page_container
from app_elements import *
from plotter.code.app_elements.callback_functions import *

indexer(data_dir)
app = Dash(
    __name__,
    assets_folder='assets',
    external_stylesheets=[getattr(dbc.themes, load_configs()["theme"])],
    use_pages=True,
    # suppress_callback_exceptions=True
)

## LAYOUT ##
app.layout = dbc.Container([
    html.H1('Multi-page app with Dash Pages'),
    dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                children=[
                dbc.DropdownMenuItem(f'{page['name']}', href=page['relative_path']) for page in page_registry.values()
                ],
                nav=True,
                in_navbar=True
            ),
        ]
    ),
    page_container
],
    fluid=True,
)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)