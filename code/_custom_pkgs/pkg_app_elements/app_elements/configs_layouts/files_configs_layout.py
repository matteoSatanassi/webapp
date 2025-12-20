"""Il modulo contiene il layout del tab Files Configs"""

from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.P("Modifica la struttura AllowedFeatures e AllowedCurves per ogni tecnologia.",
                               className="text-muted mt-3"),

    html.Div(id="container-files-configs"), # Popolato dalla callback

    dbc.Button("➕ Aggiungi Nuovo File Type", id="btn-add-file-type",
               color="primary", className="mt-3")
])