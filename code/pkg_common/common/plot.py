from common.classes import FileCurves, Curve
import plotly.graph_objects as go


## PARAMS ##
class PlotterConfigs(object):
    default_marker = "square"
    def __init__(self, file_type:str):
        cfg = self.load_plotter_configs()
        try:
            self.colors = cfg["Colors"][file_type]
        except KeyError:
            print(f"Non sono specificati colori per le curve dei file {file_type}")
            self.colors = None
        try:
            self.linestyles = cfg["Linestyles"][file_type]
        except KeyError:
            print(f"Non sono specificati linestyles per le curve dei file {file_type}")
            self.linestyles = None
        try:
            self.group_markers = cfg["GroupMarkers"][file_type]
        except KeyError:
            print(f"Non sono specificati marker di raggruppamento per le curve dei file {file_type}")
            self.group_markers = None

    def get_markers(self, group_feature):
        """Metodo che, data una feature di raggruppamento, ritorna un dizionario del tipo {feature_value:marker}"""
        try:
            return self.group_markers[group_feature]["Values"]
        except KeyError:
            raise KeyError(
                """Non è stato possibile individuare la feature di raggruppamento tra quelle supportate dal plotter
                Aggiungere i marker di gruppo dedicati alla feature nei file di configurazione del plotter"""
            )
    def get_group_feature_size(self, group_feature):
        """Metodo che, data una feature di raggruppamento, ritorna la sua grandezza fisica"""
        try:
            return self.group_markers[group_feature]["Size"]
        except KeyError:
            raise KeyError(
                """Non è stato possibile individuare la feature di raggruppamento tra quelle supportate dal plotter
                Aggiungere i marker di gruppo dedicati alla feature nei file di configurazione del plotter"""
            )

    @staticmethod
    def load_plotter_configs():
        """
        Carica i parametri di funzionamento del plotter
        """
        from pathlib import Path
        import json

        config_file = Path(__file__).parent / "plotter_configs.json"
        if config_file.exists():
            with open(config_file, 'r', encoding="utf-8") as f:
                return json.load(f)
        else:
            raise FileNotFoundError("Non è stato possibile trovare il file di configurazione")

## MAIN FUNC ##
def plot_tab(curves:FileCurves,
            c_to_plot:list[str]=(),
            all_c:bool=True,
            legend:bool=True,
            colored:bool=True,
            plot_targets:bool=False)->"CustomFigure":
    """Plotta le curve interessate, contenute da un'istanza di ExpCurves, contenente a sua volta uno o più Exp"""

    custom_fig = CustomFigure(curves,
                             curves_to_plot=c_to_plot,
                             plot_all_curves=all_c,
                             legend=legend,
                             colored=colored
                             )

    # controllo se curves contiene un gruppo di curve
    if curves.contains_group:
        if plot_targets:
            return custom_fig.plot_targets().plot_group()
        else:
            return custom_fig.plot_group()
    else:
        if plot_targets:
            return custom_fig.plot_targets().plot_all()
        else:
            return custom_fig.plot_all()

## CLASS ##
class CustomFigure(go.Figure):
    def __init__(self,
                 curves:FileCurves,
                 curves_to_plot:list[str]=(),
                 plot_all_curves:bool=True,
                 legend:bool=True,
                 colored:bool=True,
                 *args, **kwargs):
        self._curves = curves
        self._plotting_params = PlotterConfigs(curves.file_type)
        self._c_to_plot = curves_to_plot
        self._all_c = plot_all_curves
        self._legend = legend

        # controllo colored, in caso non siano state create opzioni per le curve nere
        self._colored = colored if self._plotting_params.linestyles else True

        super().__init__(*args, **kwargs)

    def __copy__(self):
        # creo una nuova istanza, dato che _curves rimane immutato, posso anche solo passare il rif
        new_fig = self.__class__(self._curves)

        new_fig.update(self.to_dict())  # copio i dati Plotly in modo standard

        # Gli attributi semplici e immutabili (str, bool, list[str] semplice)
        # possono essere copiati direttamente, bastano anche solo i riferimenti
        new_fig._c_to_plot = self._c_to_plot
        new_fig._all_c = self._all_c
        new_fig._legend = self._legend
        new_fig._colored = self._colored

        return new_fig

    @property
    def c_to_plot(self):
        return self._c_to_plot
    @property
    def all_c(self):
        return self._all_c
    @property
    def legend(self):
        return self._legend
    @property
    def colored(self):
        return self._colored

    @property
    def _get_group_markers(self):
        """
        In base alla feature di raggruppamento usata nell'istanza ritorna il giusto dizionario {feature_value:marker}
        """
        return self._plotting_params.get_markers(self._curves.grouped_by)
    @property
    def _get_group_feature_size(self):
        """
        In base alla feature di raggruppamento usata nell'istanza ritorna la sua grandezza fisica
        """
        return self._plotting_params.get_group_feature_size(self._curves.grouped_by)
    @property
    def _contains_group(self):
        return self._curves.contains_group
    @property
    def _contains_tab_data(self):
        return self._curves.contains_tab_data
    @property
    def grouped_by(self):
        """Ritorna la feature di raggruppamento se ne esiste una"""
        return self._curves.grouped_by if self._contains_group else None
    @property
    def get_group_stem(self):
        """Il metodo controlla che l'istanza contenga i dati di un gruppo e ne ritorna il nome"""
        return self._curves.get_group_stem
    @property
    def fig_stem(self):
        """
        Ritorna il nome da dare alla figura.
        Il metodo da risultato se la figura contiene i dati di un solo file o di un gruppo,
        altrimenti ritorna errore
        """
        if len(self._curves)==1:
            return self._curves.paths_list()[0].stem
        elif self._contains_group:
            return self.get_group_stem
        else:
            raise ValueError("Non è possibile dare un nome ad una figura contenente i grafici di diversi file")
    @property
    def get_tab_label(self):
        """Se i dati contenuti nell'istanza sono visualizzabili in un tab, ritorna la label che avrebbe"""
        if self._contains_tab_data:
            return self._curves.get_tab_label()
        else:
            return ValueError(f"L'oggetto non è applicabile ad un tab di visualizzazione")


    def _add_curve(self,
                   curve:Curve,
                   scales:dict[str,float] = None) -> "CustomFigure":
        """Aggiunge all'istanza la curva specificata, con colore, stile di linea, marker e nome come impostati"""
        if not scales: scales = {"X":0, "Y":0}
        try:
            self.add_trace(
                go.Scatter(
                    x=curve.X / (10**scales["X"] if scales["X"]>1 else 1),
                    y=curve.Y / (10**scales["Y"] if scales["Y"]>1 else 1),
                    name=curve.name,
                    mode='lines+markers',
                    line=dict(
                        color=curve.color,
                        dash=curve.linestyle,
                        width=0.75 if self._contains_group else None,
                    ),
                    marker=dict(
                        symbol=curve.markers
                    ),
                    visible=True,
                    showlegend=True if (self.legend and not self._contains_group) else False
                )
            )
        except AttributeError:
            raise f"Non definiti gli attributi necessari nell'oggetto {curve}"
        return self

    def _add_summary_legend(self) -> "CustomFigure":
        """Aggiunge una legenda riassuntiva a una figura contenete un gruppo di esperimenti"""
        if not self._contains_group:
            return self

        # Aggiunge markers feature raggruppamento (Es. Vgf=-2 -> square)
        for feature_value,marker in self._get_group_markers.items():
            self.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(symbol=marker, size=12, color='black'),
                name=f"{self._curves.grouped_by}={feature_value} {self._get_group_feature_size}",
                showlegend=True,
                legendgroup="vgf"
            ))

        # Aggiunge indicatori curve
        for key, color in self._plotting_params.colors.items():
            self.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='lines',
                line=dict(
                    color=color if self.colored else 'black',
                    dash=None if self.colored else self._plotting_params.linestyles[key],
                    width=3,
                ),
                name=self._curves.allowed_curves[key],
                showlegend=True,
                legendgroup="curves"
            ))

        return self

    def _add_graphics(self, scales:dict[str,float]=None) -> "CustomFigure":
        """In base alla tipologia di file contenuta chiama il giusto metodo per aggiungere la parte grafica alla figura"""
        if not scales: scales = {"X":0, "Y":0}
        match self._curves.file_type:
            case "IDVD":
                return self._graphics_idvd(scales)
            case "TRAPDATA":
                return self._graphics_trapdata(scales)
            case _:
                raise f"I file {self._curves.file_type} non hanno una grafica supportata"
    def _graphics_idvd(self, scales:dict[str,int]) -> "CustomFigure":
        """Implementa la parte grafica della figura nel caso di grafico IdVd"""
        self.update_layout(
            xaxis=dict(
                title="V<sub>D</sub> [V]",
                showline=True,
                linewidth=2,
                linecolor='black',
                mirror=False,
                tickmode='auto',
                ticklen=8,
                tickwidth=2,
                tickcolor='black',
                ticks='outside',
                minor=dict(
                    tickmode='auto',
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
                tickmode='auto',
                # dtick=0.1,
                ticklen=8,
                tickwidth=2,
                tickcolor='black',
                ticks='outside',
                minor=dict(
                    tickmode='auto',
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
            height=600 if self._contains_group else None,
        )
        if scales["Y"] > 1:
            self.add_annotation(
                x=0,
                y=1.02,
                xref="paper",
                yref="paper",
                text=f"<b>1e{scales["Y"]}</b>",
                showarrow=False,
                font=dict(size=14, ),
                xanchor="right",
                yanchor="bottom"
            )
        if scales["X"] > 1:
            self.add_annotation(
                x=1.08,
                y=-0.075,
                xref="paper",
                yref="paper",
                text=f"<b>1e{scales["X"]}</b>",
                showarrow=False,
                font=dict(size=14, ),
                xanchor="right",
                yanchor="bottom"
            )
        return self
    def _graphics_trapdata(self, scales:dict[str,int]) -> "CustomFigure":
        """Implementa la parte grafica della figura nel caso di grafico TrapData"""
        self.update_layout(
            xaxis=dict(
                title="E [eV]",
                showline=True,
                linewidth=2,
                linecolor='black',
                mirror=False,
                tickmode='auto',
                # dtick=0.5,
                ticklen=8,
                tickwidth=2,
                tickcolor='black',
                ticks='outside',
                minor=dict(
                    tickmode='auto',
                    # dtick=0.1,
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
        if scales["Y"] > 1:
            self.add_annotation(
                x=0,
                y=1.02,
                xref="paper",
                yref="paper",
                text=f"<b>1e{scales["Y"]}</b>",
                showarrow=False,
                font=dict(size=14, ),
                xanchor="right",
                yanchor="bottom"
            )
        if scales["X"] > 1:
            self.add_annotation(
                x=1.08,
                y=-0.075,
                xref="paper",
                yref="paper",
                text=f"<b>1e{scales["X"]}</b>",
                showarrow=False,
                font=dict(size=14, ),
                xanchor="right",
                yanchor="bottom"
            )
        return self

    def plot_group(self) -> "CustomFigure":
        if not self._contains_group:
            raise ValueError(f"{self._curves} non contiene un gruppo")
        if not self._plotting_params.group_markers:
            raise ValueError(f"Il file type {self._curves.file_type} non è supportato per il raggruppamento curve")
        if not self._get_group_markers:
            raise KeyError(
                """Non è stato possibile individuare la feature di raggruppamento tra quelle supportate dal plotter
                Aggiungere i marker di gruppo dedicati alla feature nei file di configurazione del plotter"""
                )

        for f_features, f_curves in self._curves.expose_all:
            # f_features: dizionario delle features del file correntemente considerato
            # f_curves: dizionario delle curve contenute nel file

            for key, curve in f_curves.items():
                curve = curve.__copy__()
                if key in self.c_to_plot or self.all_c:
                    # per ogni curva salviamo colore, linestyle e marker utilizzato e modifichiamo il nome
                    curve.color = self._plotting_params.colors[key] if self.colored else "black"
                    curve.linestyle = None if self.colored else self._plotting_params.linestyles[key]
                    # Prendo i marker dal dizionario dei config {feature_group:{feature_group_file:marker_value}}
                    # Es. {Vgf:{2:square}}
                    curve.markers = self._get_group_markers[f_features[self.grouped_by]]
                    curve.name = (
                        f"{curve.name}, {self.grouped_by}={f_features[self.grouped_by]} {self._get_group_feature_size}"
                    )

                    self._add_curve(curve)

        if self.legend:
            self._add_summary_legend()

        return self._add_graphics()

    def plot_all(self) -> "CustomFigure|list[CustomFigure]":
        """
        Ritorna le figure di tutti i file contenuti nell'istanza
        :return: In caso di un singolo file un'istanza plottata della classe CustomFigure, in caso di più file una lista di istanze plottate
        """

        # caso 1 solo file -> ritorna una CustomFigure
        if len(self._curves) == 1:
            for f_features, f_curves in self._curves.expose_all:
                scales = Curve.get_curves_scales(*f_curves.values())
                for key, curve in f_curves.items():
                    curve = curve.__copy__()
                    curve.color = self._plotting_params.colors[key] if self.colored else "black"
                    curve.linestyle = None if self.colored else self._plotting_params.linestyles[key]
                    # nel caso di grafici di singoli file non ho bisogno di cambiare i marker, uso quelli di default
                    curve.markers = self._plotting_params.default_marker
                    # il nome rimane quello già salvato nella curva
                    self._add_curve(curve, scales=scales)
                return self._add_graphics(scales)

        # caso più file -> lista di figure
        out = []
        for file_data in self._curves.subdivide:
            # creo istanze CustomFigure contenenti i dati di singoli file
            fig = CustomFigure(
                file_data,
                curves_to_plot=self.c_to_plot,
                plot_all_curves=self.all_c,
                legend=self.legend,
                colored=self.colored
            )
            out.append(fig.plot_all())
        return out

    def plot_targets(self) -> "CustomFigure":
        """
        Il metodo aggiunge alla figura le curve target, in nero, delle curve contenute nell'istanza

        La funzione non si occupa di stampare le curve contenute nell'istanza o aggiungere le grafiche,
        quindi l'operazione deve essere fatta in precedenza o in seguito
        """
        if not len(self._curves)==1 and not self._contains_group:
            raise ValueError(f"L'oggetto non è applicabile ad un tab di visualizzazione")

        for f_features,_ in self._curves.expose_all:
            target = FileCurves.find_target_file(self._curves.file_type, f_features)
            for t_features,t_curves in target.expose_all:
                t_scales = Curve.get_curves_scales(*t_curves.values())
                for key,curve in t_curves.items():
                    curve.color = "gray"
                    curve.linestyle = self._plotting_params.linestyles[key]
                    if self._contains_group:
                        curve.name = (
                            f"{curve.name}, {self.grouped_by}={t_features[self.grouped_by]} {self._get_group_feature_size}"
                        )
                        curve.markers = self._get_group_markers[t_features[self.grouped_by]]

                        self._add_curve(curve)
                    else:
                        curve.name = f"{curve.name}"
                        curve.markers = self._plotting_params.default_marker

                        self._add_curve(curve,t_scales)

        return self


if __name__=='__main__':
    from pathlib import Path

    # path = r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IdVd_TrapDistr_exponential_Vgf_0_Es_0.2_Em_0.2.csv"
    # path = r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\TrapData_TrapDistr_exponential_Vgf_1_Es_1.72_Em_1.31_state_v0.csv"
    paths = [
        Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_-1_Es_1.72_Em_0.18.csv'),
        Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_0_Es_1.72_Em_0.18.csv'),
        Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_1_Es_1.72_Em_0.18.csv'),
        Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_2_Es_1.72_Em_0.18.csv'),
        Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_-2_Es_1.72_Em_0.18.csv')]
    e = FileCurves.from_paths(*paths)
    e.get_grouping_feat()
    figs:CustomFigure = CustomFigure(e).plot_group()

    figs2 = figs.__copy__()

    figs.show()
    figs2.show()