from dash import Dash, page_container
from app_elements.page_elements import custom_spinner
from app_elements.builders import *
from app_elements.callback_functions import *
from app_resources.AppCache import GLOBAL_CACHE

app = Dash(
    __name__,
    assets_folder='_assets',
    external_stylesheets=[getattr(dbc.themes, GLOBAL_CACHE.app_configs.theme)],
    use_pages=True,
    pages_folder='_pages'
    # suppress_callback_exceptions=True
)

# creo le pagine per ogni file_type
for file_type in GLOBAL_CACHE.file_types:
    page_builder(file_type)

stores_flag_cache_refreshed = [
    dcc.Store(id={'page':ft, 'item':'store-flag-refreshed-cache'}, data=False)
    for ft in GLOBAL_CACHE.file_types
]

## LAYOUT ##
nav = nav_builder()

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),

    dcc.Store(id='store-trigger-refresh',
              data=False),

    dcc.Store(id='store-trigger-update',
              data=False),

    *stores_flag_cache_refreshed,

    dcc.Loading(
        custom_spinner=custom_spinner("Refresh "),
        overlay_style={"visibility": "visible", "filter": "blur(2px)"},
        delay_show=1000,
        style={"height": "100%", "overflow": "auto"},
        children=[
            dbc.Row(
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(nav, id="nav-holder", className="d-flex justify-content-center"),
                        className="border-0 shadow-sm bg-dark mt-2 mb-2",
                    )
                ], width=12),
            ),

            page_container
        ],
    ),
],
    id="container-app",
    fluid=True,
    style={'backgroundColor': 'var(--bs-body-bg)', 'minHeight': '100vh'}
)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)