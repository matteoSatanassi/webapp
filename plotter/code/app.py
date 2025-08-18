from dash import Dash, Input, Output, callback, State, html, dcc
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
        html.Div([
            html.Div(
                dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
            ) for page in dash.page_registry.values()
        ]),
        dash.page_container
    ]
)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)