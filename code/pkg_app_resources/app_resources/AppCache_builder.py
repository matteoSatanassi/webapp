import pandas as pd
from app_resources.parameters import *

## CLASS ##
class AppCache:
    """
    Questa classe si occupa di contenere in un'istanza, definita di seguito,
    l'intera memoria cache dell'applicazione.

    Sono in aggiunta definiti metodi per la manipolazione dei dati utili
    in tutta l'applicazione.
    """
    configs = AppConfigs()

    file_types:list[str] = FileConfigs.supported_file_types()

    files_configs:dict[str,FileConfigs] = {}

    from dash import dcc

    for file_type in file_types:
        files_configs[file_type] = FileConfigs(file_type)

    def __init__(self):
        self.index_data()

        self.tables:dict[str, pd.DataFrame] = {}
        for file_type in self.file_types:
            try:
                self.tables[file_type] = self.add_overall_aff(
                    pd.read_excel(self.configs.indexes_file,
                                  sheet_name=file_type)
                )   # aggiungo i df degli indici al dizionario (file_type:df)
            except Exception:
                raise FileNotFoundError(
                    f"""Non è stato possibile trovare il file di indicizzazione necessario
                    data_type specificato = {file_type}"""
                )
        
        self._open_tabs:dict[str,Tab] = {}

    def tab(self, paths_val:str) -> "Tab":
        """
        Dato un valore contenuto nella colonna path di una tabella dell'applicazione,
        controlla che non sia già presente un valore in memoria, e in caso negativo lo crea
        """
        if paths_val not in self._open_tabs:
            self._open_tabs[paths_val] = Tab().from_path_col(paths_val)
        
        return self._open_tabs[paths_val]
    def del_tab(self, paths_val:str):
        """Elimina il tab relativo a path_vals"""
        if paths_val not in self._open_tabs:
            raise ValueError(f"Il tab {paths_val} non compare tra quelli aperti")
        del self._open_tabs[paths_val]
    def save_tab(self, paths_val:str):
        """
        Salva il tab relativo a paths_val
        """
        if paths_val not in self._open_tabs:
            raise ValueError(f"Il tab {paths_val} non compare tra quelli aperti")
        return self._open_tabs[paths_val].save_figure()

    # noinspection PyIncorrectDocstring
    def group_df(self,
                 file_type:str,
                 grouping_feature:str,
                 only_df=True) -> tuple[pd.DataFrame,list[str]]:
        """
        Il metodo ritorna il df degli indici del file_type specificato raggruppato secondo
        la feature specificata e la lista delle colonne da nascondere.

        La feature di raggruppamento sarà l'unica a variare tra le feature dei file raggruppati.

        :param only_df: Boolean, se True ritorna il solo df raggruppato, altrimenti anche
            la lista delle colonne da nascondere
        """
        if not file_type in self.file_types:
            raise ValueError(f"File type {file_type} non trovato tra i file_types supportati")
        if grouping_feature not in self.tables[file_type].columns:
            raise ValueError(f"La feature di raggruppamento {grouping_feature} non appare tra quelle supportate")

        df = self.tables[file_type]

        # ricavo le colonne da nascondere
        cols_to_hide = self.cols_to_hide(df).append(grouping_feature)

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
        if self.files_configs[file_type].targets_presents:
            for curve in self.files_configs[file_type].allowed_curves:
                aff_col = f"aff_{curve}"
                if aff_col in df.columns:
                    df_out[aff_col] = groups[aff_col].mean().values
            df_out = self.add_overall_aff(df_out)

        if only_df:
            return df_out

        return df_out, cols_to_hide
    def calculate_affinities(self, file_type:str)->pd.DataFrame:
        if file_type not in self.tables:
            raise ValueError(f"Il file type {file_type} non corrisponde a nessuna tabella in memoria")

        from common import FileCurves

        df = self.tables[file_type]

        feature_cols = [col for col in df.columns if "aff_" not in col]

        # carico il df in un'istanza FileCurves, in modo da calcolarmi le affinità
        data = FileCurves.from_df(df[feature_cols])

        # calcolo la overall affinity, se presente, e salvo il nuovo df in memoria
        df = self.add_overall_aff(
            pd.DataFrame(data.calculate_affinities(autosave=True))
        )
        df['file_path'] = df['file_path'].astype(str)

        # salvo il nuovo df in memoria
        self._save_table(file_type)

        return df
    def _save_table(self, file_type:str):
        """Salva il df del file_type specificato nel file degli indici"""
        try:
            with pd.ExcelWriter(self.configs.indexes_file) as writer:
                self.tables[file_type].to_excel(writer, sheet_name=file_type, index=False)
        except Exception as e:
            print("Errore in save_table")
            raise e
        else:
            print("Salvataggio riuscito")

    @staticmethod
    def index_data():
        """Richiama la funzione di indicizzazione sulla directory corretta"""
        from common.indexer import indexer
        indexer(AppCache.configs.data_dir)
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
        return ["file_path", *df.columns[df.isna().all()].tolist()]
    @staticmethod
    def explode_group_paths(string: str):
        """
        Data una stringa di indirizzi raggruppati, li esplode in una lista di oggetti Path

        Se la lista contiene un solo elemento ritorna cmq una lista con quell'unico elemento
        """
        from pathlib import Path
        return [Path(p) for p in string.split('#')]
    @staticmethod
    def find_export_path() -> Path:
        """
        Crea un indirizzo di esportazione valido
        :return: Indirizzo di esportazione creato
        :rtype: pathlib.Path
        """
        export_dir = AppCache.configs.export_dir
        i = 0
        while True:
            export_path = try_mkdir(export_dir / 'export' if i == 0 else export_dir / f'export-{i}')
            if export_path:
                return export_path
            i += 1

class Tab:
    from common import FileCurves
    from pathlib import Path

    def __init__(self):
        from common import CustomFigure

        self.paths:str = None
        self._figure:CustomFigure = None
        self._figure_targets:CustomFigure = None
        self._used = self._figure

    @classmethod
    def from_path_col(cls, paths_val:FileCurves):
        """Dato un valore dalla colonna path della tabella di indexing, costruisce la corrispondente classe tab"""
        from common import FileCurves, plot_tab

        data = FileCurves().from_paths(
            AppCache.explode_group_paths(paths_val)
        )
        # controllo che i dati contengano un gruppo, e nel caso aggiungo la feature di raggruppamento
        data.get_grouping_feat()

        if not data.contains_tab_data:
            raise ValueError("L'oggetto passato come parametro non è applicabile ad un tab di visualizzazione")

        inst = cls()
        inst.paths = paths_val
        inst._figure = plot_tab(data)

        return inst

    @property
    def label(self):
        return self._figure.get_tab_label()
    @property
    def value(self):
        return self.paths
    @property
    def figure_with_targets(self):
        if not self._figure_targets:
            self._figure_targets = self._figure.__copy__().plot_targets()

        return self._figure_targets

    def use_targets(self, choice=True):
        """
        Metodo per decidere quale delle due figure ritornare nel tab o durante l'esportazione

        L'attributo self._used punta alla figura utilizzata dall'istanza
        """
        if choice:
            self._used = self.figure_with_targets()
        else:
            self._used = self._figure
        return self

    def build_dcc_tab(self):
        """Costruisce l'oggetto dcc.Tab da utilizzare nell'applicazione"""
        from dash import dcc
        
        return dcc.Tab(
            value=self.value,
            label=self.label,
            children=dcc.Graph(figure=self._used),
            style={'fontSize': 8, 'left-margin': '2px'},
        )

    def save_figure(self):
        """Salva la figura richiesta con i parametri passati in chiamata"""
        import plotly.io as pio

        export_dir = AppCache.find_export_path()
        export_path = export_dir / Path(f"{self._figure.fig_stem}.{AppCache.configs.export_format}")

        try:
            pio.write_image(self._used,
                            export_path,
                            format=AppCache.configs.export_format,
                            scale=AppCache.configs.dpi / 72)
        except Exception as e:
            raise e
        else:
            return True


# classe PlotCache oppure plotConfigs in AppCache

## HELPER FUNCS ##
def try_mkdir(path:Path)->Path:
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
    except:
        raise RuntimeError(f"Impossibile creare {path}")
    return path
