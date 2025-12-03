import pandas as pd
from app_resources.parameters import *

## CLASS ##
class AppCache:
    """
    Questa classe si occupa di contenere in un'istanza, definita di seguito,
    l'intera memoria chache dell'applicazione.

    Sono in aggiunta definiti metodi per la manipolazione dei dati utili
    in tutta l'applicazione.
    """
    configs = AppConfigs()

    file_types:list[str] = FileConfigs.supported_file_types()

    files_configs:dict[str,FileConfigs] = {}
    for file_type in file_types:
        files_configs[file_type] = FileConfigs(file_type)

    def __init__(self):
        self.index_data()

        self.indexes:dict[str, pd.DataFrame] = {}
        for file_type in self.file_types:
            try:
                self.indexes[file_type] = self.add_overall_aff(
                    pd.read_excel(self.configs.indexes_file,
                                  sheet_name=file_type)
                )   # aggiungo i df degli indici al dizionario (file_type:df)
            except Exception:
                raise FileNotFoundError(
                    f"""Non è stato possibile trovare il file di indicizzazione necessario
                    data_type specificato = {file_type}"""
                )

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
        if grouping_feature not in self.indexes[file_type].columns:
            raise ValueError(f"La feature di raggruppamento {grouping_feature} non appare tra quelle supportate")

        df = self.indexes[file_type]

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

    @staticmethod
    def index_data():
        """Richiama la funzione di indicizzazione sulla directory corretta"""
        from common import indexer
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


## classe tab
## attributi Figura e figura con target

## classe PlotChache oppure plotConfigs in AppCache

## INST ##

# Verrà istanziata la prima (e unica) volta che questo file viene importato.
# L'istanza è immediatamente disponibile per chiunque importi 'app_resources'.
# Nota: La classe AppCache contiene l'istanza di AppConfigs e le istanze di FileConfigs.
GLOBAL_CACHE = AppCache()
