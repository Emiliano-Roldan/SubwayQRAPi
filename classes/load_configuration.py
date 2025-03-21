import yaml
from pathlib import Path

class settings:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class configuration:
    def cargar_configuracion(self):
        with open(Path(__file__).resolve().parent.parent / "configuration\\config.yaml", 'r') as archivo: #C:\\nationalsoft\\FacturaPronta\\
            configuracion = yaml.safe_load(archivo)
            return settings(**configuracion)