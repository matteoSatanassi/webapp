"""
Il modulo contiene tutte le funzioni callback che agiscono sugli elementi dei modal,
all'interno dell'applicazione
"""

import pandas as pd
from dash import Input, Output, State, callback, MATCH, no_update, callback_context
from app_elements.callbacks._helper_funcs import update_table
from common import FileCurves, CustomFigure
from app_resources.AppCache import GLOBAL_CACHE


## DYNAMIC CALLBACKS ##
callback([
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'data'),
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'hidden_columns'),
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows', allow_duplicate=True),
    Input({'page':MATCH, 'item':'radio-table-mode', 'location':'modal'}, 'value'),
    State({'page':MATCH, 'item':'menu-grouping-features', 'location':'modal'}, 'value'),
    State({'page': MATCH, 'item': 'table', 'location': 'modal'}, 'id')],
    prevent_initial_call=True
)(update_table)

@callback(
    Output({'page': MATCH, 'item': 'modal'}, 'is_open'),
    Input({'page': MATCH, 'item': 'button-open-modal'}, 'n_clicks'),
    Input({'page': MATCH, 'item': 'button-close-modal'}, 'n_clicks'),
    State({'page': MATCH, 'item': 'modal'}, 'is_open'),
)
def open_close_modal(n_clicks_open: int, n_clicks_close: int, is_open: bool):
    """Apre/chiude il pop-up di esportazione nel caso venga premuto il pulsante di export/di chiusura"""
    ctx = callback_context
    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered_id
    if triggered_id != '.':
        if 'modal' in triggered_id['item']:
            if 'open' in triggered_id['item']:
                return True
            elif 'close' in triggered_id['item']:
                return False

    return no_update


@callback([
    Output({'page':MATCH, 'item':'check-legend', 'location':'modal'}, 'value'),
    Output({'page':MATCH, 'item':'check-colors', 'location':'modal'}, 'value'),
    Output({'page':MATCH, 'item':'selector-dpi', 'location':'modal'}, 'value'),
    Output({'page':MATCH, 'item':'selector-format', 'location':'modal'}, 'value')],
    Input({'page':MATCH, 'item': 'modal'}, 'is_open'),
)
def initialize_values(is_open:bool):
    """All'apertura del modal inizializza i valori dei vari oggetti in base alle impostazioni salvate nei config"""
    if not is_open:
        return no_update, no_update, no_update, no_update
    configs = GLOBAL_CACHE.app_configs
    return (['show_legend'] if configs.legend else [],
            ['colors'] if configs.colors else [],
            configs.dpi,
            configs.export_format)


@callback(
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows', allow_duplicate=True),
    Input({'page':MATCH, 'item':'button-select-all'}, 'n_clicks'),
    State({'page':MATCH, 'item':'table', 'location':'modal'}, 'data'),
    prevent_initial_call=True
)
def select_all_rows(n_clicks, table_data):
    if not n_clicks:
        return no_update

    return [i for i in range(len(table_data))]


@callback(
    Output({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows', allow_duplicate=True),
    Input({'page':MATCH, 'item':'modal'}, 'is_open'),
    State({'page':MATCH, 'item':'table', 'location':'modal'}, 'selected_rows'),
    prevent_initial_call=True
)
def unselect_rows_modal(is_open:bool, selected_rows:list[int]):
    """Deseleziona le righe quando viene chiuso il pop-up"""
    if not is_open:
        return []
    return selected_rows


@callback(
    Output({'page':MATCH, 'item':'button-export'}, "disabled"),
    Input({'page':MATCH, 'item':'table', 'location':'modal'}, "derived_virtual_selected_rows"),
    prevent_initial_call=True
)
def enable_export_button(selected_rows:list[int]):
    """Attiva il pulsante di esportazione alla selezione di almeno un esperimento/gruppo"""
    if not selected_rows:
        return True
    return False


@callback(
    [Output({'page': MATCH, 'item': 'modal'}, 'is_open', allow_duplicate=True),
     Output({'page': MATCH, 'item': 'store-placeholder-modal'}, 'data')],
    Input({'page': MATCH, 'item': 'button-export'}, 'n_clicks'),
    [State({'page': MATCH, 'item': 'table', 'location': 'modal'}, 'id'),
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
def export_selected(n_clicks:int, table_id:dict[str,str], selected_rows:list[int],table_data:list[dict], mode:str, grouping_feature:str,
                    selected_curves:list[str], legend:list, colors:list, dpi_img:int, file_format:str):
    """Esporta le righe selezionate nella tabella del pop-up, premuto il bottone di export, e a fino processo chiude il pop-up"""
    if not n_clicks or not selected_rows:
        return no_update, no_update

    file_type = table_id['page']

    export_path = GLOBAL_CACHE.find_export_path()
    selected_rows = [table_data[i] for i in selected_rows]

    if mode == "grouped":
        figs:list[CustomFigure] = []
        for row in selected_rows:
            path_list = GLOBAL_CACHE.explode_group_paths(row['file_path'])
            group_df = GLOBAL_CACHE.tables[file_type].get_table_no_aff()
            group_df = group_df[group_df['file_path'].isin(path_list)]

            figs.append(
                CustomFigure(
                    FileCurves.from_df(group_df,
                                       grouped_by=grouping_feature if len(path_list) > 1 else None
                                       ),
                    curves_to_plot= selected_curves,
                    plot_all_curves=False,
                    legend=legend,
                    colored=colors,
                ).plot_group()
            )
    elif mode == "normal":
        df = pd.DataFrame(selected_rows)
        allowed_cols = [col for col in df.columns if "aff_" not in col]

        files = FileCurves.from_df(df[allowed_cols])

        figs:list[CustomFigure] = CustomFigure(
            files,
            curves_to_plot=selected_curves,
            plot_all_curves=False,
            legend=legend,
            colored=colors,
        ).plot_all()    # con questo metodo creo una lista di CustomFigures, ognuna con i dati di un solo file all'interno
    else:
        raise ValueError(f"La modalità {mode} non è supportata dall'applicazione")

    try:
        import plotly.io as pio
        file_paths = [export_path/f"{f.fig_stem}.{file_format}" for f in figs]
        pio.write_images(fig=figs, file=file_paths, format=file_format, scale=dpi_img/72)
        return False, None
    except Exception:
        return no_update, None


## DEBUGGING ##
if __name__ == "__main__":
    print(select_all_rows(1,[1,2,3,4,5,6]))