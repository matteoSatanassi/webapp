from .classes import FileCurves
import plotly.graph_objects as go
import numpy as np


## PARAMS ##
def load_plotter_configs():
    """
    Carica i parametri di funzionamento del plotter
    """
    from pathlib import Path
    import json

    config_file = Path(__file__).parent / "plotter_configs.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError("Non è stato possibile trovare il file di configurazione")


## FUNC ##
def add_summary_legend(figure:go.Figure, colored:bool) -> go.Figure:
    """Aggiunge una legenda riassuntiva a una figura contenete un gruppo di esperimenti"""
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
    for curve in Exp.IdVd_names:
        figure.add_trace(go.Scatter(
            x=[None], y=[None],
            mode = 'lines',
            line = dict(
                color=colors[curve] if colored else 'black',
                dash=None if colored else linestyles[curve],
                width=3,
            ),
            name=Exp.toggle(curve),
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
            mirror=False,
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
                # gridcolor='lightgray',
                # griddash='dot',
                # gridwidth=0.5,
            ),
            gridcolor='lightgray',
            gridwidth=1,
            griddash='dashdot',
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            title="Charged Traps density [1/<sub>cm<sup>3</sup>·eV</sub>]",
            showline=True,
            linewidth=2,
            linecolor='black',
            mirror=False,
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
                # gridcolor='lightgray',
                # griddash='dot',
                # gridwidth=0.5,
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
def plot(curves:FileCurves,
         c_to_plot:list[str]=(),
         all_c:bool=False,
         to_export:bool=False,
         legend:bool=True,
         colored:bool=True)->go.Figure:
    """Plotta le curve interessate, contenute da un'istanza di ExpCurves, contenente a sua volta uno o più Exp"""
    plotter_configs = load_plotter_configs()

    if curves.file_type == "TRAPDATA": colored=True # colorless non supportato per curve trapdata
    if curves.contains_group:
        try:
            if curves.grouped_by in plotter_configs["GroupMarkers"][curves.file_type]:
                fig = go.Figure()
            else:
                raise AttributeError(
                    "Non è stato possibile individuare la feature di raggruppamento tra quelle supportate dal plotter"
                )
        except AttributeError:
            raise AttributeError(
                f"Il file type {curves.file_type} non è supportato per il raggruppamento curve"
            )

    out = []

    for f_features,f_curves in curves.expose_all:

        if not curves.contains_group:
            fig  = go.Figure()

        # per ogni curva del file considerato in questo ciclo
        for key in f_curves.keys():
            # se la curva è nella lista di quelle da stampare o se sono tutte da stampare
            if key in c_to_plot or all_c:
                fig.add_trace(go.Scatter(
                    x = f_curves[key].X,
                    y = f_curves[key].Y,
                    name = f_curves[key].name,
                    mode = 'lines+markers',
                    line = dict(
                        color= plotter_configs["AllowedCurveColors"][curves.file_type][key] if colored else "black",
                        dash=None if colored else plotter_configs["Linestyles"][curves.file_type][key],
                        width=0.75 if curves.contains_group else None,
                    ),
                    marker = dict(
                        symbol= plotter_configs["GroupMarkers"][curves.file_type][f_features[curves.grouped_by]] if
                        curves.contains_group else "square",
                    ),
                    visible=True,
                    showlegend = True if (legend and not curves.contains_group) else False
                ))

        if not curves.contains_group:
            out.append(fig)

    if curves.contains_group and legend:
        fig  = add_group_legend()
        out.append(fig)

    match curves.file_type:
        case "IDVD": out = [graphics_idvd(fig, group=curves.contains_group) for fig in out]
        case "TRAPDATA": out = [graphics_trapdata(fig) for fig in out]

    return out


if __name__=='__main__':
    # path = r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IdVd_TrapDistr_exponential_Vgf_0_Es_0.2_Em_0.2.csv"
    # e = FileCurves.from_path(path)
    # plot(e, all_c=True).show()
    from pathlib import Path

    print(Path(__file__).parent/"plotter_configs.json")