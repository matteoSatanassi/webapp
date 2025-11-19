from pathlib import Path
import numpy as np
import pandas as pd
from params import *

class FilesFeatures(object):
    """
    Classe preposta a contenere i dati relativi a un file dati o
    a un gruppo di file dati
    """
    __slots__ = ('file_type', '_data', 'grouped_by')
    def __init__(self):
        self.file_type = None
        self._data = []
        # self._grouped_by : creato solo in caso di bisogno

    def __str__(self):
        if not self.file_type:
            return ""
        else:
            stems = [row["file_path"].stem for row in self._data]
            return ", ".join(stems)

    @classmethod
    def from_path(cls, file_path:Path|str):
        if not Path(file_path).exists():
            raise FileNotFoundError(f'file {file_path} non trovato!')
        inst = cls()
        inst.file_type, data = cls.extract_features(file_path)
        inst._data.append(data)
        return inst
    @classmethod
    def from_df(cls, df:pd.DataFrame, grouped_by:str=None):
        try:
            file_path_col = df["file_path"].tolist()
        except KeyError:
            raise "Colonna file_path inesistente"
        if len(
                set([FilesFeatures.extract_features(file_path, only_file_type=True) for file_path in file_path_col])
        ) != 1:
            raise "I file passati non sono parte dello stesso file_type"
        else:
            file_type = FilesFeatures.extract_features(file_path_col[0], only_file_type=True)

        type_configs = cls.get_type_configs(file_type)

        if df.columns.tolist() != type_configs["AllowedFeatures"].keys():
            raise f"""
            Le feature contenute nel df sono manchevoli o errate
            Feature presentate: {', '.join(df.columns)} 
            Feature supportate: {', '.join(type_configs["AllowedFeatures"].keys())} 
            """

        try:
            df["file_path"] = df["file_path"].astype(Path)
        except:
            raise f"Non è stato possibile convertire in indirizzi la colonna del dataframe"

        inst = cls()
        if grouped_by is not None:
            if grouped_by not in df.columns:
                raise f"Feature di raggruppamento non supportata"
            inst.grouped_by = grouped_by

        inst.file_type, inst._data = file_type, df[type_configs["AllowedFeatures"].keys()].to_dict(orient='records')
        return inst

    @staticmethod
    def extract_features(file_path:Path|str, only_file_type = False):
        """
        Dato un path, controlla che il file sia di un tipo supportato,
        e in caso positivo estrae le feature contenute nel nome.
        Ritorna la tipologia di file seguita dal dizionario delle feature estratte.
        Nel caso only_file_type sia True, ritorna solo la tipologia di file, dopo aver controllato sia supportata
        """
        file_name = Path(file_path).stem
        file_features = file_name.split('_')
        file_type = file_features[0].upper()

        type_configs = FilesFeatures.get_type_configs(file_type)

        if only_file_type:
            return file_type
        dict_features = {key:None for key in type_configs["AllowedFeatures"].keys()}
        for feature,f_type in type_configs["AllowedFeatures"].items():
            if feature=='file_path':
                dict_features[feature] = Path(file_path)
            elif feature in file_features:
                feature_val = file_features[file_features.index(feature)+1]
                dict_features[feature] = feature_val if f_type=='text' else (
                    pd.to_numeric(feature_val, downcast=f_type))

        return file_type, dict_features
    @staticmethod
    def get_type_configs(file_type:str):
        try:
            return load_files_info()[file_type]
        except KeyError:
            raise f"""
            Tipologia di file non supportata {file_type}
            Tipologie supportate: {', '.join(load_files_info().keys())}
            Aggiungere alle specifiche
            """
        except Exception as error:
            raise f"Errore nella lettura del file file_params.json: {error}"


class Curve(object):
    """
    Identifica una singola curva

    :param name: Nome della curva
    :type name: str
    """
    __slots__ = ('X', 'Y', 'name')
    def __init__(self, name:str):
        self.name:str = name
        self.X: np.ndarray = None
        self.Y: np.ndarray = None
    def __str__(self):
        return self.name
    @property
    def integral(self)->float:
        """Integra la curva caricata nell'istanza"""
        return np.trapezoid(self.Y, self.X)
    def integral_affinity(self, curve:'Curve')->float:
        """calcola il rapporto di affinità tra l'istanza e un'altra curva"""
        target_area = curve.integral
        return max(1-abs(self.integral-target_area)/abs(target_area),0)
    def sort(self)->None:   #
        """
        Ordina gli array delle coordinate in modo crescente, rispetto alle ordinate
        """
        i_sorted = np.argsort(self.X)
        self.X = self.X[i_sorted]
        self.Y = self.Y[i_sorted]
        return None
    def translate_till_left(self):
        """
        Trasla la curva in modo che il valore più alto sia 0
        Utile per le curve di occupazione delle trappole, per avere la conduction band a 0
        """
        self.X -= self.X[-1]
        return None


class FileCurves(FilesFeatures):
    """
    Classe contenete i dati e le curve di un file dati o di un gruppo di file dati
    """
    def __init__(self):
        super().__init__()
        self._curves = []
    @classmethod
    def from_path(cls, file_path:Path|str)->"FileCurves":
        """crea un'istanza della classe e importa i dati a partire dall'indirizzo del file corrispondente"""
        inst = super(FileCurves, cls).from_path(file_path)
        inst.import_all()
        return inst
    @classmethod
    def from_df(cls, df:pd.DataFrame, grouped_by:str=None)->"FileCurves":
        """crea un'istanza della classe e importa i dati a partire da un dataframe contenente le feature"""
        inst = super(FileCurves, cls).from_df(df, grouped_by)
        inst.import_all()
        return inst
    @property
    def allowed_curves(self):
        """
        Ritorna un dizionario delle curve consentite nei file del tipo dell'istanza
        il dizionario ha una struttura del tipo {acronimo:label}
        """
        return FilesFeatures.get_type_configs(self.file_type)["AllowedCurves"]
    def import_all(self):
        """importa i dati dei file contenuti nell'istanza, salvandoli nell'attributo curves"""
        for file in self._data:
            self._curves += self.import_file_data(file["file_path"])
    def import_file_data(self, file_path:Path|str):
        """
        Importa i dati del file passato come variabile al metodo
        I dati sono presentati in seguito come un dizionario di oggetti Curve
        """
        allowed_curves = self.allowed_curves
        curves = {}
        try:
            data = pd.read_csv(file_path)
            data.replace("-", "0", inplace=True)

            for col in data.columns:
                name, axis = col.split(' ')  # [curve_name X/Y]

                if self.file_type == 'TRAPDATA' and name != 'trap_density':
                    _, _, _, name = name.split('_')  # ['trapped', 'charge', 'density', str_pos]

                if name in allowed_curves:
                    if name not in curves:
                        curves[name] = Curve(allowed_curves[name])

                    match axis:
                        case 'X':
                            curves[name].X = data[col].to_numpy(dtype=float)
                        case 'Y':
                            curves[name].Y = data[col].to_numpy(dtype=float)

            for _,curve in curves.items():
                curve.sort()
                if self.file_type == 'TRAPDATA': curve.translate_till_left()

        except Exception as error:
            raise f"errore leggendo il file {file_path}: \n\t{error}"
        else:
            return curves
    @staticmethod
    def find_target_file(file_type, file_features:dict):
        """Trova il file target corretto tra tutti quelli in cartella e ritorna un'istanza FileCurves contenente i dati"""
        type_configs = FileCurves.get_type_configs(file_type)
        try:
            target_files = (assets_dir / file_type).glob("*.csv")  # cartella file target
        except FileNotFoundError:
            raise "Cartella curve target non trovata"
        else:
            target_features = [f"{f}_{file_features[f]}" for f in type_configs["TargetFeatures"]]
            for t_file in target_files:
                if all(f in t_file for f in target_features):
                    return FileCurves().from_path(t_file)
            raise f"Non è stato possibile trovare il file target per le curve del file {file_features["file_path"].stem}"
    def calculate_affinities(self):
        """
        Calcola le affinità delle curve contenute nei file definiti nell'istanza.
        Nel caso il calcolo dell'affinità non sia supportato per i file del tipo caricati nell'istanza, non ritorna nulla
        :return: Dizionario del tipo {file_path:{curve_acronym:curve_affinity}}
        """
        type_configs = self.get_type_configs(self.file_type)

        if type_configs["TargetCurves"]==0:
            print("Questa tipologia di file non supporta il calcolo delle affinità")
            return None

        affinities = {}
        for file,curves in zip(self._data, self._curves):

            target = self.find_target_file(self.file_type, file)

            for name,curve in curves.items():
                affinities[file["file_path"]][name] = curve.calculate_affinity(target._curves[name])

        return affinities


if __name__ == '__main__':
    path = r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IdVd_TrapDistr_exponential_Vgf_0_Es_0.2_Em_0.2.csv"
    # prova = FileCurves.from_path(path)
    # print(prova)
    print("Vgf" in path)