from dash import Dash, html, page_registry, page_container, callback, Input
import dash_bootstrap_components as dbc
from common import indexer
from app_elements import *

## PARAMS ##
CURRENT_THEME = load_configs()["theme"]

## FUNC ##
def configure_app():
    global CURRENT_THEME
    return Dash(
        __name__,
        assets_folder='assets',
        external_stylesheets=[getattr(dbc.themes, load_configs()["theme"])],
        use_pages=True,
        # suppress_callback_exceptions=True
    )

indexer(data_dir)

app = configure_app()

## LAYOUT ##
app.layout = dbc.Container(
    children=[
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
            ],
            brand='IdVd',
            brand_href='/IdVd-plotter',
        ),
        page_container
    ],
    fluid=True,
)

@callback([], Input("config-status-message", "children"),)
def config_status_message(status):
    if status in ("Impostazioni salvate!", "Impostazioni resettate!"):
        global app, CURRENT_THEME
        if CURRENT_THEME != load_configs()["theme"]:
            app = configure_app()
            return app
    return None

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)