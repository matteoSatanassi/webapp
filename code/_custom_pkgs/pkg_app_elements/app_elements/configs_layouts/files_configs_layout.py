"""Il modulo contiene il layout del tab Files Configs"""

from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    dcc.Store(id={"config-tab":"files-configs", "item":"initial-config-loaded"}, data=False),

    html.P("Aggiungi e modifica le strutture dei file letti dall'applicazione.",
                               className="text-muted mt-3"),

    html.Div(id={"config-tab":"files-configs", "item":"configs-container"}), # Popolato dalla callback

    dbc.Button("➕ Aggiungi Nuovo File Type", id="btn-add-file-type",
               color="primary", className="mt-3")
])