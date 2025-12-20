"""Il modulo contiene il layout del tab Plotter Configs"""

from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.P("Configura colori, stili linea e titoli degli assi.",
           className="text-muted mt-3"),

    html.Div(id="container-plotter-configs"), # Popolato dalla callback
])