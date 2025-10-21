from .common import ExpCurves, toggle
import plotly.graph_objects as go
import numpy as np

## FUNC ##
def add_summary_legend(figure:go.Figure, colored:bool) -> go.Figure:
    """Aggiunge una legenda riassuntiva ad una figura contenete un gruppo di esperimenti"""
    # Aggiunge indicatori Vgf
    for vgf,marker in markers.items():
        figure.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(symbol=marker, size=12, color='black'),
            name=f"Vgf = {vgf}V",
            showlegend=True,
            legendgroup="vgf"
        ))

    # Aggiunge indicatori curve
    curves = ('v0', '0', '15', '30')
    for curve in curves:
        figure.add_trace(go.Scatter(
            x=[None], y=[None],
            mode = 'lines',
            line = dict(
                color=colors[curve] if colored else 'black',
                dash=None if colored else linestyles[curve],
                width=3,
            ),
            name=toggle(curve),
            showlegend=True,
            legendgroup="curves"
        ))

    return figure

def graphics_idvd(figure:go.Figure, group:bool=False) -> go.Figure:
    """Implementa la parte grafica della figura nel caso di grafico IdVd"""
    tick_x_pos = np.arange(-25, 25, 0.5)
    figure.update_layout(
        xaxis=dict(
            title="V<sub>D</sub> [V]",
            showline=True,
            linewidth=2,
            linecolor='black',
            mirror=False,
            tickmode='array',
            tickvals=tick_x_pos,
            ticktext=[f'{tick:.1f}' if tick % 1 == 0 else '' for tick in tick_x_pos],
            ticklen=8,
            tickwidth=2,
            tickcolor='black',
            ticks='outside',
            minor=dict(
                tickmode='linear',
                dtick=0.1,
                ticklen=4,
                tickwidth=1,
                tickcolor='black',
                ticks='outside',
            ),
            gridcolor='lightgray',
            gridwidth=1,
            griddash='dashdot',
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            title="I<sub>D</sub> [A/mm]",
            showline=True,
            linewidth=2,
            linecolor='black',
            mirror=False,
            tickmode='linear',
            dtick=0.1,
            ticklen=8,
            tickwidth=2,
            tickcolor='black',
            ticks='outside',
            minor=dict(
                tickmode='linear',
                dtick=0.02,
                ticklen=4,
                tickwidth=1,
                tickcolor='black',
                ticks='outside',
            ),
            gridcolor='lightgray',
            gridwidth=1,
            griddash='dashdot',
            showgrid=True,
            zeroline=False,
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=14),
        # width=800,
        height=600 if group else None,
    )
    return figure

def graphics_trapdata(figure:go.Figure) -> go.Figure:
    """Implementa la parte grafica della figura nel caso di grafico TrapData"""
    figure.update_layout(
        xaxis=dict(
            title="E [eV]",
            showline=True,
            linewidth=2,
            linecolor='black',
            mirror=True,
            tickmode='linear',
            dtick=0.5,
            ticklen=8,
            tickwidth=2,
            tickcolor='black',
            ticks='outside',
            minor=dict(
                tickmode='linear',
                dtick=0.1,
                ticklen=4,
                tickwidth=1,
                tickcolor='black',
                ticks='outside',
                gridcolor='lightgray',
                griddash='dot',
                gridwidth=0.5,
            ),
            gridcolor='gray',
            gridwidth=1,
            griddash='dash',
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            title="Charged Traps density [1/<sub>cm<sup>3</sup>·eV</sub>]",
            showline=True,
            linewidth=2,
            linecolor='black',
            mirror=True,
            tickmode='linear',
            dtick=0.5,
            ticklen=8,
            tickwidth=2,
            tickcolor='black',
            ticks='outside',
            minor=dict(
                tickmode='linear',
                dtick=0.1,
                ticklen=4,
                tickwidth=1,
                tickcolor='black',
                ticks='outside',
                gridcolor='lightgray',
                griddash='dot',
                gridwidth=0.5,
            ),
            gridcolor='gray',
            gridwidth=1,
            griddash='dash',
            showgrid=True,
            zeroline=False,
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=14),
        # width=800,
        height=600,
    )
    figure.add_annotation(
        x=0,
        y=1.02,
        xref="paper",
        yref="paper",
        text="<b>1e13</b>",
        showarrow=False,
        font=dict(size=14, ),
        xanchor="right",
        yanchor="bottom"
    )
    return figure

## MAIN FUNC ##
def plot(curves:ExpCurves, c_to_plot:list[str]=(), all_c:bool=False, to_export:bool=False, legend:bool=True, colored:bool=True)->go.Figure:
    """Plotta le curve interessate, contenute da un'istanza di ExpCurves, contenente a sua volta uno o più Exp"""
    if not curves.contains_imported_data:
        curves = curves.import_data

    exp_type = curves.exp[0].exp_type
    curves.names_update()
    fig = go.Figure()

    for curves_dict in curves.curves:
        for key in curves_dict.keys():
            if key in c_to_plot or all_c:
                fig.add_trace(go.Scatter(
                    x=curves_dict[key].X,
                    y=curves_dict[key].Y/1e13 if exp_type=='TrapData' else curves_dict[key].Y,
                    name=curves_dict[key].name,
                    mode='lines+markers',
                    line=dict(
                        color= colors[key] if colored else 'black',
                        dash=None if colored else linestyles[key],
                        width=0.75 if curves.contains_group else None,
                    ),
                    marker=dict(
                        symbol= markers[curves.get_vgf(curves_dict)] if curves.contains_group else 'square'
                    ),
                    visible=True,
                    showlegend=True if (not to_export or legend and not curves.contains_group) else False,
                ))
    if to_export and legend and curves.contains_group:
        fig = add_summary_legend(fig, colored=colored)

    if exp_type=='IdVd':
        fig = graphics_idvd(fig, curves.contains_group)
    elif exp_type=='TrapData':
        fig = graphics_trapdata(fig)
    return fig

## PARAMS ##
class Config:
    DPI = 300
    bk_color = 'white'
    sec_color = 'black'
    out_ext = 'png' #png, pdf, svg
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
    '0.9500': '#17e3bc',    # verde acqua
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