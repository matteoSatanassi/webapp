import dash
from app_elements.page_layout import layout

dash.register_page(__name__, path='/', name='IdVd')

## PARAMS ##
PAGE = 'IDVD'

## LAYOUT ##
layout = layout(PAGE)