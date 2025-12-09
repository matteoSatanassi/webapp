"""
Il modulo raccorda tutte le callback definite in altri moduli, e definisce le callback globali
"""

from app_elements.callbacks.Modal_cbks import *
from app_elements.callbacks.GraphsTab_cbks import *
from app_elements.callbacks.TableTab_cbks import *
from app_elements.page_elements import my_table_template
from app_elements.page_layout import children_layout
from app_elements.builders import nav_builder


## GLOBAL CALLBACKS ##
@callback(
    Output('nav-holder','children'),
    Output('store-trigger-update','data'),
    Input('store-trigger-refresh','data'),
)
def refresh_cache(refresh_flag):
    """Callback che ricarica la memoria cache dell'applicazione e aggiorna la barra di navigazione"""
    if refresh_flag:
        print('Refreshing cache')
        GLOBAL_CACHE.refresh()

        print('Refreshing navbar\n')

        return nav_builder(), True

    return no_update, no_update


@callback(
    Output({'page':MATCH, 'item':'container-ALL'}, 'children'),
    Input('store-trigger-update','data'),
    State({'page':MATCH, 'item':'container-ALL'}, 'id')
)
def refresh_page_content(trigger_update, container_id):
    """La callback ricarica il layout della pagina corrente"""
    print(f'layout update call\ntrigger: {trigger_update}\n')
    if trigger_update:
        return children_layout(container_id['page'])
    return no_update


@callback(
    Output('container-app', 'className'),
    Input('url','pathname'),
)
def dotted_bkg(url):
    """Mette lo sfondo a pallini nella pagina Home"""
    if url== '/':
        return 'dotted-bkg'
    return None
