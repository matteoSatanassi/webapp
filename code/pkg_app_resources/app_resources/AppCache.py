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
class TableCache:
    """
    La classe contiene tutti i dati e i metodi riguardanti le tabelle di indicizzazione,
    la loro manipolazione e il loro salvataggio in memoria
    """
    def __init__(self, file_type:str):
        if not file_type in ConfigCache.file_types:
            raise ValueError(f"File type {file_type} non riconosciuto")

        if not ConfigCache.app_configs.indexes_file.exists():
            self.index_data_dir()

        self.file_type = file_type
        try:
            self._table = self.add_overall_aff(
                pd.read_excel(ConfigCache.app_configs.indexes_file,
                              sheet_name=file_type)
            )
        except Exception as e:
            raise FileNotFoundError(f"la pagina {file_type} non è compare tra le disponibili") from e


    def _save_table(self):
        """Salva il df del file_type specificato nel file degli indici"""
        try:
            with pd.ExcelWriter(ConfigCache.app_configs.indexes_file) as writer:
                self._table.to_excel(writer, sheet_name=self.file_type, index=False)
        except Exception as e:
            raise Exception(f"Errore nel salvataggio della tabella {self.file_type}") from e
        print("Salvataggio riuscito")

    @property
    def table(self):
        return self._table.copy()

    # noinspection PyIncorrectDocstring
    def group_df(self,
                 grouping_feature: str,
                 only_df=False) -> tuple[pd.DataFrame, list[str]]:
        """
        Il metodo ritorna una copia del df degli indici del file_type specificato,
        raggruppato secondo la feature specificata, e la lista delle colonne da nascondere.

        La feature di raggruppamento sarà l'unica a variare tra le feature dei file raggruppati.

        :param only_df: Boolean, se True ritorna il solo df raggruppato, altrimenti anche
            la lista delle colonne da nascondere
        """
        if grouping_feature not in self._table.columns:
            raise ValueError(
                f"La feature di raggruppamento {grouping_feature} non appare tra quelle supportate"
            )

        df = self._table.copy()

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
        if ConfigCache.files_configs[self.file_type].targets_presents:
            for curve in ConfigCache.files_configs[self.file_type].allowed_curves:
                aff_col = f"aff_{curve}"
                if aff_col in df.columns:
                    df_out[aff_col] = groups[aff_col].mean().values
            df_out = self.add_overall_aff(df_out)

        if only_df:
            return df_out

        return df_out, list(cols_to_hide)

    def calculate_affinities(self) -> pd.DataFrame:
        """Dato un file_type, calcola le affinità delle
        curve indicizzate nella relativa tabella"""

        df = self._table

        feature_cols = [col for col in df.columns if "aff_" not in col]

        # carico il df in un'istanza FileCurves, in modo da calcolarmi le affinità
        data = FileCurves.from_df(df[feature_cols])

        # calcolo la overall affinity, se presente, e salvo il nuovo df in memoria
        df = self.add_overall_aff(
            pd.DataFrame(data.calculate_affinities(autosave=True))
        )
        df.loc[:,'file_path'] = df['file_path'].astype(str)

        self._table = df.copy()

        # salvo il nuovo df in memoria
        self._save_table()

        return self.table

    def get_table_no_aff(self)->pd.DataFrame:
        """
        Ritorna la tabella del file_type specificato senza le colonne delle affinità.

        Utile per le operazioni con FileCurves e FileFeatures.
        """

        df = self.table
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
        self.paths: str = None
        self._figure: CustomFigure = None
        self._figure_targets: CustomFigure = None
        self._used = self._figure

    @classmethod
    def from_path_col(cls, paths_val: FileCurves):
        """
        Dato un valore dalla colonna path della tabella di indexing,
        costruisce la corrispondente classe tab
        """
        data = FileCurves().from_paths(
            *TableCache.explode_group_paths(paths_val)
        )
        # controllo che i dati contengano un gruppo,
        # e nel caso aggiungo la feature di raggruppamento
        data.get_grouping_feat()

        if not data.contains_tab_data:
            raise ValueError(
                "L'oggetto passato come parametro non è applicabile ad un tab di visualizzazione"
            )

        inst = cls(data.file_type)
        inst.paths = paths_val
        inst._figure = plot_tab(data)
        inst._used = inst._figure

        return inst

    @property
    def label(self):
        """Ritorna la label del tab"""
        return self._figure.get_tab_label

    @property
    def value(self):
        """Ritorna il valore da dare al tab"""
        return self.paths

    @property
    def figure_with_targets(self):
        """Ritorna la figura caricata nell'istanza con le relative curve target"""
        if not ConfigCache.files_configs[self.file_type].targets_presents:
            print("I dati all'interno del tab non hanno dei valori target da visualizzare")
            return self._figure

        if not self._figure_targets:
            print("costruendo la figura con curve target")
            self._figure_targets = copy(self._figure).plot_targets()

        return self._figure_targets

    @property
    def figure(self):
        """Ritorna la figura del tab"""
        return self._used

    def switch_fig(self):
        """
        Metodo per modificare la figura visualizzata dal tab; se senza target, li stampa,
        altrimenti il contrario.

        L'attributo self._used punta alla figura utilizzata dall'istanza.
        """
        if self._used != self._figure:
            self._used = self._figure
        else:
            self._used = self.figure_with_targets
        return self

    def build_dcc_tab(self):
        """Costruisce l'oggetto dcc.Tab da utilizzare nell'applicazione"""
        return dcc.Tab(
            value=self.value,
            label=self.label,
            children=[
                dcc.Graph(id={'page': self.file_type, 'item': 'graph-tab', 'tab': self.value},
                          figure=self._used)
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
            pio.write_image(self._used,
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

    @property
    def tabs_values(self):
        """
        Generator function.

        Ritorna i valori dei tab con file_type specificato tra quelli salvati in memoria.
        """
        for tab_val in self._tabs.keys():
            yield tab_val


class AppCache(ConfigCache):
    """
    La classe si occupa di contenere le istanze di tutte le classi di cache mem.
    """

    tables = {file_type:TableCache(file_type) for file_type in ConfigCache.file_types}

    open_tabs = {file_type:OpenTabsCache(file_type) for file_type in ConfigCache.file_types}

    @staticmethod
    def explode_group_paths(string: str):
        """
        Data una stringa di indirizzi raggruppati, li esplode in una lista di oggetti Path

        Se la lista contiene un solo elemento ritorna cmq una lista con quell'unico elemento
        """
        return TableCache.explode_group_paths(string)

    @staticmethod
    def index_data_dir():
        """Richiama la funzione di indicizzazione sulla directory dei dati"""
        TableCache.index_data_dir()

    @staticmethod
    def find_export_path() -> Path:
        """
        Crea un indirizzo di esportazione valido
        :return: Indirizzo di esportazione creato
        :rtype: pathlib.Path
        """
        return SingleTabCache.find_export_path()

# classe PlotCache oppure plotConfigs in AppCache
# se la figura non ha targets modificare Tab


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
