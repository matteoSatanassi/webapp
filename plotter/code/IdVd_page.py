from dash import Dash, html, dcc, Input, Output, callback, dash_table
import pandas as pd
import dash_bootstrap_components as dbc
import plotly_express as px

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
            children=[          #ogni colonna ha dimensione 12
                dbc.Col(
                    children=html.P('Elenco'),
                    style={'textAlign': 'center', 'border': '1px solid white'},
                    width=4
                ),  #ELENCO FILE
                dbc.Col(
                    children=html.P('spazio vuoto'),
                    style={'textAlign': 'center', 'border': '1px solid white'},
                    width=1
                ),  #spazio vuoto
                dbc.Col(
                    children=html.P('GRAFICI'),
                    style={'textAlign': 'center', 'border': '1px solid white'},
                    width=7
                ),  #GRAFICI
            ],
            style={'height':'60vh'}
        ),  #GRAFICO+TABELLA
    ],
    fluid=True,
    className='IdVd_dashboard'
)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)