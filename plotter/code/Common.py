from pathlib import Path
import numpy as np
import pandas as pd

## CLASSES ##
class Exp:
    def __init__(self, trap_distr:str, e_sigma:float, e_mid:float, v_gf:int, file_path:Path):
        self.trap_distr: str = trap_distr
        self.Es: float = e_sigma
        self.Em: float = e_mid
        self.Vgf: int = v_gf
        self.path:Path = file_path
