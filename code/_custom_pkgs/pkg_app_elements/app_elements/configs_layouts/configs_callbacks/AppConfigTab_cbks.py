"""
Il modulo contiene tutte le funzioni callback che agiscono
sulla pagina Config dell'applicazione
"""

import time
from pathlib import Path
from dash import Input, Output, State, callback, no_update
from dash_bootstrap_templates import ThemeChangerAIO
import dash_bootstrap_components as dbc
from app_elements.page_elements import custom_spinner
from app_resources.AppCache import GLOBAL_CACHE


## CALLBACKS ##
@callback(
    [Output("config-export-path", "value"),
     Output("config-data-path", "value"),
     Output("config-export-format", "value"),
     Output("config-theme", "value"),
     Output("current-theme", "data"),
     Output(ThemeChangerAIO.ids.radio("theme"), "value"),
     Output("config-legend-colors-checklist", "value"),
     Output("config-DPI-selector", "value"),
     Output({"config-tab":"app-configs", "item":"initial-config-loaded"}, "data")],
    Input({"config-tab":"app-configs", "item":"initial-config-loaded"}, "data"),
)
def initialize_config_values(is_loaded):
    """Inizializza i valori della pagina e non permette ulteriori aggiornamenti"""
    if is_loaded:
        return (no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update)

    configs = GLOBAL_CACHE.app_configs

    checklist_values = []
    if configs.legend:
        checklist_values.append('show_legend')
    if configs.colors:
        checklist_values.append('colors')

    return (
        str(configs.export_dir),
        str(configs.data_dir),
        configs.export_format,
        configs.theme,
        configs.theme,
        getattr(dbc.themes, configs.theme),
        checklist_values,
        configs.dpi,
        True  # Marca come caricato lo store placeholder
    )

@callback(
    [Output("loading-main-configs", "custom_spinner"),
     Output("current-theme", "data", allow_duplicate=True),
     Output(ThemeChangerAIO.ids.radio("theme"), "value", allow_duplicate=True),
     Output("store-trigger-refresh", "data", allow_duplicate=True),],
    Input("save-config-button", "n_clicks"),
    [State("config-data-path", "value"),
     State("config-export-path", "value"),
     State("config-export-format", "value"),
     State("config-theme", "value"),
     State("config-legend-colors-checklist", "value"),
     State("config-DPI-selector", "value")],
    prevent_initial_call=True
)
def save(n_clicks:int, data_path:str, export_path:str, export_format:str,
         theme:str, legend_colors:list, dpi:int):
    """Salva i parametri di configurazione visualizzata nella pagina ConfigPage"""
    if not n_clicks:
        return no_update, no_update, no_update, no_update

    try:
        export_path = Path(export_path)
    except (OSError, ValueError):
        return (custom_spinner("Export path non valido"),
                no_update, no_update, no_update)

    try:
        data_path = Path(data_path)
        if not data_path.exists():
            raise ValueError
    except (OSError, ValueError):
        return (custom_spinner("Data path non valido"),
                no_update, no_update, no_update)

    configs = GLOBAL_CACHE.app_configs

    refresh_flag = False
    if configs.data_dir!=data_path:
        refresh_flag=True

    configs.theme = theme
    configs.data_dir = data_path
    configs.export_dir = export_path
    configs.export_format = export_format
    configs.legend = "show_legend" in legend_colors
    configs.colors = "colors" in legend_colors
    configs.dpi = dpi

    configs.save_all()

    return (custom_spinner("Impostazioni Salvate!"),
            theme, getattr(dbc.themes, theme),
            refresh_flag)

@callback(
    [Output("loading-main-configs", "custom_spinner", allow_duplicate=True),
     Output("current-theme", "data", allow_duplicate=True),
     Output("config-export-path", "value", allow_duplicate=True),
     Output("config-data-path", "value", allow_duplicate=True),
     Output("config-export-format", "value", allow_duplicate=True),
     Output("config-theme", "value", allow_duplicate=True),
     Output("config-legend-colors-checklist", "value", allow_duplicate=True),
     Output("config-DPI-selector", "value", allow_duplicate=True),
     Output("store-trigger-refresh", "data", allow_duplicate=True)],
    Input("reset-config-button", "n_clicks"),
    prevent_initial_call=True
)
def reset(n_clicks):
    if not n_clicks:
        return (no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update)

    configs = GLOBAL_CACHE.app_configs
    data_dir = configs.data_dir
    configs.reset_all()

    refresh_flag = False
    if configs.data_dir!=data_dir:
        refresh_flag = True

    legend_colors = []
    if configs.legend:
        legend_colors.append("show_legend")
    if configs.colors:
        legend_colors.append("colors")

    return (custom_spinner("Impostazioni Resettate!"),
            configs.theme,
            str(configs.export_dir),
            str(configs.data_dir),
            configs.export_format,
            configs.theme,
            legend_colors,
            configs.dpi,
            refresh_flag)


@callback(
    Output(ThemeChangerAIO.ids.radio("theme"), "value", allow_duplicate=True),
    Input("current-theme", "data"),
    prevent_initial_call=True
)
def change_theme(curr_theme):
    """Alla modifica dello store current-theme, modifica il tema dell'applicazione"""
    if not curr_theme:
        return no_update
    time.sleep(1)
    return getattr(dbc.themes, curr_theme)