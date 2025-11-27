import pandas as pd
from dash import Input, Output, State, callback, MATCH, no_update, callback_context
from app_elements.callback_functions import explode_group_paths
from app_elements.callbacks._helper_funcs import find_export_path, update_table
from common import FileCurves, CustomFigure
from params import *


## DYNAMIC CALLBACKS ##
callback([
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'data'),
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'hidden_columns'),
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows', allow_duplicate=True),
    Input({'page':MATCH, 'item':'radio-table-mode', 'location':'modal'}, 'value'),
    State({'page':MATCH, 'item':'menu-grouping-features', 'location':'modal'}, 'value'),
    State({'page':MATCH, 'item':'table', 'location':'modal'}, 'hidden_columns'),
    State({'page':MATCH, 'item':'table', 'location':'modal'}, 'data'),
    State({'page': MATCH, 'item': 'table', 'location': 'modal'}, 'id')],
    prevent_initial_call=True
)(update_table)

@callback([
    Output({'page': MATCH, 'item': 'modal'}, 'is_open'),
    Input({'page': MATCH, 'item': 'button-open-modal'}, 'n_clicks'),
    Input({'page': MATCH, 'item': 'button-close-modal'}, 'n_clicks'),
    State({'page': MATCH, 'item': 'modal'}, 'is_open'),
])
def open_close_modal(n_clicks_open: int, n_clicks_close: int, is_open: bool):
    """Apre/chiude il pop-up di esportazione nel caso venga premuto il pulsante di export/di chiusura"""
    ctx = callback_context
    if not ctx.triggered:
        return is_open

    triggered_id = ctx.triggered_id
    if triggered_id != '.':
        if 'modal' in triggered_id['item']:
            if 'open' in triggered_id['item']:
                return True
            elif 'close' in triggered_id['item']:
                return False

    return is_open


@callback([
    Output({'page':MATCH, 'item':'check-legend', 'location':'modal'}, 'value'),
    Output({'page':MATCH, 'item':'check-colors', 'location':'modal'}, 'value'),
    Output({'page':MATCH, 'item':'selector-dpi', 'location':'modal'}, 'value'),
    Output({'page':MATCH, 'item':'selector-format', 'location':'modal'}, 'value'),
    Input({'page':MATCH, 'item': 'modal'}, 'is_open'),
])
def initialize_values(is_open:bool):
    """All'apertura del modal inizializza i valori dei vari oggetti in base alle impostazioni salvate nei config"""
    if not is_open:
        return no_update, no_update, no_update, no_update
    config = load_configs()
    return (['show_legend'] if bool(config['legend']) else [],
            ['colors'] if bool(config['colors']) else [],
            int(config['DPI']),
            config['export_format'])


@callback([
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows', allow_duplicate=True),
    Input({'page':MATCH, 'item':'modal'}, 'is_open'),
    State({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows')],
    prevent_initial_call=True
)
def unselect_rows_modal(is_open:bool, selected_rows:list[int]):
    """Deseleziona le righe quando viene chiuso il pop-up"""
    if not is_open:
        return []
    return selected_rows


@callback([
    Output({'page':MATCH, 'item':'button-export'}, "disabled"),
    Input({'page':MATCH, 'item':'table', 'location':'modal'}, "derived_virtual_selected_rows"),],
    prevent_initial_call=True
)
def enable_export_button(selected_rows:list[int]):
    """Attiva il pulsante di esportazione alla selezione di almeno un esperimento/gruppo"""
    if not selected_rows:
        return True
    return False


@callback([
    Output({'page': MATCH, 'item': 'modal'}, 'is_open', allow_duplicate=True),
    Input({'page': MATCH, 'item': 'button-export'}, 'n_clicks'),
    State({'page': MATCH, 'item': 'table', 'location': 'modal'}, 'derived_virtual_selected_rows'),
    State({'page': MATCH, 'item': 'table', 'location': 'modal'}, 'derived_virtual_data'),
    State({'page': MATCH, 'item': 'radio-table-mode', 'location': 'modal'}, 'value'),
    State({'page': MATCH, 'item': 'menu-grouping-features', 'location': 'modal'}, 'value'),
    State({'page': MATCH, 'item': 'checklist-curves', 'location': 'modal'}, 'value'),
    State({'page': MATCH, 'item': 'check-legend', 'location': 'modal'}, 'value'),
    State({'page': MATCH, 'item': 'check-colors', 'location': 'modal'}, 'value'),
    State({'page': MATCH, 'item': 'selector-dpi', 'location': 'modal'}, 'value'),
    State({'page': MATCH, 'item': 'selector-format', 'location': 'modal'}, 'value')],
    prevent_initial_call=True
)
def export_selected(n_clicks:int, selected_rows:list[int],table_data:list[dict], mode:str, grouping_feature:str,
                    selected_curves:list[str], legend:list, colors:list, dpi_img:int, file_format:str):
    """Esporta le righe selezionate nella tabella del pop-up, premuto il bottone di export, e a fino processo chiude il pop-up"""
    if not n_clicks or not selected_rows:
        return no_update

    export_path = find_export_path()

    if mode == "grouped":
        figs:list[CustomFigure] = []
        for selected_index in selected_rows:
            row = table_data[selected_index]

            path_list = explode_group_paths(row['file_path'])
            figs.append(
                CustomFigure(
                    FileCurves.from_paths(*path_list,
                                          grouping_feature=grouping_feature if len(path_list) > 1 else None
                                          ),
                    curves_to_plot= selected_curves,
                    plot_all_curves=False,
                    legend=legend,
                    colored=colors,
                ).plot_group()
            )
        file_paths = [export_path/f"{fig.get_group_stem}.{file_format}" for fig in figs]
    if mode == "normal":
        figs:list[CustomFigure] = CustomFigure(
            FileCurves.from_df(pd.DataFrame(table_data)),
            curves_to_plot=selected_curves,
            plot_all_curves=False,
            legend=legend,
            colored=colors,
        ).plot_all()    # con questo metodo creo una lista di CustomFigures, ognuna con i dati di un solo file all'interno
        file_paths = [export_path/f"{f.get_paths.stem}.{file_format}" for f in figs]
    else:
        raise ValueError(f"La modalità {mode} non è supportata dall'applicazione")

    try:
        import plotly.io as pio

        pio.write_images(fig=figs, file=file_paths, format=file_format, scale=dpi_img/72)
        return False

    except Exception:
        return no_update

