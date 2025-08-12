from pathlib import Path
import plotly.graph_objects as go
import numpy as np


## CLASSES ##
class Exp:
    """
    Identifica un singolo file esperimento
    supporta file con nomi del tipo IdVd_exponential_Vgf_2_Es_1.72_Em_1.04.csv o TrapData_exponential_Vgf_0_Es_1.72_Em_0.18_(0,0).csv

    Utilizzabile sia per i file IdVd che quelli di TrapDistr

    :parameter file_path: indirizzo del file dell'esperimento
    :type file_path: str or pathlib.Path

    :raises FileNotFoundError: se il file non viene trovato all'indirizzo specificato
    """
    def __init__(self, file_path:Path|str) -> None:
        self.trap_distr: str = None
        self.Es: float = None
        self.Em: float = None
        self.Vgf: int = None
        self.start_cond: str = None
        if Path(file_path).exists():
            self.path = Path(file_path)
        else:
            raise FileNotFoundError(f'file {file_path} non trovato!')
    def __str__(self):
        return self.path.stem
    @property
    def compile(self)->'Exp':
        """
        Da utilizzare per inizializzare un'istanza di Exp definita dal solo path

        :return: istanza di classe completa di tutti i parametri non nulli
        :rtype: Exp
        :raises : se il file ha un nome non supportato
        """

        info = np.array((self.path.stem.split('_')))
        if info[0] == 'TrapData':
            self.start_cond = toggle(info[8])   # in modo da avere l'acronimo delle condizioni iniziali e non la label
        self.trap_distr = str(info[1])
        self.Es = float(info[5])
        self.Em = float(info[7])
        self.Vgf = int(info[3])
        return self

class Curve:
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
    def sort(self)->None:   #
        """
        Ordina gli array delle coordinate in modo crescente, rispetto alle ordinate

        :return: None
        """
        i_sorted = np.argsort(self.X)
        self.X = self.X[i_sorted]
        self.Y = self.Y[i_sorted]
        return None
    def y_limits(self)->list:
        return self.Y.min(), self.Y.max()

## FUNCTIONS ##
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

def find_export_path()->Path:
    """
    Crea un indirizzo di esportazione valido
    :return: Indirizzo di esportazione creato
    :rtype: pathlib.Path
    """
    i=0
    while True:
        export_path = try_mkdir(Path("../../exported_files/export" if i==0 else f"../../exported_files/export-{i}"))
        if export_path:
          return export_path
        i+=1

def toggle(name:str)->str:
    """
    Scambia Nome di una curva con la Label corrispondente o viceversa
    :param name: nome/label della curva
    :type name: str
    :return: label/nome della curva
    :rtype: str
    """
    if name in CP.labels:
        return CP.labels[name]
    elif name in CP.names:
        return CP.names[name]
    else:
        raise ValueError(f"{name} non è supportato")

## PARAMS ##
class CP:   # curves params
    labels = {
        "v0": "(0,0)",
        "0": "(-7,0)",
        "15": "(-7,15)",
        "30": "(-7,30)"
    }
    names = {
        "(0,0)": "v0",
        "(-7,0)": "0",
        "(-7,15)": "15",
        "(-7,30)": "30"
    }





'''
IdVd_Common -> ExpData(Exp, path)[__str__, fill()]
TrapDistrCommon -> ExpData(Exp, path)[__str__, fill()]
'''