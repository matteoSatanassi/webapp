"""
Il modulo implementa la classe principale utilizzata per le funzioni di plotting dei dati,
nonché la funzione semplificata per il plotting dei dati contenuti nei tab
"""


import plotly.graph_objects as go
from common.PlotterConfigs import PlotterConfigs
from common.classes import FileCurves, Curve


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
        return custom_fig.plot_group(target_curves=plot_targets)
    else:
        return custom_fig.plot_all(target_curves=plot_targets)[0]

## CLASS ##
class CustomFigure(go.Figure):
    def __init__(self,
                 curves:FileCurves,
                 curves_to_plot:list[str]=(),
                 plot_all_curves:bool=True,
                 legend:bool=True,
                 colored:bool=True,
                 *args, **kwargs):

        # attributi nascosti per permettere la compatibilità con go.Figure
        self._curves = curves
        self._c_to_plot = curves_to_plot
        self._all_c = plot_all_curves
        self._legend = legend

        ## PARAMS ##
        self._configs = PlotterConfigs.files_configs[self._file_type]

        # controllo colored, in caso non siano state create opzioni per le curve nere
        self._colored = colored if self._configs.linestyles else True

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

    @classmethod
    def sub_samples_plot(cls, fig:"CustomFigure", *x_vals:float):
        """
        Data una figura, crea la figura dei suoi sub samples alle ascisse desiderate

        La figura deve contenere un gruppo o un singolo file
        """

        if not fig._contains_tab_data:
            raise ValueError("La figura passata non è applicable ad un tab di visualizzazione")

        out = cls(
            fig._curves,
            curves_to_plot=fig._c_to_plot,
            plot_all_curves=fig._all_c,
            legend=fig._legend,
            colored=fig._colored
        )

        if fig._contains_group:
            return out.plot_group_subsamples(*x_vals)

        return out.plot_all_subsamples(*x_vals)[0]

    @property
    def _get_group_markers(self):
        """
        In base alla feature di raggruppamento usata
        nell'istanza ritorna il giusto dizionario {feature_value:marker}

        Nel caso ci sia stato un errore e la feature di raggruppamento
        non comparisse tra quelle specificate nel file di configurazione,
        ritorna None
        """
        return self._configs.get_group_markers(self._grouped_by)
    @property
    def _get_group_feature_size(self):
        """
        In base alla feature di raggruppamento usata nell'istanza,
        ritorna la sua grandezza fisica

        Nel caso non fosse definita, ritorna None
        """
        return self._configs.get_grouping_feat_size(self._grouped_by)
    @property
    def _contains_group(self):
        return self._curves.contains_group
    @property
    def _contains_tab_data(self):
        return self._curves.contains_tab_data
    @property
    def _file_type(self):
        """Ritorna il file_type dei dati contenuti nell'istanza"""
        return self._curves.file_type
    @property
    def _grouped_by(self):
        """Ritorna la feature di raggruppamento se ne esiste una"""
        return self._curves.grouped_by if self._contains_group else None
    @property
    def _get_group_stem(self):
        """Il metodo controlla che l'istanza contenga i dati di un gruppo e ne ritorna il nome"""
        return self._curves.get_group_stem

    @property
    def fig_stem(self):
        """
        Ritorna il nome da dare alla figura.
        Il metodo da risultato se la figura contiene i dati
        di un solo file o di un gruppo, altrimenti ritorna errore
        """
        if len(self._curves)==1:
            return self._curves.paths_list()[0].stem
        elif self._contains_group:
            return self._get_group_stem
        else:
            raise ValueError("Non è possibile dare un nome ad una figura contenente i grafici di diversi file")
    @property
    def get_tab_label(self):
        """
        Se i dati contenuti nell'istanza sono visualizzabili in un tab,
        ritorna la label che avrebbe
        """
        if self._contains_tab_data:
            return self._curves.get_tab_label()
        else:
            return ValueError(f"L'oggetto non è applicabile ad un tab di visualizzazione")


    def _add_curve(self,
                   curve:Curve,
                   scales:dict[str,float] = None,
                   marker_size:int = 6) -> "CustomFigure":
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
                        width=curve.width,
                    ),
                    marker=dict(
                        symbol=curve.markers,
                        size=marker_size,
                    ),
                    visible=True,
                    showlegend=True if (self._legend and not self._contains_group) else False
                )
            )
        except AttributeError:
            raise f"Non definiti gli attributi necessari nell'oggetto {curve}"
        return self

    def _add_scatter(self,
                     curve:Curve,
                     scales:dict[str,float] = None,
                     mode = "markers",
                     marker_size:int = 6) -> "CustomFigure":
        """
        Aggiunge all'istanza i punti specificati nell'oggetto curve,
        con colore, stile di linea, marker e nome come impostati
        all'interno di quest'ultimo

        :param mode: "markers", "lines+markers
        """
        if not scales: scales = {"X":0, "Y":0}
        try:
            self.add_scatter(
                x=curve.X / (10**scales["X"] if scales["X"]>1 else 1),
                y=curve.Y / (10**scales["Y"] if scales["Y"]>1 else 1),
                name=curve.name,
                mode=mode,
                line=dict(
                    color=curve.color,
                    dash=curve.linestyle,
                    width=curve.width,
                ),
                marker=dict(
                    color=curve.color,
                    symbol=curve.markers,
                    size=marker_size,
                ),
                visible=True,
                showlegend=True if (self._legend and not self._contains_group) else False
            )
        except AttributeError:
            raise f"Non definiti gli attributi necessari nell'oggetto {curve}"
        return self

    def _send_to_back(self, N:int):
        """
        Sposta le ultime N tracce aggiunte sullo sfondo
        """
        all_traces = list(self.data)

        if not all_traces:
            return self

        to_back = all_traces[-N:]
        remaining = all_traces[:-N]

        # Sovrascrive la tupla data della figura
        self.data = to_back + remaining
        return self

    def _add_summary_legend(self) -> "CustomFigure":
        """Aggiunge una legenda riassuntiva a una figura contenete un gruppo di esperimenti"""
        if not self._contains_group:
            return self

        grouping_feat = self._grouped_by
        feature_size = self._get_group_feature_size
        # Aggiunge markers feature raggruppamento (Es. Vgf=-2 -> square)
        for feature_value,marker in self._get_group_markers.items():
            self.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(
                    symbol=marker,
                    size=12,
                    color='black'),
                name=f"{grouping_feat}={feature_value} {feature_size}",
                showlegend=True,
                legendgroup=grouping_feat
            ))

        # Aggiunge indicatori curve
        for curve,color in self._configs.colors.items():
            self.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='lines',
                line=dict(
                    color=color if self._colored else 'black',
                    dash=None if self._colored else self._configs.linestyles[curve],
                    width=3),
                name=self._curves.allowed_curves[curve],
                showlegend=True,
                legendgroup="colors"
            ))

        return self

    def _add_graphics(self, scales:dict[str,float]=None) -> "CustomFigure":
        """In base alla tipologia di file contenuta chiama il giusto metodo per aggiungere la parte grafica alla figura"""
        if not scales: scales = {"X":0, "Y":0}

        self.update_layout(
            xaxis=dict(
                title=self._configs.get_axis_title('x'),
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
                title=self._configs.get_axis_title('y'),
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
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=14),
            # width=800,
            height=600 if self._contains_group else None,
        )

        # aggiungo annotazione della scala se presente
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

    def plot_targets(self) -> "CustomFigure":
        """
        Il metodo aggiunge alla figura le curve target delle curve contenute nell'istanza

        La funzione non si occupa di stampare le curve contenute nell'istanza o aggiungere le grafiche,
        quindi l'operazione deve essere fatta in precedenza o in seguito a queste ultime
        """
        if not self._contains_tab_data:
            raise ValueError("L'oggetto non è applicabile ad un tab di visualizzazione")

        group_markers_dict = self._get_group_markers
        grouping_feat_size = self._get_group_feature_size

        linestyles_dict = self._configs.linestyles

        # numero di curve target stampate
        N = 0

        for f_features,_ in self._curves.expose_all:
            target = FileCurves.find_target_file(self._curves.file_type, f_features)
            for t_features,t_curves in target.expose_all:
                t_scales = Curve.get_curves_scales(*t_curves.values())
                for key,curve in t_curves.items():
                    N += 1
                    curve.color = "gray"
                    curve.linestyle = linestyles_dict[key] if linestyles_dict else None
                    if self._contains_group:
                        curve.name = (
                            f"{curve.name}, {self._grouped_by}={t_features[self._grouped_by]} {grouping_feat_size}"
                        )
                        curve.markers = group_markers_dict[f_features[self._grouped_by]]
                        curve.width = 0.6

                        self._add_curve(curve, marker_size=3)
                    else:
                        curve.name = f"{curve.name}"
                        curve.markers = self._configs.default_marker
                        curve.width = 0.75

                        self._add_curve(curve,t_scales, marker_size=3)

        return self._send_to_back(N)

    def plot_targets_subsamples(self, *x_vals) -> "CustomFigure":
        """
        Il metodo aggiunge alla figura le subsamples delle curve target
        delle curve contenute nell'istanza

        La funzione non si occupa di stampare le curve contenute
        nell'istanza o aggiungere le grafiche, quindi l'operazione
        deve essere fatta in precedenza o in seguito a queste ultime
        """
        contains_group = self._contains_group
        if not self._contains_tab_data:
            raise ValueError(f"L'oggetto non è applicabile ad un tab di visualizzazione")

        if contains_group:
            group_markers_dict = self._get_group_markers
            grouping_feat_size = self._get_group_feature_size
            if not group_markers_dict:
                raise ValueError(f"non sono stati definiti dei marker "
                             f"per il raggruppamento di file {self._file_type} "
                             f"sotto la feature {self._grouped_by}")

        colors_dict = self._configs.colors

        for f_features,_ in self._curves.expose_all:
            target = FileCurves.find_target_file(self._curves.file_type, f_features)
            for t_features,t_curves in target.expose_all:
                t_scales = Curve.get_curves_scales(*t_curves.values())
                sub_samples = {
                    t_id:t.create_sub_sample(*x_vals) for t_id,t in t_curves.items()
                }
                for key,curve in sub_samples.items():
                    curve.color = colors_dict[key]
                    curve.linestyle = None
                    if contains_group:
                        # entra solo se deve stampare un gruppo
                        # noinspection PyUnboundLocalVariable
                        curve.name = (
                            f"{curve.name}, {self._grouped_by}={t_features[self._grouped_by]} {grouping_feat_size}"
                        )
                        # noinspection PyUnboundLocalVariable
                        curve.markers = group_markers_dict[t_features[self._grouped_by]]
                        curve.width = 0.6

                        self._add_scatter(curve, mode="markers")
                    else:
                        curve.name = f"{curve.name}"
                        curve.markers = self._configs.default_marker
                        curve.width = 0.75

                        self._add_scatter(curve,t_scales, mode="markers")

        self.update_traces(
            selector=dict(mode='markers'),  # Applica solo alle tracce che sono puramente scatter di punti
            marker=dict(
                line=dict(
                    width=1 if self._contains_group else 2,
                    color='DarkSlateGrey'  # Colore del contorno
                ),
            )
        )

        return self

    def plot_group(self, target_curves=False) -> "CustomFigure":
        """Controlla che l'istanza contenga i dati di un gruppo di esperimenti, e in caso ne stampa il grafico"""
        if not self._contains_group:
            raise ValueError(f"{self._curves} non contiene un gruppo")

        group_markers_dict = self._get_group_markers
        grouping_feat_size = self._get_group_feature_size
        if not group_markers_dict:
            raise ValueError(f"non sono stati definiti dei marker "
                             f"per il raggruppamento di file {self._file_type} "
                             f"sotto la feature {self._grouped_by}")

        linestyles_dict = None
        colors_dict = None
        if self._colored: colors_dict = self._configs.colors
        else: linestyles_dict = self._configs.linestyles

        if target_curves:
            self.plot_targets()

        for f_features, f_curves in self._curves.expose_all:
            # f_features: dizionario delle features del file correntemente considerato
            # f_curves: dizionario delle curve contenute nel file

            for key, curve in f_curves.items():

                if key in self._c_to_plot or self._all_c:

                    curve = curve.__copy__()
                    # per ogni curva salviamo colore, linestyle, width e marker utilizzato e modifichiamo il nome
                    curve.color = colors_dict[key] if self._colored else "black"
                    curve.linestyle = None if self._colored else linestyles_dict[key]
                    curve.width = 0.75
                    # Prendo i marker dal dizionario dei config {feature_group:{feature_group_file:marker_value}}
                    # Es. {Vgf:{2:square}}
                    curve.markers = group_markers_dict[f_features[self._grouped_by]]
                    curve.name = (
                        f"{curve.name}, {self._grouped_by}={f_features[self._grouped_by]} {grouping_feat_size}"
                    )

                    # dato che devo stampare diverse curve nella stessa figura, non specifico una scala
                    self._add_curve(curve)

        if self._legend:
            self._add_summary_legend()

        return self._add_graphics()

    def plot_all(self, target_curves=False) -> "list[CustomFigure]":
        """
        Ritorna le figure di tutti i file contenuti nell'istanza
        """

        # caso 1 solo file -> ritorna una CustomFigure
        if len(self._curves) == 1:
            if target_curves:
                self.plot_targets()
            for f_features, f_curves in self._curves.expose_all:
                scales = Curve.get_curves_scales(*f_curves.values())
                for key, curve in f_curves.items():
                    curve = curve.__copy__()
                    curve.color = self._configs.colors[key] if self._colored else "black"
                    curve.linestyle = None if self._colored else self._configs.linestyles[key]
                    curve.width = 1
                    # nel caso di grafici di singoli file non ho bisogno di cambiare i marker, uso quelli di default
                    curve.markers = self._configs.default_marker
                    # il nome rimane quello già salvato nella curva
                    self._add_curve(curve, scales=scales)
                return [self._add_graphics(scales)]

        # caso più file -> lista di figure
        out = []
        for file_data in FileCurves.subdivide(self._curves):
            # creo istanze CustomFigure contenenti i dati di singoli file
            fig = CustomFigure(
                file_data,
                curves_to_plot=self._c_to_plot,
                plot_all_curves=self._all_c,
                legend=self._legend,
                colored=self._colored
            )
            out.extend(fig.plot_all())
        return out

    def plot_group_subsamples(self, *x_vals, target_subsamples=False) -> "CustomFigure":
        """
        Controlla che l'istanza contenga ai dati di un gruppo, e nel caso
        ritorna la figura dei sub-samples di tutte le curve,
        per le ascisse richieste

        Ritorna solo figure a colori
        """
        if not self._contains_group:
            raise ValueError(f"{self._curves} non contiene un gruppo")

        group_markers_dict = self._get_group_markers
        grouping_feat_size = self._get_group_feature_size
        if not group_markers_dict:
            raise ValueError(f"non sono stati definiti dei marker "
                             f"per il raggruppamento di file {self._file_type} "
                             f"sotto la feature {self._grouped_by}")

        colors_dict = self._configs.colors

        for f_features, f_curves in self._curves.expose_all:
            # f_features: dizionario delle features del file correntemente considerato
            # f_curves: dizionario delle curve contenute nel file

            for key, curve in f_curves.items():
                if key in self._c_to_plot or self._all_c:

                    sub_samples = curve.create_sub_sample(*x_vals)
                    # per ogni curva salviamo colore, linestyle, width e marker utilizzato e modifichiamo il nome
                    sub_samples.color = colors_dict[key]
                    sub_samples.linestyle = None
                    sub_samples.width = 0.75
                    # Prendo i marker dal dizionario dei config {feature_group:{feature_group_file:marker_value}}
                    # Es. {Vgf:{2:square}}
                    sub_samples.markers = group_markers_dict[f_features[self._grouped_by]]
                    sub_samples.name = (
                        f"{curve.name}, {self._grouped_by}={f_features[self._grouped_by]} {grouping_feat_size}"
                    )

                    # dato che devo stampare diverse curve nella stessa figura, non specifico una scala
                    self._add_scatter(sub_samples, mode="lines+markers", marker_size=3)

        if self._legend:
            self._add_summary_legend()

        if target_subsamples:
            self.plot_targets_subsamples(*x_vals)

        return self._add_graphics()

    def plot_all_subsamples(self, *x_vals, target_subsamples=False) -> "list[CustomFigure]":
        """
        Ritorna le figure dei sub-samples di tutti i file contenuti nell'istanza,
        per le ascisse richieste

        Ritorna solo figure a colori
        """
        # caso 1 solo file -> ritorna una CustomFigure
        if len(self._curves) == 1:
            colors_dict = self._configs.colors

            for f_features, f_curves in self._curves.expose_all:
                scales = Curve.get_curves_scales(*f_curves.values())
                sub_samples = {
                    c_id:c.create_sub_sample(*x_vals) for c_id,c in f_curves.items()
                }
                for key, curve in sub_samples.items():
                    curve = curve.__copy__()
                    curve.color = colors_dict[key]
                    curve.linestyle = None
                    curve.width = 1
                    curve.markers = None
                    # il nome rimane quello già salvato nella curva
                    self._add_scatter(curve, scales=scales, mode="lines")

                if target_subsamples:
                    self.plot_targets_subsamples(*x_vals)

                return [self._add_graphics(scales)]

        # caso più file -> lista di figure
        out = []
        for file_data in FileCurves.subdivide(self._curves):
            # creo istanze CustomFigure contenenti i dati di singoli file
            fig = CustomFigure(
                file_data,
                curves_to_plot=self._c_to_plot,
                plot_all_curves=self._all_c,
                legend=self._legend,
                colored=self._colored
            )
            if target_subsamples:
                fig.plot_targets()
            out.extend(fig.plot_all())
        return out

if __name__=='__main__':
    from pathlib import Path
    e = FileCurves.from_paths(
        Path(r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IDVD_TrapDistr_exponential_Vgf_-2_Es_0.2_Em_0.2.csv"),
        Path(r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IDVD_TrapDistr_exponential_Vgf_-1_Es_0.2_Em_0.2.csv"),
        Path(r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IDVD_TrapDistr_exponential_Vgf_0_Es_0.2_Em_0.2.csv"),
        Path(r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IDVD_TrapDistr_exponential_Vgf_1_Es_0.2_Em_0.2.csv"),
        Path(r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IDVD_TrapDistr_exponential_Vgf_2_Es_0.2_Em_0.2.csv")
    )
    e.get_grouping_feat()

    if e:
        prova_fig = CustomFigure(e)
        # prova_fig.plot_group_subsamples(0.4,3,10, target_subsamples=True)
        prova_fig.plot_group(target_curves=True)
        prova_fig.show()
