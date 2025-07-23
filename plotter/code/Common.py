from pathlib import Path
import plotly.graph_objects as go
import numpy as np
import pandas as pd

## CLASSES ##

# identifica un esperimento, a cui appartengono 4 curve
class Exp:
    def __init__(self, file_path:Path, trap_distr:str=None, e_sigma:float=None, e_mid:float=None, v_gf:int=None) -> None:
        self.trap_distr: str = trap_distr
        self.Es: float = e_sigma
        self.Em: float = e_mid
        self.Vgf: int = v_gf
        self.path:Path = file_path
    def fill(self)->None:
        info = np.array((self.path.stem.split('_')))  # es: IdVd_exponential_Vgf_2_Es_1.72_Em_1.04
        self.trap_distr = info[1]
        self.Es = float(info[5])
        self.Em = float(info[7])
        self.Vgf = int(info[3])

# identifica una singola curva di un esperimento
class Curve:
    def __init__(self, name:str):
        self.name:str = name
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
        self.curves:dict[str, Curve] = dict()
        for key, name in CP.names.items():
            self.curves[key] = Curve(name)
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

class ExpPlots:
    def __init__(self, exp:Exp):        #possibilità di aggiungere più esperimenti in array
        self.exp_curves = ExpCurves(exp)
        self.fig = go.Figure()
    def plot(self, c_to_plot:list[str])->None:
        self.exp_curves.import_csv()
        self.exp_curves.sort()
        for c in c_to_plot:
            self.fig.add_trace(go.Scatter(
                x=self.exp_curves.curves[c].X,
                y=self.exp_curves.curves[c].Y,
                name=self.exp_curves.curves[c].name,
                mode='lines+markers',
                line=dict(
                    color=CP.colors[c] if Config.colors else 'black',
                    dash=None if Config.colors else CP.linestyles[c],
                ),
                marker=dict(
                    symbol='square',
                ),
                visible=True
            ))
        return None

## PARAMS ##
class Config:
    DPI = 300
    bk_color = 'white'
    sec_color = 'black'
    out_ext = 'png' #png, pdf, svg
    same_fig = True
    legend = True
    colors = True

class CP:   # curves params
    names = {
        "v0": "(0,0)",
        "0": "(-7,0)",
        "15": "(-7,15)",
        "30": "(-7,30)"
    }
    colors = {
        "v0": "red",
        "0": "limegreen",
        "15": "dodgerblue",
        "30": "darkorange"
    }
    linestyles = {
        "v0": "dashdot",
        "0": "dotted",
        "15": "dashed",
        "30": "solid"
    }   # to use in case of colorless image configuration