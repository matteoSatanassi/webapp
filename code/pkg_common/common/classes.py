from pathlib import Path
from typing_extensions import Any, Generator
import numpy as np
import pandas as pd
from params import *

## CLASSES ##
class FilesFeatures(object):
    """
    Classe preposta a contenere i dati relativi a un file dati o
    a un gruppo di file dati
    """
    __slots__ = ('file_type', '_data', 'grouped_by')
    def __init__(self):
        self.file_type:str = None
        self._data:list[dict[str,Any]] = []
        self.grouped_by:str|None = None

    def __str__(self):
        if not self.file_type:
            return ""
        else:
            stems = [row["file_path"].stem for row in self._data]
            return ", ".join(stems)
    def __len__(self):
        return len(self._data)

    @classmethod
    def from_paths(cls, *args, grouping_feature=None):
        if not all(isinstance(arg,(Path,str)) for arg in args):
            raise TypeError("I valori passati al costruttore non sono tutti stringhe o paths")

        inst = cls()
        inst.file_type = cls.extract_features(Path(args[0]), only_file_type=True)
        for arg in set(args):

            if not Path(arg).exists():
                raise FileNotFoundError(f'file {arg} non trovato!')

            file_type, data = cls.extract_features(arg)

            if file_type != inst.file_type:
                raise ValueError(f"Il file {arg} non è dello stesso tipo dei precedenti ({inst.file_type})")

            inst._data.append(data)

        if grouping_feature:
            inst.grouped_by = grouping_feature

            if not inst.contains_group:
                return ValueError("Il gruppo di file passati non fanno parte dello stesso raggruppamento")

        return inst
    @classmethod
    def from_df(cls, df: pd.DataFrame, grouped_by: str = None):
        try:
            file_path_col = df["file_path"].tolist()
        except KeyError:
            raise KeyError("Colonna file_path inesistente")
        if len(
                set([FilesFeatures.extract_features(file_path, only_file_type=True) for file_path in file_path_col])
        ) != 1:
            raise ValueError("I file passati non sono parte dello stesso file_type")
        else:
            file_type = FilesFeatures.extract_features(file_path_col[0], only_file_type=True)

        type_configs = FilesFeatures.get_type_configs(file_type)

        if set(df.columns.tolist()) != set(type_configs["AllowedFeatures"].keys()):
            raise ValueError(f"""
                Le feature contenute nel df sono manchevoli o errate
                Feature presentate: {', '.join(df.columns)} 
                Feature supportate: {', '.join(type_configs["AllowedFeatures"].keys())} 
                """)

        try:
            df["file_path"] = df["file_path"].apply(lambda p: Path(p))
        except:
            raise ValueError("Non è stato possibile convertire in indirizzi la colonna file_path del dataframe")

        inst = cls()
        if grouped_by is not None:
            if grouped_by not in df.columns:
                raise ValueError(f"Feature di raggruppamento non supportata")
            inst.grouped_by = grouped_by

        inst.file_type, inst._data = file_type, df[type_configs["AllowedFeatures"].keys()].to_dict(orient='records')
        return inst

    @property
    def contains_group(self):
        """Ritorna True se i file formano effettivamente un gruppo omogeneo"""
        if self.grouped_by is None or len(self) <= 1:
            return False

        df_data = pd.DataFrame(self._data)

        # tutte le colonne tranne quella di raggruppamento e quelle vuote
        other_cols = [c for c in df_data.columns if c not in
                      (self.grouped_by,"file_path", *df_data.columns[df_data.isna().all()].tolist())]

        # ogni colonna deve avere un solo valore distinto
        return all(df_data[col].nunique() == 1 for col in other_cols)
    @property
    def paths(self) -> Generator[Path, None, None]:
        """Ritorna un generator con tutti i path contenuti nell'istanza"""
        for f_features in self._data:
            yield f_features["file_path"]
    @property
    def get_group_stem(self) -> str|None:
        """Se l'istanza contiene un gruppo, ritorna il nome del gruppo"""
        if self.contains_group:
            return (self._data[0]["file_path"].stem
                    .replace(f"{self.grouped_by}_{self._data[0][self.grouped_by]}_", ""))
        else:
            return None

    def get_tab_label(self):
        if not len(self)==1 and not self.contains_group:
            raise ValueError(f"L'oggetto non è applicabile ad un tab di visualizzazione")

        prefix = "GROUP" if self.contains_group else "FILE"

        features = self._data[0].copy()
        del features["file_path"]
        if self.grouped_by:
            del features[self.grouped_by]

        vals = [str(v) if v is not None else "." for v in features.values()]

        return f"{prefix} {self.file_type} - {"/".join(vals)}"
    def divide_in_groups(self, grouping_feat:str) -> Generator["FilesFeatures"]:
        """
        Il metodo, dato un oggetto FileFeatures contenente i dati di una certa quantità di file,
        divide il dataset in una lista di oggetti dello stesso tipo, ognuno contenente un solo gruppo di file

        NB - con gruppo si intende un dataset in cui i file hanno tutti stesse feature, a meno
        della grouping feature
        """
        if (not len(self)>1) or self.contains_group:
            raise ValueError("L'istanza non è divisibile in sottogruppi")
        if grouping_feat not in self._data[0].keys():
            raise ValueError(f"{grouping_feat} non è tra le feature presenti")

        df = pd.DataFrame(self._data)

        # raggruppo il df in gruppi con colonne tutte uguali tranne grouping_feat
        other_cols = [col for col in df.columns if col!=grouping_feat and col!="file_path"]
        grouped = df.groupby(other_cols, dropna=False)

        for _, group_df in grouped:
            # crea nuova istanza
            inst = type(self)()  # mantiene la sottoclasse corretta (posso chiamare anche da sottoclassi)
            inst.file_type = self.file_type
            inst.grouped_by = grouping_feat
            inst._data = group_df.to_dict(orient="records")
            yield inst
    def paths_list(self)->list[Path]:
        return [p for p in self.paths]
    def get_grouping_feat(self)->bool:
        """
        Il metodo, data un'istanza contenete i dati di più file, controlla
        se sono o no parte dello stesso raggruppamento, e nel caso aggiorna
        l'attributo grouped_by

        :return: False se non contiene nessun gruppo, True altrimenti
        """
        if not len(self)>1:
            return False

        data = pd.DataFrame(self._data)

        # Trova tutte le colonne che cambiano almeno una volta
        variable_cols = [
            col for col in data.columns
            if data[col].nunique() > 1 and col!="file_path"
        ]

        # Se ci sono 0 o più di 1 colonne variabili ⇒ NON è un grouping valido
        if len(variable_cols) != 1:
            return False

        # Altrimenti quella è la grouping feature
        self.grouped_by = variable_cols[0]
        return True

    @staticmethod
    def extract_features(file_path:Path|str, only_file_type = False):
        """
        Dato un path, controlla che il file sia di un tipo supportato,
        e in caso positivo estrae le feature contenute nel nome.

        Ritorna la tipologia di file seguita dal dizionario di tutte le feature
        specificate per il corrispondente file_type. Le feature senza nessun valore
        specificato nel nome, avranno valore None.

        Nel caso only_file_type sia True, ritorna solo la tipologia di file,
        dopo aver controllato sia supportata.
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
                dict_features[feature] = feature_val if f_type=='text' else round(
                    pd.to_numeric(feature_val, downcast=f_type, ), 2
                )

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
    def __init__(self, name:str):
        self.name:str = name
        self.X: np.ndarray = None
        self.Y: np.ndarray = None
    def __str__(self):
        return self.name
    def __copy__(self):
        copy = type(self)(self.name)
        copy.X = self.X
        copy.Y = self.Y
        return copy

    @property
    def y_scale(self):
        """Ritorna la scala delle ordinate della curva"""
        return self.get_data_scale(self.Y)
    @property
    def x_scale(self):
        """Ritorna la scala delle ascisse della curva"""
        return self.get_data_scale(self.X)
    @property
    def integral(self)->float:
        """Integra la curva caricata nell'istanza"""
        return np.trapezoid(self.Y, self.X)

    def sort(self)->None:   #
        """
        Ordina gli array delle coordinate in modo crescente, rispetto alle ordinate
        """
        i_sorted = np.argsort(self.X)
        self.X = self.X[i_sorted]
        self.Y = self.Y[i_sorted]
        return None
    def integral_affinity(self, curve:'Curve')->float:
        """calcola il rapporto di affinità tra l'istanza e un'altra curva"""
        target_area = curve.integral
        return max(1-abs(self.integral-target_area)/abs(target_area),0)
    def translate_till_left(self):
        """
        Trasla la curva in modo che il valore più alto sia 0
        Utile per le curve di occupazione delle trappole, per avere la conduction band a 0
        """
        self.X -= self.X[-1]
        return None

    @staticmethod
    def get_data_scale(values:np.ndarray)->float:
        """Ritorna la scala dei dati contenuti in un array numpy"""
        max_val = np.nanmax(np.abs(values))
        if max_val == 0:
            return 0
        exponent = int(np.floor(np.log10(max_val)))
        # esponente arrotondato alla decade (1e13 → 13)
        return exponent
    @staticmethod
    def get_curves_scales(*args:"Curve")->dict[str,float]:
        """
        Ritorna le scale di ordinate e ascisse del gruppo di curve passato come argomento
        :return: Dizionario del tipo {"X":x_scale, "Y":y_scale}
        """
        if all(isinstance(arg, Curve) for arg in args):
            return {
                "X": max(arg.x_scale for arg in args),
                "Y": max(arg.y_scale for arg in args),
            }
        raise ValueError("Gli argomenti passati non erano tutte istanze della classe Curve")


class FileCurves(FilesFeatures):
    """
    Classe contenete i dati e le curve di un file dati o di un gruppo di file dati
    """
    __slots__ = ('file_type', '_data', 'grouped_by', '_curves')
    def __init__(self):
        super().__init__()
        self._curves:dict[str,dict[str,Curve]] = {}

    def _validate(self):
        """
        Verifica che l'istanza sia contenga dati corretti.
        In caso positivo ritorna l'istanza.

        Controlla che il numero di file e di curve sia equivalente e che tutti i dati delle curve
        abbiano un file corrispondente.
        """
        if not len(self._curves)==len(self._data):
            raise ValueError("I numeri di curve e di file salvati nell'istanza non uguali")

        if set(self._curves.keys()) != set(self.paths):
            raise ValueError(f"Inconsistenza tra dati e curve")

        return self

    @classmethod
    def _from_super(cls, data:FilesFeatures)-> "FileCurves":
        if not isinstance(data,FilesFeatures):
            return ValueError("L'argomento passato non è del tipo FileFeatures")
        inst = cls()
        inst.file_type = data.file_type
        inst.grouped_by = data.grouped_by
        inst._data = data._data
        return inst.import_all()._validate()
    # noinspection PyUnresolvedReferences,PyProtectedMember
    @classmethod
    def from_paths(cls, *args, grouping_feature=None)-> "FileCurves":
        """crea un'istanza della classe e importa i dati a partire dall'indirizzo del file corrispondente"""
        return cls._from_super(
            super().from_paths(*args, grouping_feature=grouping_feature)
        )
    # noinspection PyUnresolvedReferences,PyProtectedMember
    @classmethod
    def from_df(cls, df: pd.DataFrame, grouped_by: str = None) -> "FileCurves":
        """crea un'istanza della classe e importa i dati a partire da un dataframe contenente le feature"""
        return cls._from_super(
            super().from_df(df, grouped_by)
        )

    @property
    def allowed_curves(self):
        """
        Ritorna un dizionario delle curve consentite nei file del tipo dell'istanza
        il dizionario ha una struttura del tipo {acronimo:label}
        """
        return self.get_type_configs["AllowedCurves"]
    @property
    def get_type_configs(self):
        """Ritorna i file_type config relativi all'istanza corrente"""
        return FilesFeatures.get_type_configs(self.file_type)
    @property
    def expose_all(self):
        """
        Ritorna dati e curve contenute nell'istanza di classe
        :return: generator function che ritorna {file_features_dict, file_curves_dict}
        per ogni dato salvato nell'istanza
        """
        self._validate()
        for f in self._data:
            curves = self._curves.get(f["file_path"])
            yield f, curves
    # noinspection PyUnboundLocalVariable
    @property
    def subdivide(self):
        """Ritorna una lista di oggetti FileCurves, ognuno contenente solo i dati di un file"""
        self._validate()
        for f in self._data:
            instance = FileCurves()
            instance.file_type = self.file_type
            instance._data = [f]
            instance._curves = {f["file_path"]: self._curves[f["file_path"]]}
            yield instance

    def import_all(self):
        """importa i dati dei file contenuti nell'istanza, salvandoli nell'attributo curves"""
        for path in self.paths:
            self._curves[path] = self.import_file_data(path)
        return self
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
    def calculate_affinities(self, autosave=False):
        """
        Calcola le affinità delle curve contenute nei file definiti nell'istanza.
        Nel caso il calcolo dell'affinità non sia supportato per i file del tipo
        caricati nell'istanza, non ritorna nulla.

        :param autosave: Nel caso sia True (default False), i dati delle affinità calcolati
            sono salvati direttamente nell'attributo _data dell'istanza, e il metodo ritorna
            appunto quell'attributo
        :return: Dizionario del tipo {file_path:{curve_acronym:curve_affinity}}
        """
        if self.get_type_configs["TargetCurves"]==0:
            print("Questa tipologia di file non supporta il calcolo delle affinità")
            return None

        if not autosave:
            affinities = {}
            for file_features,curves in self.expose_all:

                affinities[file_features["file_path"]] = {}
                target = self.find_target_file(self.file_type, file_features)

                for name,curve in curves.items():
                    target_path = target._data[0]["file_path"]
                    affinities[file_features["file_path"]][name] = curve.integral_affinity(target._curves[target_path][name])

            return affinities
        else:
            for file_features,curves in self.expose_all:

                target = self.find_target_file(self.file_type, file_features)

                for name,curve in curves.items():
                    target_path = target._data[0]["file_path"]
                    file_features[f"aff_{name}"] = curve.integral_affinity(target._curves[target_path][name])

            return self._data
    def divide_in_groups(self, grouping_feat:str) -> Generator["FileCurves"]:
        """
        Il metodo, dato un oggetto FileCurves contenente i dati di una certa quantità di file,
        divide il dataset in una lista di oggetti dello stesso tipo, ognuno contenente un solo gruppo di file.
        Vengono importate nei nuovi oggetti anche i dati delle curve corrispondenti.

        NB - con gruppo si intende un dataset in cui i file hanno tutti stesse feature, a meno
        della grouping feature
        """
        # ottengo istanze FileCurves con solo gli attributi file_type, _data e grouped_by
        out:list[FileCurves] = super().divide_in_groups(grouping_feat)

        for inst in out:
            for path in inst.paths:
                inst._curves[path] = self._curves[path]
            yield inst

    @staticmethod
    def find_target_file(file_type, file_features:dict):
        """Trova il file target corretto tra tutti quelli in cartella e ritorna un'istanza FileCurves contenente i dati"""
        type_configs = FilesFeatures.get_type_configs(file_type)

        target_dir = targets_dir/file_type   # cartella file target
        if not target_dir.exists():
            raise FileNotFoundError(f"Cartella {str(target_dir)} non trovata")

        target_files = target_dir.glob("*.csv")

        # costruisco i token da cercare nel nome del file target
        target_features = [
            f"{feature}_{file_features[feature]}" for feature in type_configs["TargetFeatures"]
        ]
        for t_file in target_files:
            if all(token in t_file.stem for token in target_features):
                return FileCurves.from_paths(t_file)
        raise f"Non è stato possibile trovare il file target per le curve del file {file_features["file_path"].stem}"


if __name__ == '__main__':
    # # path = r"C:\Users\user\Documents\Uni\Tirocinio\webapp\data\IdVd_TrapDistr_exponential_Vgf_0_Es_0.2_Em_0.2.csv"
    # paths = [Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_-1_Es_1.72_Em_0.18.csv'),
    #          Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_0_Es_1.72_Em_0.18.csv'),
    #          Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_1_Es_1.72_Em_0.18.csv'),
    #          Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_2_Es_1.72_Em_0.18.csv'),
    #          Path('C:/Users/user/Documents/Uni/Tirocinio/webapp/data/IdVd_TrapDistr_exponential_Vgf_-2_Es_1.72_Em_0.18.csv')]
    # # prova = FileCurves.from_paths(*paths)
    # # prova.calculate_affinities(autosave=True)
    # # print(prova._data)
    #
    # prova = FilesFeatures().from_paths(*paths)
    # print(prova.get_grouping_feat())
    # print(prova.grouped_by)

    paths = [
        Path(r"D:\IdVd_csv\IDVD_Region_1_EmAcc_0.93_Vgf_-2.csv"),
        Path(r"D:\IdVd_csv\IDVD_Region_1_EmAcc_0.93_Vgf_-1.csv"),
        Path(r"D:\IdVd_csv\IDVD_Region_1_EmAcc_0.93_Vgf_0.csv"),
        Path(r"D:\IdVd_csv\IDVD_Region_1_EmAcc_0.93_Vgf_1.csv"),
        Path(r"D:\IdVd_csv\IDVD_Region_1_EmAcc_0.93_Vgf_2.csv"),
    ]
    prova = FilesFeatures().from_paths(*paths, grouping_feature="Vgf")
    print(prova.get_tab_label())
