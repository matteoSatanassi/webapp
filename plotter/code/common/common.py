from pathlib import Path
import numpy as np
import pandas as pd

## CLASSES ##
class Exp:
    """
    Identifica un singolo file esperimento

    Supporta file con nomi del tipo IdVd_exponential_Vgf_2_Es_1.72_Em_1.04.csv o TrapData_exponential_Vgf_0_Es_1.72_Em_0.18_(0,0).csv

    Utilizzabile sia per i file IdVd che quelli di TrapDistr

    :parameter file_path: indirizzo del file dell'esperimento
    :type file_path: str or pathlib.Path

    :raises FileNotFoundError: se il file non viene trovato all'indirizzo specificato
    """
    def __init__(self, file_path:Path|str) -> None:
        self.exp_type: str = None
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
        """Da utilizzare per compilare un'istanza di Exp definita dal solo path"""
        info = self.path.stem.split('_')
        self.exp_type = info[0]
        self.trap_distr = str(info[1])
        self.Es = float(info[5])
        self.Em = float(info[7])
        self.Vgf = int(info[3])
        if info[0] == 'TrapData':
            self.start_cond = toggle(info[8])   # in modo da avere l'acronimo delle condizioni iniziali e non la label
        return self
    @property
    def is_to_compile(self)->bool:
        """Controlla che un'istanza di classe Exp non sia ancora da compilare"""
        attrs = ('exp_type', 'trap_distr', 'Es', 'Em', 'Vgf')
        return any(getattr(self, attr) is None for attr in attrs)
    @property
    def group(self)->str:
        """Mostra il gruppo di esperimenti a cui appartiene un'istanza di Exp"""
        return f"{self.trap_distr}_{self.Em}_{self.Es}"
    # def compile_from(self,row)->'Exp':
    # da aggiungere per compilare un'istanza da un dataframe o da un dizionario

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

class ExpCurves:
    """
    Classe che comprende le informazione di uno o più esperimenti e le rispettive curve
    """
    def __init__(self, *args:Exp|Path|str):
        self.exp = [check_arg(arg) for arg in args]
        self.curves:list[dict[str,Curve]] = []
        if not self.exp:
            raise ValueError("ExpCurves richiede almeno un esperimento")
        if not same_group(*self.exp):
            raise ValueError("Gli esperimenti caricati nella stessa istanza ExpCurves non fanno parte dello stesso gruppo")
    def sort(self)->None:
        """Riordina tutte le curve appartenenti all'istanza di classe"""
        for curves_dict in self.curves:
            for key, curve in curves_dict.items():
                curve.sort()
        return None
    def import_curves(self)->None:
        self.curves = [import_csv(exp) for exp in self.exp]
        self.sort()
        return None

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

def toggle(value:str)->str:
    """
    Scambia Nome di una curva con la Label corrispondente o viceversa
    :param value: nome/label della curva
    :return: label/nome della curva
    """
    translator = {**dict(zip(CP.IdVd_labels, CP.IdVd_names)), **dict(zip(CP.IdVd_names, CP.IdVd_labels))}
    if value not in translator:
        raise ValueError(f"{value} non è supportato come nome o label per una curva")
    return translator[value]

def check_arg(arg)->Exp:
    """
    Controlla gli argomenti in ingresso alla classe ExpCurves,
    facendo in modo che siano sempre istanze di classe Exp compilate
    """
    if isinstance(arg, Exp):
        if arg.is_to_compile:
            arg = arg.compile
    elif isinstance(arg, (Path,str)):
        arg = Exp(arg).compile
    else:
        raise TypeError(f"Argument {arg} is not a valid type")
    return arg

def import_csv(exp:Exp)->dict[str,Curve]:
    curves = create_dict(exp.exp_type)
    try:
        data = pd.read_csv(exp.path)
        data.replace('-', '0', inplace=True)

        for col in data.columns:
            name, axis = col.split(' ') #[curve_name X/Y]
            if name not in curves:
                _,_,_,name = name.split('_')    #['trapped', 'charge', 'density', str_pos]
            match axis:
                case 'X':
                    curves[name].X = data[col].to_numpy(dtype=float)
                case 'Y':
                    curves[name].Y = data[col].to_numpy(dtype=float)
    except Exception as e:
        print(f"Errore leggendo {exp.path}: {e}")
        raise
    return curves

def create_dict(exp_type:str)->dict[str,Curve]:
    """Crea un dizionario di curve ad hoc in base al tipo di esperimento passato come argomento"""
    if exp_type == 'TrapData':
        return {pos:Curve(pos) for pos in CP.TrapData_pos}
    elif exp_type == 'IdVd':
        return {name:Curve(toggle(name)) for name in CP.IdVd_names}
    else:
        raise ValueError(f"{exp_type} può essere solo IdVd o TrapData")

def same_group(*args:Exp)->bool:
    """Dice se di esperimenti passati come argomenti fanno parte dello stesso gruppo"""
    if not all(isinstance(arg,Exp) for arg in args):
        raise TypeError('Gli argomenti della funzione devono essere tutti di tipo Exp')
    if len(args) < 2:
        return True
    ref = args[0].group
    return all(exp.group == ref for exp in args[1:])

## PARAMS ##
class CP:
    """Curves parameters"""
    IdVd_labels = ['v0','0','15','30']
    IdVd_names = ['(0,0)','(-7,0)','(-7,15)','(-7,30)']
    TrapData_pos = ['trap_density','0.5000','0.6160','0.7660','0.7830','0.9670','0.9840','1.1840','1.3340','1.8340']

'''
IdVd_Common -> ExpData(Exp, path)[__str__, fill()]
TrapDistrCommon -> ExpData(Exp, path)[__str__, fill()]
'''