from pathlib import Path
import json

from dash.dash_table.FormatTemplate import percentage


## CLASSES ##
class AppConfigs(object):
    """
    Legge e modifica i parametri di configurazione dell'applicazione
    """
    assets_dir = Path(__file__).resolve().parent / 'assets'
    targets_dirs = assets_dir / 'target_curves'
    config_file = assets_dir / 'config.json'

    def __init__(self):
        self.all:dict = self.load_configs()

    # APP CONFIGS
    @property
    def export_dir(self)->Path:
        return Path(self.all["export_directory"])
    @property
    def data_dir(self)->Path:
        return Path(self.all["data_directory"])
    @property
    def theme(self)->str:
        return self.all["theme"]
    @property
    def legend(self)->bool:
        return bool(self.all["legend"])
    @property
    def colors(self)->bool:
        return bool(self.all["colors"])
    @property
    def dpi(self)->int:
        return int(self.all["DPI"])

    # derived
    @property
    def indexes_file(self)->Path:
        return self.data_dir / 'indexes.xlsx'

    def save_all(self):
        """Salva la configurazione aggiornata"""
        with open(self.config_file, 'w', encoding="utf-8") as f:
            json.dump(self.all, f, indent=4)
    def set_vals(self, **kwargs):
        """
        Imposta uno o più parametri di configurazione e salva.

        I parametri accettati sono le chiavi del dizionario di configurazione:

        * theme (str): Il tema dell'interfaccia. Es: "DARKLY"
        * data_directory (str): Il percorso alla cartella dei dati.
        * export_directory (str): Il percorso per l'esportazione dei file.
        * export_format (str): Il formato di esportazione. Es: "png", "svg"
        * legend (bool): Se mostrare la legenda nei grafici.
        * colors (bool): Se usare i colori nei grafici.
        * DPI (int): La risoluzione per l'esportazione dei grafici.

        Qualsiasi altra chiave passata verrà ignorata e segnalata.
        """
        for key, value in kwargs.items():
            if key in self.all:
                self.all[key] = value
            else:
                raise ValueError("Il valore specificato non è parte dei parametri di configurazione supportati")
        self.save_all()

    @staticmethod
    def load_configs():
        """Carica configurazione esistente o crea default"""
        if AppConfigs.config_file.exists():
            with open(AppConfigs.config_file, 'r', encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "theme": "SUPERHERO",
                "data_directory": str(Path(__file__).parent.parent.parent.parent / 'data'),
                "export_directory": str(Path.home() / 'Desktop' / 'exported_files'),
                "export_format": "png",
                "legend": True,
                "colors": True,
                "DPI": 150,
            }


class FileConfigs(object):
    """
    Si occupa di leggere e modificare i parametri di configurazione di un certo file_type,
    specificato alla creazione
    """
    files_configs_file = AppConfigs.assets_dir / 'files_configs.json'

    def __init__(self, file_type:str):        
        self._files_configs = self.load_files_info()

        if file_type in self._files_configs:
            self._file_type = file_type
            self.all = self._files_configs[file_type]
        else:
            raise ValueError("Il file type specificato non è tra quelli supportati")

    @property
    def allowed_curves(self)->dict[str,str]:
        return self.all["AllowedCurves"]
    @property
    def allowed_features(self)->dict[str,str]:
        return self.all["AllowedFeatures"]
    @property
    def targets_presents(self)->bool:
        return bool(self.all["TargetCurves"])
    @property
    def target_features(self)->list[str]:
        if self.targets_presents:
            return self.all["TargetFeatures"]
        else:
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
        Ritorna la lista delle colonne da passare al parametro columns
        di un oggetto dash_table
        """
        from dash import dash_table

        columns = [
            {"name": f_name,
             "id": f_name,
             "type": "numeric" if f_type in ("integer", "float") else None}
            for f_name, f_type in self.allowed_features.items()
        ]
        if self.targets_presents:
            percentage_format = dash_table.FormatTemplate.percentage(2)
            columns.append({
                "name": "Aff Overall",
                "id": "aff_tot",
                "type": "numeric",
                "format": percentage_format
            })
            for curve_id, curve_label in self.allowed_curves.items():
                columns.append({
                    "name": f"Aff {curve_label}",
                    "id": f"aff_{curve_id}",
                    "type": "numeric",
                    "format": percentage_format
                })

        return columns

    def modify_curves(self, **kwargs):
        for key, value in kwargs.items():
            self.all["AllowedCurves"][str(key)] = str(value)
        self.save_all()
    def modify_features(self, **kwargs):
        for key, value in kwargs.items():
            self.all["AllowedFeatures"][str(key)] = str(value)
        self.save_all()
    def save_all(self):
        self._files_configs[self._file_type] = self.all
        with open(self.files_configs_file, 'w', encoding="utf-8") as f:
            json.dump(self._files_configs, f, indent=4)
            
    @staticmethod
    def load_files_info()->dict:
        """
            Carica i tipi di file da analizzare nella run,
            i parametri a loro associati e le curve contenute
        """
        if FileConfigs.files_configs_file.exists():
            with open(FileConfigs.files_configs_file, 'r', encoding="utf-8") as f:
                out = json.load(f)
                out.pop("_comments")
                return out
        else:
            return {}
    @staticmethod
    def supported_file_types()->list[str]:
        """Ritorna la lista dei file_type supportati dall'applicazione"""
        out:list = FileConfigs.load_files_info().keys()
        out.remove("_comments")
        return out


if __name__ == '__main__':
    config = AppConfigs()
    print(config.dpi)