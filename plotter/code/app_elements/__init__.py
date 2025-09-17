from .callback_functions import _create_tabs_callback, _create_export_callback, _create_graph_callback, _create_modal_callbacks, _create_tables_callbacks
from .page_elements import my_table_template, mode_options, export_modal
from .parameters import data_dir, load_configs, config_path

__all__ = ['my_table_template', 'mode_options', 'export_modal', 'data_dir', '_register_all_callbacks', 'load_configs']

def _register_all_callbacks(page:str):
    """
    Crea le funzioni di callback per le pagine IdVd e TrapData
    :param page: la pagina di cui creare le callbacks
    :return: ritorna le varie funzioni, in ordine tabs_callback, graph_callback, modal_callbacks(2), export_callback e,
    nel caso la pagina sia IdVd, anche le tables_callbacks(2)
    """
    if page == 'IdVd':
        return (_create_tabs_callback(page), _create_graph_callback(page), *_create_modal_callbacks(page),
                _create_export_callback(page), *_create_tables_callbacks(page))
    else:
        return (_create_tabs_callback(page), _create_graph_callback(page), *_create_modal_callbacks(page),
                _create_export_callback(page))