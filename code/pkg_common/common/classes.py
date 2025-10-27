from pathlib import Path
import numpy as np
import pandas as pd
from params import assets_dir

## CLASSES ##
class Exp:
    """
    Identifica un singolo file esperimento

    Supporta file con nomi del tipo IdVd_exponential_Vgf_2_Es_1.72_Em_1.04.csv o TrapData_exponential_Vgf_0_Es_1.72_Em_0.18_(0,0).csv

    Utilizzabile sia per i file IdVd che quelli di TrapDistr
    """

    # Variabili di classe
    IdVd_names = ('v0', '0', '15', '30')
    IdVd_labels = ('(0,0)', '(-7,0)', '(-7,15)', '(-7,30)')

    def __init__(self) -> None:
        self.exp_type: str = None
        self.trap_distr: str = None
        self.Es: float = None
        self.Em: float = None
        self.Vgf: int = None
        self.start_cond: str = None
        self.path = None
    def __str__(self):
        return self.path.stem
    @classmethod
    def from_path(cls, file_path:Path|str) -> 'Exp':
        """Crea una istanza di Exp fià compilata a partire da un file_path"""
        file_path = Path(file_path)
        if not Path(file_path).exists():
            raise FileNotFoundError(f'file {file_path} non trovato!')
        inst = cls()
        inst.path = Path(file_path)
        return inst.compile
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
            self.start_cond = self.toggle(info[8])   # in modo da avere l'acronimo delle condizioni iniziali e non la label
        return self
    @property
    def is_to_compile(self)->bool:
        """Controlla che un'istanza di classe Exp non sia ancora da compilare"""
        attrs = ('exp_type', 'trap_distr', 'Es', 'Em', 'Vgf')
        return any(getattr(self, attr) is None for attr in attrs)
    @property
    def group(self)->str:
        """
        Mostra il gruppo di esperimenti a cui appartiene un'istanza di Exp
        Un gruppo è identificato dalle stesse condizioni di quiescenza iniziali
        """
        return f"{self.exp_type}_{self.trap_distr}_Em_{self.Em}_Es_{self.Es}"
    @staticmethod
    def toggle(value: str) -> str:
        """
        Scambia Nome di una curva con la Label corrispondente o viceversa
        :param value: nome/label della curva
        :return: label/nome della curva
        """
        translator = {
            **dict(zip(Exp.IdVd_names, Exp.IdVd_labels)),
            **dict(zip(Exp.IdVd_labels, Exp.IdVd_names))
        }
        if value not in translator:
            raise ValueError(f"{value} non è supportato come nome o label per una curva")
        return translator[value]
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
    @classmethod
    def get_target(cls, vgf: int, state: str) -> 'Curve':
        if state not in Exp.IdVd_names:
            raise ValueError(f"la curva target con stato di quiescenza {state} non è presente")
        df_target = pd.read_excel(
            assets_dir /'target_curves'/ f"{vgf}.xlsx",
            sheet_name=state
        )
        target_curve = cls(f"taget {state} - Vgf = {vgf}")
        target_curve.X = df_target['Vds'].to_numpy(dtype=float)
        target_curve.Y = df_target['Ids'].to_numpy(dtype=float)
        return target_curve
    def sort(self)->None:   #
        """
        Ordina gli array delle coordinate in modo crescente, rispetto alle ordinate
        """
        i_sorted = np.argsort(self.X)
        self.X = self.X[i_sorted]
        self.Y = self.Y[i_sorted]
        return None
    @property
    def integral(self)->float:
        """Integra la curva caricata nell'istanza"""
        return np.trapezoid(self.Y, self.X)
    def integral_affinity(self, curve:'Curve')->float:
        target_area = curve.integral
        return max(1-abs(self.integral-target_area)/abs(target_area),0)
    def y_limits(self)->list:
        return self.Y.min(), self.Y.max()

class ExpCurves:
    """
    Classe che comprende le informazione di uno o più esperimenti e le rispettive curve
    """
    def __init__(self, *args:Exp|Path|str):
        self.exp:list[Exp] = [self.check_arg(arg) for arg in args]
        self.curves:list[dict[str,Curve]] = []
        self.affinities:list[dict[str,float]] = []
        self.group_affinity:dict[str,float]=None
        if not self.exp:
            raise ValueError("ExpCurves richiede almeno un esperimento")
        if not self.same_group(*self.exp):
            raise ValueError("Gli esperimenti caricati nella stessa istanza ExpCurves non fanno parte dello stesso gruppo")
    @staticmethod
    def check_arg(arg) -> Exp:
        """
        Controlla gli argomenti in ingresso alla classe ExpCurves,
        facendo in modo di ritornare sempre istanze della classe Exp compilate
        """
        if isinstance(arg, Exp):
            if arg.is_to_compile:
                arg = arg.compile
        elif isinstance(arg, (Path, str)):
            arg = Exp.from_path(arg)
        else:
            raise TypeError(f"Argument {arg} is not a valid type")
        return arg
    @staticmethod
    def same_group(*args: Exp) -> bool:
        """Dice se di esperimenti passati come argomenti fanno parte dello stesso gruppo"""
        if not all(isinstance(arg, Exp) for arg in args):
            raise TypeError('Gli argomenti della funzione devono essere tutti di tipo Exp')
        if len(args) < 2:
            return True
        ref = args[0].group
        return all(exp.group == ref for exp in args[1:])
    @staticmethod
    def exp_data(exp:Exp)->dict[str,Curve]:
        """Dato un oggetto Exp importa i dati collegati in un dizionario ordinato"""
        curves = {}
        try:
            data = pd.read_csv(exp.path)
            data.replace('-', '0', inplace=True)

            for col in data.columns:
                name, axis = col.split(' ')  # [curve_name X/Y]

                if exp.exp_type == 'TrapData' and name!='trap_density':
                    _, _, _, name = name.split('_')  # ['trapped', 'charge', 'density', str_pos]

                if name not in curves:
                    curves[name] = Curve(name)

                match axis:
                    case 'X':
                        curves[name].X = data[col].to_numpy(dtype=float)
                    case 'Y':
                        curves[name].Y = data[col].to_numpy(dtype=float)

        except Exception as error:
            print(f"Errore leggendo {exp.path}: {error}")
            raise
        return curves
    def __contains__(self, other:Exp) -> bool:
        if not isinstance(other, Exp):
            raise TypeError("__contains__() richiede il confronto con un Exp")
        return self.same_group(other, *self.exp)
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
    @property
    def contains_idvd_data(self):
        return all(exp.exp_type == 'IdVd' for exp in self.exp)
    @property
    def import_data(self)->'ExpCurves':
        self.curves = [self.exp_data(exp) for exp in self.exp]
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
    def get_vgf(self,attribute:dict)->int:
        """Dato un elemento di self.curves o self.affinities, recupera la Vg_f del rispettivo esperimento"""
        if attribute in self.curves:
            return self.exp[self.curves.index(attribute)].Vgf
        if attribute in self.affinities:
            return self.exp[self.affinities.index(attribute)].Vgf
        return None
    @property
    def group(self)->str:
        if self.contains_group:
            return self.exp[0].group
        return None
    @property
    def affinity_calc(self) -> 'ExpCurves':
        """calcola l'affinità delle curve caricate nell'istanza di classe rispetto alle curve target"""
        if not self.contains_idvd_data:
            raise ValueError("L'istanza non contiene solo dati IdVd")
        self.affinities = []
        for idx,curves_dict in enumerate(self.curves):
            vgf = self.get_vgf(curves_dict)
            e_affinity = {}
            for name,curve in curves_dict.items():
                e_affinity[name] = curve.integral_affinity(Curve.get_target(vgf,name))
            self.affinities.append(e_affinity)

        if self.contains_group:
            df_temp = pd.DataFrame(self.affinities)
            self.group_affinity = df_temp.mean().to_dict()

        return self
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

if __name__ == '__main__':
    # exp = Exp().from_path(
    #     'C:\\Users\\user\\Documents\\Uni\\Tirocinio\\webapp\\plotter\\data\\IdVd_exponential_Vgf_-1_Es_1.72_Em_1.31.csv'
    # )
    #
    # g = Exp()
    #
    # print(isinstance(exp,Exp))

    # print(f"Tipo: {exp.exp_type}")
    # print(f"Vgf: {exp.Vgf}")
    # print(f"Es: {exp.Es}")
    # print(f"Em: {exp.Em}")

    # target = Curve.get_target(2,'v0')
    # print(target.name)
    # print(target.X)
    # print(target.Y)

    e = ExpCurves(
         'C:\\Users\\user\\Documents\\Uni\\Tirocinio\\webapp\\plotter\\data\\IdVd_exponential_Vgf_-1_Es_1.72_Em_1.31.csv'
    ).import_data

    print(e.curves)