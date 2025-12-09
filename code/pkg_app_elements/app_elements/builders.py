import dash
import dash_bootstrap_components as dbc
from app_elements.page_layout import layout
from app_resources.AppCache import GLOBAL_CACHE


def page_builder(file_type:str):
    """
    Genera il layout specifico per un dato tipo di file e lo registra con un nome univoco.

    Se file_type è presente tra i file_types supportati, crea un container
    e lo popola di elementi, altrimenti lo lascia vuoto, tanto verrà disabilitato nella navbar.
    """
    dash.register_page(
        f"page.{file_type}",
        path=f"/{file_type}",
        name=file_type,
        layout=layout(file_type),
    )

def nav_builder():
    """Genera automaticamente la l'oggetto dbc.Nav da usare come menù dell'applicazione"""
    navs = [
        dbc.NavItem(dbc.NavLink('Config Page',
                                href='/configs',
                                active='exact',
                                )
                    ),
    ]

    navs.extend(
        [
            dbc.NavItem(dbc.NavLink(f'{file_type} Plotter',
                                    href=f'/{file_type}',
                                    active='exact',
                                    disabled=True if file_type in GLOBAL_CACHE.tables.not_presents else False,
                                    )
                        )
            for file_type in GLOBAL_CACHE.file_types
        ]
    )

    return dbc.Nav(
        navs,
        pills=True,
    )