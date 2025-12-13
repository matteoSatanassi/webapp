import json
from pathlib import Path
from pypalettes import load_palette
from app_resources.AppCache import ConfigCache


## CLASSES ##
class ConfigFileManager:
    plotter_configs_file = Path(__file__).parent / "PlotterConfigs.json"

    @staticmethod
    def generate_generic_file_configs(file_type:str):
        """
        Genera un dizionario con dei configs generici per un file_type generico

        Riempie solo il dizionario dei colori con delle palette generate randomicamente
        """
        if file_type not in ConfigCache.file_types:
            raise ValueError(f"Il file_type {file_type} non è supportato dall'applicazione")

        allowed_curves =ConfigCache.files_configs[file_type].allowed_curves
        curves_palette = ConfigFileManager.generate_palette(len(allowed_curves))

        file_cfgs = ConfigFileManager.template_file_configs()
        file_cfgs["Colors"] = {
            curve:color for curve,color in zip(allowed_curves, curves_palette)
        }

        return file_cfgs
    @staticmethod
    def template_file_configs():
        return {
            "Colors":{}, "Linestyles":{}, "GroupsMarkers":{}, "AxisProps": {"X":{}, "Y":{}}
        }
    @staticmethod
    def generate_palette(num_colors:int):
        """Dato un numero N, ritorna una lista di N colori"""
        out = []
        while len(out) < num_colors:
            out.extend(load_palette())
        return out[:num_colors-1]
    @staticmethod
    def load_plotter_configs():
        """
        Carica i parametri di funzionamento del plotter
        """
        if ConfigFileManager.plotter_configs_file.exists():
            with open(ConfigFileManager.plotter_configs_file, 'r', encoding="utf-8") as f:
                return json.load(f)
        else:
            raise FileNotFoundError("Non è stato possibile trovare il file di configurazione")


class PlotFileTypeConfigs:
    default_marker = "square"

    def __init__(self, file_type:str):
        self.file_type = file_type
        self._data = None

    @classmethod
    def from_config_dict(cls):
        """
        Crea una lista di istanze PlotFileTypeConfigs, contenenti i dati contenuti
        nel file di configurazione del plotter
        """
        cfgs = ConfigFileManager.load_plotter_configs()

        out:list[PlotFileTypeConfigs] = []
        for file_type in ConfigCache.file_types:
            inst = cls(file_type)
            inst._data = (cfgs[file_type] if file_type in cfgs else
                          ConfigFileManager.generate_generic_file_configs(file_type))
            out.append(inst)

        return out

    def expose(self):
        """Ritorna la tupla (key, data), in modo da poterla salvare in memoria"""
        return self.file_type, self._data

    @property
    def _groups_markers_dict(self) -> dict:
        """
        Ritorna il dizionario di definizione dei marker di gruppo,
        nel caso almeno uno sia stato definito, altrimenti ritorna None
        """
        if self._data["GroupsMarkers"]:
            return self._data["GroupsMarkers"]
        return None
    @property
    def _get_axis_props(self) -> dict[str, dict]:
        return self._data["AxisProps"]

    @property
    def colors(self)->dict[str,str]:
        """Ritorna il dizionario dei colori {curve_name:color}"""
        return self._data["Colors"]
    @property
    def linestyles(self)->dict[str,str]:
        """
        Ritorna il dizionario dei linestyles {curve_name:linestyle}

        In caso non siano stati impostati ritorna None
        """
        if self._data["Linestyles"]:
            return self._data["Linestyles"]
        return None
    @property
    def has_colorless_configuration(self):
        """Sono definiti dei parametri linestyles per il file_type?"""
        return bool(self.linestyles)
    @property
    def has_grouping_configuration(self):
        """
        Se sono definiti dei possibili raggruppamenti per il file_type,
        ritorna le feature di raggruppamento definite, altrimenti False
        :return:
        """
        if self._groups_markers_dict:
            return self._groups_markers_dict.values
        return False

    def get_group_markers(self, grouping_feat:str)->dict[str,str]|None:
        """
        Ritorna il dizionario dei marker di gruppo data la
        feature di raggruppamento

        In caso la feature sia stata definita presenta un dizionario del tipo
        {feat_val:marker_type}, altrimenti None
        """
        if grouping_feat in self._groups_markers_dict:
            return self._groups_markers_dict[grouping_feat]["Values"]
        return None
    def get_grouping_feat_size(self,grouping_feat:str)->str|None:
        """
        Nel caso la feature di raggruppamento sia stata definita, ritorna
        la sua grandezza fisica, altrimenti False
        """
        if grouping_feat in self._groups_markers_dict:
            return self._groups_markers_dict[grouping_feat]["Size"]
        return None
    def get_axis_title(self,axis:str)->str|None:
        """Ritorna il titolo dell'asse specificato; se non presente ritorna None"""
        axis = axis.upper()
        try:
            if axis in "XY":
                return self._get_axis_props[axis]["Title"]
            raise ValueError(f"Titolo non specificato per l'asse {axis}, per il file_type {self.file_type}")
        except Exception:
            return None


class PlotterConfigs(ConfigFileManager):
    files_configs = {f_conf.file_type:f_conf for f_conf
                     in PlotFileTypeConfigs.from_config_dict()}

    def save_all(self):
        """Salva i parametri attualmente caricati"""
        cfgs = {
            file_type:cfg for f_conf in self.files_configs.values()
            for file_type,cfg in f_conf.expose()
        }

        with open(self.plotter_configs_file, 'w', encoding="utf-8") as f:
            json.dump(cfgs, f, indent=4)
