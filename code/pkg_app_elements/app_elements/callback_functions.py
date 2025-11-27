from app_elements.callbacks.Modal_cbks import *
from app_elements.callbacks.GraphsTab_cbks import *
from app_elements.callbacks.TableTab_cbks import *

## GLOBAL CALLBACKS ##
@callback(
    Output('store-trigger-indexing', 'data'),
    Input('store-trigger-indexing','data')
)
def indexing(trigger):
    """Callback che chiama la funzione di indexing"""
    if not trigger:
        from common import indexer
        indexer(data_dir)
        return True
    return no_update