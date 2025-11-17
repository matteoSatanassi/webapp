from pathlib import Path
import numpy as np
import pandas as pd
from params import *

class FilesFeatures(object):
    def __init__(self):
        self.file_type = None
        self._data = []
        self._grouped_by = None

    @classmethod
    def from_path(cls, file_path:Path|str):
        if not Path(file_path).exists():
            raise FileNotFoundError(f'file {file_path} non trovato!')
        inst = cls()
        inst.file_type, data = cls.extract_features(file_path)
        inst._data.append(data)
        return inst
    @classmethod
    def from_df(cls, file_type:str, df:pd.DataFrame, grouped_by:str=None):
        file_type = file_type.upper()
        files_configs = load_files_info()

        if file_type not in files_configs:
            raise f"""
            Tipologia di file non supportata
            Tipologie supportate: {', '.join(files_configs.keys())} 
            """
        if df.columns != files_configs[file_type]["AllowedFeatures"].keys():
            raise f"""
            Le feature contenute nel df sono manchevoli o errate
            Feature presentate: {', '.join(df.columns)} 
            Feature supportate: {', '.join(files_configs[file_type]["AllowedFeatures"].keys())} 
            """

        if grouped_by is not None:
            if grouped_by not in df.columns:
                raise f"Feature di raggruppamento non supportata"

        try:
            df["file_path"] = df["file_path"].astype(Path)
        except:
            raise f"Non è stato possibile convertire in indirizzi la colonna del dataframe"

        inst = cls()
        inst.file_type, inst._data = file_type, df.to_dict(orient='records')
        return inst

    @staticmethod
    def extract_features(file_path:Path|str):
        """
        Dato un path, controlla che il file sia di un tipo supportato,
        e in caso positivo estrae le feature contenute nel nome.
        Ritorna la tipologia di file seguita dal dizionario delle feature estratte.
        """
        file_name = Path(file_path).stem
        file_features = file_name.split('_')
        file_type = file_features[0].upper()
        try:
            files_configs = load_files_info()[file_type]
        except:
            raise f"Non è stato possibile processare il file {file_path}"
        else:
            dict_features = {key:None for key in files_configs["AllowedFeatures"].keys()}
            for feature,f_type in files_configs["AllowedFeatures"].items():
                if feature=='file_path':
                    dict_features[feature] = Path(file_path)
                elif feature in file_features:
                    feature_val = file_features[file_features.index(feature)+1]
                    dict_features[feature] = feature_val if f_type=='text' else (
                        pd.to_numeric(feature_val, downcast=f_type))

            return file_type, dict_features

    def __str__(self):
        if not self.file_type:
            return ""
        else:
            stems = [row["file_path"].stem for row in self._data]
            return ", ".join(stems)


if __name__ == '__main__':
    path = r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IdVd_exponential_Vgf_0_Es_0.2_Em_0.2.csv"
    prova = FilesFeatures.from_path(path)
    print(prova)

