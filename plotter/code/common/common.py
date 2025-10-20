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
        return f"{self.exp_type}_{self.trap_distr}_Em_{self.Em}_Es_{self.Es}"
    # def compile_from(self,row)->'Exp':
    # da aggiungere per compilare un'istanza da un dataframe o da un dizionario

class Curve:
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
    def sort(self)->None:   #
        """
        Ordina gli array delle coordinate in modo crescente, rispetto alle ordinate

        :return: None
        """
        i_sorted = np.argsort(self.X)
        self.X = self.X[i_sorted]
        self.Y = self.Y[i_sorted]
        return None
    @property
    def integrate(self)->float:
        """Integra la curva caricata nell'istanza"""
        return np.trapezoid(self.Y, self.X)
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
    def __contains__(self, other:Exp) -> bool:
        if not isinstance(other, Exp):
            raise TypeError("__contains__() richiede il confronto con un Exp")
        return same_group(other, *self.exp)
    def __add__(self, other:Exp) -> 'ExpCurves':
        if not isinstance(other, Exp):
            raise TypeError("__add__() richiede di aggiungere un Exp all'istanza")
        if other in self:
            self.exp.append(other)
        return self
    def __str__(self):
        if len(self.exp)<2:
            return self.exp[0].path.stem
        else:
            return self.exp[0].group
    def sort(self)->None:
        """Riordina tutte le curve appartenenti all'istanza di classe"""
        for curves_dict in self.curves:
            for key, curve in curves_dict.items():
                curve.sort()
        return None
    def import_data(self)->'ExpCurves':
        self.curves = [import_csv(exp) for exp in self.exp]
        self.sort()
        return self
    @property
    def contains_imported_data(self)->bool:
        """Controlla che l'istanza di classe abbia dei valori importati nel campo curve"""
        if not self.curves:
            return False
        if len(self.curves) != len(self.exp):
            print("Errore: il numero di esperimenti e di raccolte di curve contenute nella classe sono diversi")
            return False
        return True
    @property
    def contains_group(self)->bool:
        """Controlla che l'istanza di classe contenga un gruppo o un singolo esperimento"""
        if len(self.exp) > 1:
            return True
        return False
    def curves_areas(self):
        """Controlla che l'istanza sia piena, poi, nel caso sia un esperimento IdVd,
         ritorna un dizionario contenente le aree delle curve al suo interno"""
        if self.contains_group:
            return None
        if self.exp[0].exp_type == 'IdVd':
            if not self.contains_imported_data:
                self.import_data()
            areas = {}
            for name,curve in self.curves[0].items():
                areas[name] = curve.integrate
            return areas
        return None
    def get_vgf(self,curves_dict:dict[str,Curve])->int:
        """Dato un elemento di self.curves, recupera la Vg_f del rispettivo esperimento"""
        return self.exp[self.curves.index(curves_dict)].Vgf
    def names_update(self)->None:
        """
        Se l'istanza di ExpCurves corrente contiene un gruppo di esperimenti, aggiunge
        la rispettiva vgf ai nomi delle varie curve.

        Nel caso l'istanza contenga un esperimento di tipo trapData aggiunge 'x=...µm' ai nomi
        delle curve
        """
        if not self.contains_group:
            if self.exp[0].exp_type=='TrapData':
                for curves_dict in self.curves:
                    for key, curve in curves_dict.items():
                        curve.name = f"x={float(curve.name)}µm" if curve.name!='trap_density' else "Trap Density"
            return None
        for curves_dict in self.curves:
            vgf = self.get_vgf(curves_dict)
            for key, curve in curves_dict.items():
                curve.name += f", Vgf={vgf}"
        return None
        

## HELPER FUNCTIONS ##
def toggle(value:str)->str:
    """
    Scambia Nome di una curva con la Label corrispondente o viceversa
    :param value: nome/label della curva
    :return: label/nome della curva
    """
    translator = {**dict(zip(CP.IdVd_names, CP.IdVd_labels)), **dict(zip(CP.IdVd_labels, CP.IdVd_names))}
    if value not in translator:
        raise ValueError(f"{value} non è supportato come nome o label per una curva")
    return translator[value]

def check_arg(arg)->Exp:
    """
    Controlla gli argomenti in ingresso alla classe ExpCurves,
    facendo in modo di ritornare sempre istanze della classe Exp compilate
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
    """Dato un oggetto Exp importa i dati contenuti nel .csv indicato e crea un dizionario di curve"""
    curves = create_dict(exp.exp_type)
    try:
        data = pd.read_csv(exp.path)
        data.replace('-', '0', inplace=True)

        for col in data.columns:
            name, axis = col.split(' ') #[curve_name X/Y]
            if name not in curves:
                _,_,_,name = name.split('_')    #['trapped', 'charge', 'density', str_pos]
            if name not in curves:
                curves[name] = Curve(name)
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
    IdVd_names = ['v0','0','15','30']
    IdVd_labels = ['(0,0)','(-7,0)','(-7,15)','(-7,30)']
    TrapData_pos = ['trap_density']