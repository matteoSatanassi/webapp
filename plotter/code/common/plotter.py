from AppData.IdVd_plotter.Common import markers
from .common import ExpCurves, CP
import plotly.graph_objects as go

## MAIN FUNC ##
def plot(curves:ExpCurves, c_to_plot:list[str])->go.Figure:
    """Plotta le curve contenute volute da un'istanza di ExpCurves contenente uno o più Exp"""
    if not curves.contains_imported_data:
        curves.import_data()
    fig = go.Figure()
    for curves_dict in curves.curves:
        for c in c_to_plot:
            fig.add_trace(go.Scatter(
                x=curves_dict[c].X,
                y=curves_dict[c].Y,
                name=curves_dict[c].name,
                mode='lines+markers',
                line=dict(
                    color= colors[c] if Config.colors else 'black',
                    dash=None if Config.colors else linestyles[c],
                    width=0.75 if curves.contains_group else None,
                ),
                marker=dict(
                    symbol= markers[curves.get_vgf(curves_dict)] if curves.contains_group else 'square'
                ),
                visible=True
            ))
    return fig

## PARAMS ##
class Config:
    DPI = 300
    bk_color = 'white'
    sec_color = 'black'
    out_ext = 'png' #png, pdf, svg
    same_fig = True
    legend = True
    colors = True

colors = {
    'v0': 'red',
    '0': 'limegreen',
    '15': 'dodgerblue',
    '30': 'darkorange',
    'trap_density': 'black',
    '0.5000': '#1f77b4',    # blu
    '0.6160': '#ff7f0e',    # arancione
    '0.7660': '#2ca02c',    # verde
    '0.7830': '#d62728',    # rosso
    '0.9670': '#9467bd',    # viola
    '0.9840': '#8c564b',    # marrone
    '1.1840': '#e377c2',    # rosa
    '1.3340': '#17becf',    # azzurro
    '1.8340': '#bcbd22'     # giallo
}
linestyles = {
    "v0": "dashdot",
    "0": "dotted",
    "15": "dashed",
    "30": "solid"
}   # to use in case of colorless image configuration
markers = {
    -2: "square",
    -1: "circle",
    0: "triangle-down",
    1: "diamond",
    2: "star"
}  # to use in same fig, multiple plots