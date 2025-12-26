"""
In questo modulo è definita la classe AppCache, che verrà usata per
costruire la cache dell'applicazione tramite instantiation
"""

from copy import copy
from pathlib import Path
from dash import dcc
import pandas as pd
import plotly.io as pio
from app_resources.parameters import ConfigCache
from common import *  # non è un wildcard import, mi serve tutto


## CLASS ##
class TablesCache:
    """
    La classe contiene tutti i dati e i metodi riguardanti le tabelle di indicizzazione,
    la loro manipolazione e il loro salvataggio in memoria
    """
    def __init__(self):

        self.index_data_dir()

        self._tables:dict[str,pd.DataFrame] = {}
        # file types non indicizzati nella data_dir corrente
        self._not_presents:set[str] = set()
        for file_type in ConfigCache.file_types:
            try:
                self._tables[file_type] = pd.read_excel(
                    ConfigCache.app_configs.indexes_file,
                    sheet_name=file_type)
            except Exception as e:
                print("\tErrore costruzione TablesCache\n"
                      f"\tfile_type: {file_type}\n"
                      f"\terror: {e}\n"
                )
                self._not_presents.add(file_type)

    @property
    def not_presents(self):
        """Ritorna un set dei file_type non indicizzati"""
        return self._not_presents

    def _save_tables(self):
        """Salva i df in memoria nel file di indicizzazione"""
        try:
            with pd.ExcelWriter(ConfigCache.app_configs.indexes_file) as writer:
                for file_type, table in self._tables.items():
                    table.to_excel(writer, sheet_name=file_type, index=False)
        except Exception as e:
            raise Exception("Errore nel salvataggio delle tabelle") from e
        print("Salvataggio riuscito")

    def get(self, file_type:str) -> pd.DataFrame:
        """Ritorna una copia della tabella del file_type specificato"""
        return self._tables[file_type].copy()

    # noinspection PyIncorrectDocstring
    def group_df(self,
                 file_type:str,
                 grouping_feature: str,
                 only_df=False):
        """
        Il metodo ritorna una copia del df degli indici del file_type specificato,
        raggruppato secondo la feature specificata, e la lista delle colonne da nascondere.

        La feature di raggruppamento sarà l'unica a variare tra le feature dei file raggruppati.

        :param only_df: Boolean, se True ritorna il solo df raggruppato, altrimenti anche
            la lista delle colonne da nascondere
        """
        if file_type not in self._tables:
            raise ValueError(f"File type {file_type} non esistente in memoria")

        if grouping_feature not in self._tables[file_type].columns:
            raise ValueError(
                f"La feature di raggruppamento {grouping_feature} non appare tra quelle supportate"
            )

        df:pd.DataFrame = self.get(file_type)

        # ricavo le colonne da nascondere
        cols_to_hide = set(self.cols_to_hide(df))
        cols_to_hide.add(grouping_feature)

        # Costruisco chiave del gruppo
        group_cols = [col for col in df.columns if col not in cols_to_hide and "aff_" not in col]
        df["group_key"] = df[group_cols].astype(str).agg("_".join, axis=1)

        # Raggruppo
        groups = df.groupby("group_key")

        # Prendo una riga per gruppo
        df_out = groups.first().reset_index(drop=True)

        # raggruppo gli indirizzi dei file del gruppo in un'unica stringa
        df_out["file_path"] = groups["file_path"].agg(lambda x: "#".join(map(str, x))).values

        # Calcolo medie delle colonne affinità se presenti
        if ConfigCache.files_configs[file_type].targets_presents:
            for curve in ConfigCache.files_configs[file_type].allowed_curves:
                aff_col = f"aff_{curve}"
                if aff_col in df.columns:
                    df_out[aff_col] = groups[aff_col].mean().values
            df_out = self.add_overall_aff(df_out)

        if only_df:
            return df_out

        return df_out, list(cols_to_hide)

    def calculate_affinities(self, file_type:str) -> pd.DataFrame:
        """Dato un file_type, calcola le affinità delle
        curve indicizzate nella relativa tabella"""

        df:pd.DataFrame = self._tables[file_type]

        feature_cols = [col for col in df.columns if "aff_" not in col]

        # carico il df in un'istanza FileCurves, in modo da calcolarmi le affinità
        data = FileCurves.from_df(df[feature_cols])

        # calcolo la overall affinity, se presente, e salvo il nuovo df in memoria
        df = self.add_overall_aff(
            pd.DataFrame(data.calculate_affinities(autosave=True))
        )
        df.loc[:,'file_path'] = df['file_path'].astype(str)

        self._tables[file_type] = df.copy()

        # salvo il nuovo df in memoria
        self._save_tables()

        return df

    def get_table_no_aff(self, file_type:str)->pd.DataFrame:
        """
        Ritorna una copia della tabella del file_type specificato
        senza le colonne delle affinità.

        Utile per le operazioni con FileCurves e FileFeatures.
        """

        df = self.get(file_type)
        allowed_cols = [col for col in df.columns if "aff_" not in col]

        return df[allowed_cols].reset_index(drop=True)

    @staticmethod
    def add_overall_aff(df: pd.DataFrame) -> pd.DataFrame:
        """
        Se il df contiene delle colonne di affinità, crea una colonna delle loro medie di riga,
        con nome "aff_tot", altrimenti ritorna il df senza modifiche
        """
        aff_cols = [col for col in df.columns if "aff_" in col]

        if not aff_cols:
            return df

        df["aff_tot"] = df[aff_cols].mean(axis=1, skipna=True)

        return df

    @staticmethod
    def cols_to_hide(df: pd.DataFrame) -> list[str]:
        """Ritorna la lista delle colonne da nascondere
        tra quelle della tabella passata come parametro"""
        return ["file_path", *df.columns[df.isna().all()].tolist()]

    @staticmethod
    def index_data_dir():
        """Richiama la funzione di indicizzazione sulla directory dei dati"""
        indexer(ConfigCache.app_configs.data_dir)

    @staticmethod
    def explode_group_paths(string: str):
        """
        Data una stringa di indirizzi raggruppati, li esplode in una lista di oggetti Path

        Se la lista contiene un solo elemento ritorna cmq una lista con quell'unico elemento
        """
        return [Path(p) for p in string.split('#')]


class SingleTabCache:
    """
    Le istanze costruite da questa classe conterranno i dati visualizzati nei tab
    dell'applicazione
    """

    def __init__(self, file_type):
        if file_type not in ConfigCache.file_types:
            raise ValueError(f"File type {file_type} non valido")

        self.file_type: str = file_type
        # il valore del tab sarà il valore della colonna file_path
        # della riga da cui è stato originato
        self.value: str = None
        self._figs: dict = {
            "figure":None,
            "figure+t":None,
            "samples":None,
            "samples+t":None,
        }
        self._x_vals: list[float] = []
        self._used:str = "figure"

    @classmethod
    def from_path_col(cls, paths_val:str):
        """
        Dato un valore dalla colonna path della tabella di indexing,
        costruisce la corrispondente classe tab
        """
        data = FileCurves().from_paths(
            *TablesCache.explode_group_paths(paths_val)
        )
        # controllo che i dati contengano un gruppo,
        # e nel caso aggiungo la feature di raggruppamento
        data.get_grouping_feat()

        if not data.contains_tab_data:
            raise ValueError(
                "L'oggetto passato come parametro non è applicabile ad un tab di visualizzazione"
            )

        inst = cls(data.file_type)
        inst.value = paths_val
        inst._figure = plot_tab(data)
        inst._used = "figure"

        return inst

    @property
    def _figure(self):
        return self._figs["figure"]
    @_figure.setter
    def _figure(self, value):
        self._figs["figure"] = value
    @property
    def _figure_targets(self):
        """Ritorna la figura caricata nell'istanza con le relative curve target"""
        if not ConfigCache.files_configs[self.file_type].targets_presents:
            print("I dati all'interno del tab non hanno dei valori target da visualizzare")
            return self._figure

        if not self._figs["figure+t"]:
            print("costruendo la figura con curve target")
            self._figs["figure+t"] = copy(self._figure).plot_targets()

        return self._figs["figure+t"]
    @property
    def _samples(self):
        """
        Ritorna la figura contenente i punti alle sole ascisse richieste,
        caricate nell'istanza, e la rende la figura utilizzata
        """
        if not self._x_vals:
            print("Non sono state specificate ascisse nell'istanza")
            print("Ritorno la figura standard")
            return self._figure

        if not self._figs["samples"]:
            self._figs["samples"] = CustomFigure.sub_samples_plot(self._figure, *self._x_vals)

        return self._figs["samples"]
    @property
    def _samples_targets(self):
        """Ritorna la figura caricata in subsamples con i relativi punti target"""
        if not self._x_vals:
            print("Non sono state specificate ascisse nell'istanza")
            print("Ritorno la figura standard")
            return self._figure

        if not ConfigCache.files_configs[self.file_type].targets_presents:
            print("I dati all'interno del tab non hanno dei valori target da visualizzare")
            return self._samples

        if not self._figs["samples+t"]:
            self._figs["samples+t"] = copy(self._samples).plot_targets_subsamples(*self._x_vals)

        return self._figs["samples+t"]

    @property
    def x_vals(self):
        """Ritorna le ascisse per cui voglio stampare i valori in figura"""
        return self._x_vals
    @x_vals.setter
    def x_vals(self, vals: list[float]):
        """Setter per modificare i valori delle ascisse"""
        if not vals:
            raise ValueError("Non sono state settate ascisse")

        if not all(isinstance(val, (float,int)) for val in vals):
            raise ValueError("I valori delle ascisse immesse non sono tutti numeri")

        if set(vals) == set(self._x_vals):
            return

        self._x_vals = vals
        self._figs["samples"] = None
        self._figs["sample+t"] = None

    @property
    def label(self):
        """Ritorna la label del tab"""
        return self._figure.get_tab_label
    @property
    def used(self):
        """Ritorna la figura utilizzata del tab"""
        match self._used :
            case "figure": return self._figure
            case "figure+t": return self._figure_targets
            case "samples": return self._samples
            case "samples+t": return self._samples_targets

        print("I dati all'interno della figura utilizzata non sono corretti")
        return self._figure

    def switch_char(self):
        """
        Scambia il grafico utilizzato dal tab, se "figure"
        passa a "samples" e viceversa, lasciando inalterata la
        parte della presenza dei target
        """
        if "figure" in self._used:
            self._used = self._used.replace("figure", "samples")
        elif "samples" in self._used:
            self._used = self._used.replace("samples", "figure")
        else:
            raise ValueError("I dati sulla figura usata all'interno del tab non sono corretti")
        return self

    def switch_target(self):
        """
        Metodo per scambiate la figura utilizzata tra con valori target e senza
        """
        if "+t" in self._used:
            self._used = self._used.replace("+t","")
        else:
            self._used += "+t"
        return self

    def build_dcc_tab(self):
        """Costruisce l'oggetto dcc.Tab da utilizzare nell'applicazione"""
        if self.file_type == "BarrAccOccupation":
            self.used.update_layout(
                xaxis=dict(
                    range=[-0.004, 0.02],    # Imposto l'intervallo iniziale per l'asse X
                    # Opzionale: disattiva il pulsante di autoscale (utile se vuoi bloccare lo zoom)
                    autorange=False
                ),
                yaxis=dict(
                    range=[-0.05, 1.05],   # Intervallo iniziale per l'asse Y
                    autorange=False
                )
            )
        return dcc.Tab(
            value=self.value,
            label=self.label,
            children=[
                dcc.Graph(id={'page': self.file_type, 'item': 'graph-tab', 'tab': self.value},
                          figure=self.used)
            ],
            style={'fontSize': 8, 'left-margin': '2px'},
        )

    def save_figure(self):
        """Salva la figura richiesta con i parametri passati in chiamata"""
        export_dir = self.find_export_path()
        export_path = (export_dir /
                       Path(
                           f"{self._figure.fig_stem}.{ConfigCache.app_configs.export_format}"
                       ))

        try:
            pio.write_image(self.used,
                            export_path,
                            format=ConfigCache.app_configs.export_format,
                            scale=ConfigCache.app_configs.dpi / 72)
        except Exception as e:
            raise e
        return True

    @staticmethod
    def find_export_path() -> Path:
        """
        Crea un indirizzo di esportazione valido
        :return: Indirizzo di esportazione creato
        :rtype: pathlib.Path
        """
        export_dir = ConfigCache.app_configs.export_dir
        i = 0
        while True:
            export_path = try_mkdir(export_dir / 'export' if i == 0 else export_dir / f'export-{i}')
            if export_path:
                return export_path
            i += 1


class OpenTabsCache:
    """La classe contiene i dati di tutti i tab aperti nell'applicazione"""
    def __init__(self, file_type:str):
        self.file_type: str = file_type
        self._tabs: dict[str,SingleTabCache] = {}

    @property
    def tabs_values(self):
        """
        Generator function.

        Ritorna i valori dei tab con file_type specificato tra quelli salvati in memoria.
        """
        for tab_val in self._tabs.keys():
            yield tab_val

    def tab(self, paths_val: str) -> "SingleTabCache":
        """
        Dato un valore contenuto nella colonna path di una tabella dell'applicazione,
        controlla che non sia già presente un valore in memoria, e in caso negativo lo crea
        """
        if paths_val not in self._tabs:
            self._tabs[paths_val] = SingleTabCache(self.file_type).from_path_col(paths_val)

        return self._tabs[paths_val]

    def del_tab(self, paths_val: str):
        """Elimina il tab relativo a path_vals"""
        if paths_val not in self._tabs:
            raise ValueError(f"Il tab {paths_val} non compare tra quelli aperti")
        del self._tabs[paths_val]

    def save_tab(self, paths_val: str):
        """
        Salva il tab relativo a paths_val
        """
        if paths_val not in self._tabs:
            raise ValueError(f"Il tab {paths_val} non compare tra quelli aperti")
        return self._tabs[paths_val].save_figure()

    def close_all_tabs(self):
        """Elimina tutti i tab aperti dalla memoria"""
        self._tabs = {}


class AppCache(ConfigCache):
    """
    La classe si occupa di contenere le istanze di tutte le classi di cache mem.
    """

    tables = TablesCache()

    open_tabs = {file_type:OpenTabsCache(file_type) for file_type in ConfigCache.file_types}

    @property
    def present_file_types(self):
        """Ritorna un set contenenti file_types per cui è stato possibile leggere i dati"""
        return self.file_types - self.tables.not_presents

    def refresh(self):
        """Richiama le operazioni di aggiornamento sugli attributi della classe"""

        self.tables = TablesCache()

        for tabs in self.open_tabs.values():
            tabs.close_all_tabs()

    @staticmethod
    def explode_group_paths(string: str):
        """
        Data una stringa di indirizzi raggruppati, li esplode in una lista di oggetti Path

        Se la lista contiene un solo elemento ritorna cmq una lista con quell'unico elemento
        """
        return TablesCache.explode_group_paths(string)

    @staticmethod
    def index_data_dir():
        """Richiama la funzione di indicizzazione sulla directory dei dati"""
        TablesCache.index_data_dir()

    @staticmethod
    def find_export_path() -> Path:
        """
        Crea un indirizzo di esportazione valido
        :return: Indirizzo di esportazione creato
        :rtype: pathlib.Path
        """
        return SingleTabCache.find_export_path()


## INST ##

# Verrà istanziata la prima (e unica) volta che questo file viene importato.
# L'istanza è immediatamente disponibile per chiunque importi 'app_resources'.
# Nota: La classe AppCache contiene l'istanza di AppConfigs e le istanze di FileConfigs.
GLOBAL_CACHE = AppCache()


## HELPER FUNCS ##
def try_mkdir(path: Path) -> Path:
    """
    Prova a creare la directory specificata
    :param path: indirizzo della directory da creare
    :type path: pathlib.Path
    :return: l'indirizzo della directory creata o None nel caso esistesse già
    :rtype: pathlib.Path or None
    :raises RuntimeError: Nel caso fosse impossibile creare la directory specificata
    """
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        return None
    except Exception as e:
        raise RuntimeError(f"Impossibile creare {path}") from e
    return path
