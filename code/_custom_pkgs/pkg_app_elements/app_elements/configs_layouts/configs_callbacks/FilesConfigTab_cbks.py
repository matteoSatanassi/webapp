"""Il modulo contiene le callback che agiscono sul tab di configurazione dei file"""

import json
from dash import html, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import dash_ace
from app_resources.AppCache import GLOBAL_CACHE


## HELPER FUNCS ##
def render_file_config_editor(f_type, content):
    """
    Esempio di una sezione per un singolo file_type (es. IDVD)
    """
    return dbc.AccordionItem([
        # --- HEADER INTERNO: Titolo e Modifica Nome ---
        dbc.Row([
            dbc.Col([
                html.H5(f"Configurazione per: {f_type}", className="mb-0"),
                html.Small("Modifica il nome del File Type se necessario", className="text-muted")
            ], width=8),
            dbc.Col([
                dbc.InputGroup([
                    dbc.Input(id={'type': 'rename-input', 'index': f_type}, placeholder="Nuovo nome..."),
                    dbc.Button("Rinomina", id={'type': 'rename-btn', 'index': f_type}, color="outline-secondary"),
                ], size="sm")
            ], width=4),
        ], className="align-items-center mb-3"),

        html.Hr(),

        # --- TEXT EDITOR: JSON Area ---
        dbc.Label("Editor JSON (Sintassi Raw):", className="fw-bold"),

        dash_ace.DashAceEditor(
            id={'type': 'advanced-json-edit', 'f_type': f_type, 'cfg': "file"},
            value=json.dumps(content, indent=4),
            mode='json',  # Attiva l'evidenziazione JSON
            theme='github',  # Tema scuro (o 'github' per chiaro)
            tabSize=4,  # Il tasto Tab funzionerà come previsto
            width='100%',
            height='400px',
            showGutter=True,  # Mostra i numeri di riga
            showPrintMargin=False,
            fontSize=14,
            setOptions={
                'useSoftTabs': True,  # Converte il tab in spazi
                'enableBasicAutocompletion': True,
                'enableLiveAutocompletion': True,
                'showLineNumbers': True,
            }
        ),

        # --- FOOTER INTERNO: Feedback e Azioni ---
        html.Div(id={'type': 'json-feedback', 'f_type': f_type, 'cfg': 'files'}),

        dbc.Row([
            dbc.Col(
                dbc.Button("🗑️ Elimina File Type",
                           id={'type': 'delete-f-type', 'index': f_type},
                           color="danger",
                           size="sm",
                           outline=True),
                width="auto"
            )
        ], justify="end", className="mt-2")

    ], title=f"📂 {f_type}", item_id=f"acc-{f_type}")


## CALLBACKS ##
@callback(
    [Output({"config-tab":"files-configs", "item":"initial-config-loaded"}, 'data'),
     Output({"config-tab":"files-configs", "item":"configs-container"}, 'children')],
    Input({"config-tab":"files-configs", "item":"initial-config-loaded"}, 'data')
)
def initialize_configs_values(trigger):
    if not trigger:
        return no_update

    pass
