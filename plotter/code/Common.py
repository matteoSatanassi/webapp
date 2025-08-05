from pathlib import Path
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd

## CLASSES ##

# identifica un esperimento, a cui appartengono 4 curve
class Exp:
    def __init__(self, file_path:Path|str, trap_distr:str=None, e_sigma:float=None, e_mid:float=None, v_gf:int=None) -> None:
        self.trap_distr: str = trap_distr
        self.Es: float = e_sigma
        self.Em: float = e_mid
        self.Vgf: int = v_gf
        if Path(file_path).exists():
            self.path = Path(file_path)
        else:
            raise FileNotFoundError(f'file {file_path} non trovato!')
    def __str__(self):
        return self.path.stem
    def fill(self)->'Exp':
        info = np.array((self.path.stem.split('_')))  # es: IdVd_exponential_Vgf_2_Es_1.72_Em_1.04
        self.trap_distr = str(info[1])
        self.Es = float(info[5])
        self.Em = float(info[7])
        self.Vgf = int(info[3])
        return self

class Group:
    def __init__(self) -> None:
        self.trap_distr: str = None
        self.Es: float = None
        self.Em: float = None
        self.files: dict[int,Path] = {}
    def __contains__(self, item:Exp) -> bool:
        if self.trap_distr == item.trap_distr and self.Es == item.Es and self.Em == item.Em:
            return True
        else:
            return False
    def __str__(self) -> str:
        return f"IdVd_{self.trap_distr}_Es_{self.Es}_Em_{self.Em}"  #IdVd_exponential_Vgf_-1_Es_0.2_Em_0.2
    def add(self, exp:Exp)->None:
        if not self.trap_distr:
            self.trap_distr = exp.trap_distr
            self.Es = exp.Es
            self.Em = exp.Em
        elif exp not in self:
            raise Exception(f"Cannot add {exp} to {self}, it doesn't belong to the group")
        self.files[exp.Vgf] = Path(exp.path)
        return None
    def add_path(self, path:Path) -> None:
        self.add(Exp(path).fill())
        return None
    def add_paths(self, paths:list[Path]) -> 'Group':
        if type(paths) is not list:
            paths = [paths]
        for path in paths:
            self.add(Exp(path).fill())
        return self

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
    def sort(self)->None:
        self.curves['v0'].sort()
        self.curves['0'].sort()
        self.curves['15'].sort()
        self.curves['30'].sort()
        return None
    def import_csv(self)->None:
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

# classe che raggruppa tutte le curve di un dato gruppo(sotto forma di ExpCurves)
class GroupCurves:
    def __init__(self, group:Group):
        self.group:Group = group
        self.curves:list[ExpCurves] = []
        for vgf,file in group.files.items():    # POSSIBILE IMPLEMENTARE METODO __iter__() (chatGPT)
            exp = Exp(
                trap_distr=group.trap_distr,
                e_sigma=group.Es,
                e_mid=group.Em,
                v_gf=vgf,
                file_path=file
            )
            self.curves.append(ExpCurves(exp))
    def sort_all_exp(self)->None:
        for exp_curves in self.curves:
            exp_curves.sort()
        return None
    def import_all_csv(self)->None:
        for exp_curves in self.curves:
            exp_curves.import_csv()
        return None
    def y_limits_group(self)->list:
        y_mins = []
        y_maxs = []
        for exp_curves in self.curves:
            y_min_exp, y_max_exp = exp_curves.y_limits_exp()
            y_mins.append(y_min_exp)
            y_maxs.append(y_max_exp)
        return min(y_mins), max(y_maxs)

# classe per graficare esperimento singolo
class ExpPlot:
    def __init__(self, exp:Exp):        #possibilità di aggiungere più esperimenti in array
        self.exp_curves = ExpCurves(exp)
        self.fig = go.Figure()
    def plot(self, c_to_plot:list[str])->'ExpPlot':
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
        return self

# classe per graficare un gruppo di esperimenti
class GroupPlot:
    def __init__(self, group:Group):
        self.group_curves = GroupCurves(group)
        self.fig = go.Figure()
    def plot(self, c_to_plot:list[str])->'GroupPlot':
        self.group_curves.import_all_csv()
        self.group_curves.sort_all_exp()
        for exp_curve in self.group_curves.curves:
            for c in c_to_plot:
                self.fig.add_trace(go.Scatter(
                    x=exp_curve.curves[c].X,
                    y=exp_curve.curves[c].Y,
                    name=f"{exp_curve.curves[c].name} - Vgf:{exp_curve.exp.Vgf}",
                    mode='lines+markers',
                    line=dict(
                        color=CP.colors[c] if Config.colors else 'black',
                        dash=None if Config.colors else CP.linestyles[c],
                        width=0.75
                    ),
                    marker=dict(
                        symbol=GP.markers[exp_curve.exp.Vgf],
                        size=8 if GP.markers[exp_curve.exp.Vgf]=='*' else None
                    ),
                    visible=True
                ))
        return self

## FUNCTIONS ##
def try_mkdir(path:Path)->Path:
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        return None
    except:
        raise RuntimeError(f"Impossibile creare {path}")
    return path

def find_export_path()->Path:
    i=0
    while True:
        export_path = try_mkdir(Path("../exported_files/export" if i==0 else f"../exported_files/export-{i}"))
        if export_path:
          return export_path
        i+=1

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

class GP:
    markers = {
        -2: "square",
        -1: "circle",
        0: "triangle-down",
        1: "diamond",
        2: "star"
    }  # to use in same fig, multiple plots