from pathlib import Path
import plotly.graph_objects as go
import numpy as np
import pandas as pd

## CLASSES ##

# identifica un esperimento, a cui appartengono 4 curve
class Exp:
    def __init__(self, trap_distr:str, e_sigma:float, e_mid:float, v_gf:int, file_path:Path):
        self.trap_distr: str = trap_distr
        self.Es: float = e_sigma
        self.Em: float = e_mid
        self.Vgf: int = v_gf
        self.path:Path = file_path

# identifica una singola curva di un esperimento
class Curve:
    def __init__(self):
        self.X: np.ndarray = None
        self.Y: np.ndarray = None
    def sort(self)->None:   #ordina gli array delle coordinate in modo crescente, rispetto alle x
        i_sorted = np.argsort(self.X)
        self.X = self.X[i_sorted]
        self.Y = self.Y[i_sorted]
        return None
    def y_limits(self)->list:
        return self.Y.min(), self.Y.max()

# classe che raggruppa tutte le curve di un dato esperimento
class ExpCurves:
    def __init__(self, exp:Exp):
        self.exp:Exp = exp
        self.curves:dict[str, Curve] = {
            'v0': Curve(),
            '0': Curve(),
            '15': Curve(),
            '30': Curve(),
        }
    def sort(self):
        self.curves['v0'].sort()
        self.curves['0'].sort()
        self.curves['15'].sort()
        self.curves['30'].sort()
    def import_csv(self):
        if not self.exp.path.exists():
            raise FileNotFoundError(f'file {self.exp.path} non trovato!')
        try:
            data = pd.read_csv(self.exp.path)
            data.replace('-','0',inplace=True)

            for col in data.columns:
                name, ax = np.array(col.split(' '), dtype=str) #[curve_name X/Y]
                match ax:
                    case 'X': self.curves[name].X = data[col].to_numpy(dtype=float)
                    case 'Y': self.curves[name].Y = data[col].to_numpy(dtype=float)

            self.sort()
        except Exception as e:
            print(f"Errore leggendo {self.exp.path}: {e}")
            raise
        return None
    def y_limits_exp(self)->list:
        y_mins = []
        y_maxs = []
        for name, curve in self.curves.items():
            y_min, y_max = curve.y_limits()
            y_mins.append(y_min)
            y_maxs.append(y_max)
        return min(y_mins), max(y_maxs)

## PARAMS ##
class Config:
    DPI = 300
    bk_color = 'white'
    sec_color = 'black'
    out_ext = 'png' #png, pdf, svg
    same_fig = True
    legend = True
    colors = True
