"""
Il modulo contiene due classi contenenti, il cui compito è leggere, memorizzare,
modificare e salvare i vari parametri di configurazione dell'applicazione
"""

import json
from pathlib import Path


## CLASSES ##
class AppConfigs:
    """
    Legge e modifica i parametri di configurazione dell'applicazione
    """
    assets_dir = Path(__file__).resolve().parent / 'assets'
    targets_dirs = assets_dir.parent.parent.parent.parent / 'target_curves'
    config_file = assets_dir / 'config.json'

    defaults = {"theme": "SUPERHERO",
                "data_directory": str(Path(__file__).parent.parent.parent.parent / 'data'),
                "export_directory": str(Path.home() / 'Desktop' / 'exported_files'),
                "export_format": "png",
                "legend": True,
                "colors": True,
                "DPI": 150,}

    def __init__(self):
        self._all:dict = self.load_configs()

    # APP CONFIGS GETTERS
    @property
    def export_dir(self)->Path:
        """Ritorna l'indirizzo della directory di esportazione"""
        return Path(self._all["export_directory"])
    @property
    def export_format(self)->str:
        """Ritorna il formato di esportazione impostato"""
        return str(self._all["export_format"])
    @property
    def data_dir(self)->Path:
        """Ritorna l'indirizzo della directory contenente i dati .csv"""
        return Path(self._all["data_directory"])
    @property
    def theme(self)->str:
        """Ritorna il nome del tema dell'applicazione"""
        return self._all["theme"]
    @property
    def legend(self)->bool:
        """Ritorna bool, se la legenda è visualizzata da impostazioni"""
        return bool(self._all["legend"])
    @property
    def colors(self)->bool:
        """Ritorna bool, se i grafici sono impostati come colorati"""
        return bool(self._all["colors"])
    @property
    def dpi(self)->int:
        """Ritorna la risoluzione impostata per i grafici"""
        return int(self._all["DPI"])

    # derived
    @property
    def indexes_file(self)->Path:
        """Ritorna l'indirizzo del file di indicizzazione"""
        return self.data_dir / 'indexes.xlsx'

    # APP CONFIGS SETTERS
    @export_dir.setter
    def export_dir(self, val):
        self._all["export_directory"] = str(val)
    @export_format.setter
    def export_format(self, val):
        self._all["export_format"] = str(val)
    @data_dir.setter
    def data_dir(self, val):
        self._all["data_directory"] = str(val)
    @theme.setter
    def theme(self, val):
        self._all["theme"] = str(val)
    @legend.setter
    def legend(self, val):
        self._all["legend"] = str(val)
    @colors.setter
    def colors(self, val):
        self._all["colors"] = str(val)
    @dpi.setter
    def dpi(self, val):
        self._all["DPI"] = str(val)

    def save_all(self):
        """Salva la configurazione aggiornata"""
        with open(self.config_file, 'w', encoding="utf-8") as f:
            json.dump(self._all, f, indent=4)
    def reset_all(self):
        """Resetta i parametri di configurazione dell'applicazione e salvati in memoria"""
        self._all = self.defaults.copy()
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)
        self.save_all()

    @staticmethod
    def load_configs():
        """Carica configurazione esistente o crea default"""
        if AppConfigs.config_file.exists():
            with open(AppConfigs.config_file, 'r', encoding="utf-8") as f:
                return json.load(f)
        else:
            return AppConfigs.defaults


class FilesConfigsManager:
    """Classe preposta a interventi generici sul file di configurazione"""

    files_configs_file = AppConfigs.assets_dir / 'files_configs.json'

    @staticmethod
    def load_files_info() -> dict:
        """
        Carica i tipi di file da analizzare nella run,
        i parametri a loro associati e le curve contenute
        """
        files_configs_file = FilesConfigsManager.files_configs_file
        if files_configs_file.exists():
            with open(files_configs_file, 'r', encoding="utf-8") as f:
                out = json.load(f)
                if "_comments" in out:
                    out.pop("_comments")
                return out
        else:
            return {}


class FileConfigs:
    """
    Si occupa di memorizzare e presentare i parametri di configurazione
    di un certo file_type, specificato alla creazione
    """
    def __init__(self, file_type:str):
        self.file_type = file_type
        self._all:dict = None

    @classmethod
    def from_mem(cls):
        """
        Crea una lista di istanze FileConfigs, contenenti i dati contenuti
        nel file di configurazione files_configs.json
        """
        cfgs = FilesConfigsManager.load_files_info()

        out:list[FileConfigs] = []
        for file_type in cfgs.keys():
            inst = cls(file_type)
            inst._all = cfgs[file_type]
            out.append(inst)

        return out

    @property
    def allowed_curves(self)->dict[str,str]:
        """Ritorna il dizionario AllowedCurves {acr:label}"""
        return self._all["AllowedCurves"]
    @property
    def allowed_features(self)->dict[str,str]:
        """Ritorna il dizionario AllowedFeatures {feat:feature_type}"""
        return self._all["AllowedFeatures"]
    @property
    def targets_presents(self)->bool:
        """Ritorna se il file_type corrente ha delle curve taget o no"""
        return bool(self._all["TargetCurves"])
    @property
    def target_features(self)->list[str]:
        """Ritorna le features secondo cui riconoscere le curve target per i vari esperimenti"""
        if self.targets_presents:
            return self._all["TargetFeatures"]
        return "No targets present"
    @property
    def get_table_cols(self)->list[str]:
        """
        Ritorna la lista delle colonne nel file di indicizzazione di questo data_type,
        controllando anche se devono essere presenti colonne per i fattori di affinità
        a in caso aggiungendole
        """
        out = list(self.allowed_features.keys())
        if self.targets_presents:
            out.append("aff_tot")
            for curve in self.allowed_curves.keys():
                out.append(f"aff_{curve}")
        return out
    @property
    def get_dash_table_cols(self)->list[dict]:
        """
        Ritorna la lista delle colonne da passare al parametro columnDefs
        di un oggetto dash_ag_grid.AgGrid
        """
        columns = [
            {
                "headerName": "",
                "field": "selection",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "width": 40,
                "maxWidth": 40,
                "suppressSizeToFit": True,
                "pinned": "left",
                "lockPinned": True,
                "lockPosition": "left",
                "sortable": False,
                "filter": False,
                "headerClass": "center-header",
                "suppressMenu": True,
                "valueFormatter": {"function": "return null"},
            }
        ]

        columns.extend([
            {"headerName": f_name,
             "field": f_name,
             "type": "numericColumn" if f_type in ("integer", "float") else None,
             "filter": "agNumberColumnFilter" if f_type in ("integer", "float") else "agTextColumnFilter",
             "hide":False,}
            for f_name, f_type in self.allowed_features.items()
        ])

        if self.targets_presents:
            # Formattatore per le percentuali (es. 0.85 -> 85.00%)
            percentage_formatter = {"function": "d3.format('.2%')(params.value)"}

            columns.append({
                "headerName": "Aff Overall",
                "field": "aff_tot",
                "type": "numericColumn",
                "valueFormatter": percentage_formatter
            })
            for curve_id, curve_label in self.allowed_curves.items():
                columns.append({
                    "headerName": f"Aff {curve_label}",
                    "field": f"aff_{curve_id}",
                    "type": "numericColumn",
                    "valueFormatter": percentage_formatter
                })

        return columns

    # def modify_curves(self, **kwargs):
    #     """
    #     Date delle coppie chiave, valore, modifica i valori delle rispettive
    #     curve nel dizionario delle AllowedCurves, e lo salva in memoria
    #     """
    #     for key, value in kwargs.items():
    #         self._all["AllowedCurves"][str(key)] = str(value)
    #     self.save_all()
    # def modify_features(self, **kwargs):
    #     """
    #     Date delle coppie chiave, valore, modifica i valori delle rispettive
    #     features nel dizionario delle AllowedCurves, e lo salva in memoria
    #     """
    #     for key, value in kwargs.items():
    #         self._all["AllowedFeatures"][str(key)] = str(value)
    #     self.save_all()


class FilesConfigs(FilesConfigsManager):
    """
    La classe contiene tutti i metodi per la
    lettura e la modifica dei dati contenuti in
    files_configs.json
    """

    file_data = FilesConfigsManager.load_files_info()

    data = {f_configs.file_type:f_configs for f_configs in FileConfigs.from_mem()}

    @property
    def supported_file_types(self) -> set[str]:
        """Ritorna la lista dei file_type salvati nella classe"""
        return set(self.file_data.keys())

    def save_all(self):
        """Salva in memoria i parametri di configurazione scritti nella classe"""
        for file_type in self.data:
            self.file_data[file_type] = self.data[file_type]._all

        with open(self.files_configs_file, 'w', encoding="utf-8") as f:
            json.dump(self.file_data, f, indent=4)


## CACHE CLASS ##

class ConfigCache:
    """
    La classe si occupa di raggruppare i parametri di configurazione dell'applicazione
    """
    app_configs = AppConfigs()

    _files_configs = FilesConfigs()

    @property
    def file_types(self) -> set[str]:
        return self._files_configs.supported_file_types

    @staticmethod
    def get_f_configs(file_type:str) -> FileConfigs:
        if file_type not in ConfigCache.file_types:
            raise ValueError(f"Il file_type {file_type} non compare tra i presenti nell'applicazione")

        return ConfigCache._files_configs.data[file_type]

if __name__ == '__main__':
    print(AppConfigs.targets_dirs.exists())
