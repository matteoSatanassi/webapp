from dash import register_page, html
import dash_bootstrap_components as dbc

register_page(__name__, path='/', title='Home')

layout = dbc.Container(
    # 1. Contenitore principale (100% altezza viewport e sfondo puntinato)
    html.Div(
        html.H1(
            "My Plotter",
            style={
                'fontSize': '8em',
                'fontFamily': 'serif',
                'fontWeight': '900',
                'margin': '0',
            },
            id='h1-home'
        ),
        style={
            # Stili per centrare l'intero Rettangolo
            'display': 'flex',
            'justifyContent': 'center', # Centratura verticale
            'alignItems': 'center',     # Centratura orizzontale
            'minHeight': '80vh',
            'width': '100%',
        },
        className="d-flex flex-column",
    ),
    fluid=True,
    className="p-0"
)