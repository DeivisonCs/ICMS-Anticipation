from dataclasses import dataclass
from typing import List
from models.nfe_item import NFEItem

@dataclass
class Nfe:
    key: str
    ie: str
    uf: str
    number: str
    series: str
    emitter_name: str
    emitter_cnpj: str
    emission_date: str
    emitter_uf: str
    filename: str
    items: List[NFEItem]

    def __init__(self, key:str, uf:str, ie:str, number:str, series:str, emitter_name:str, emitter_cnpj:str, emission_date:str, emitter_uf:str, filename: str, items: List[NFEItem]):
        self.emitter_name = emitter_name
        self.emitter_cnpj = emitter_cnpj
        self.ie = ie
        self.number = number
        self.key = key
        self.series = series
        self.emission_date = emission_date
        self.emitter_uf = emitter_uf
        self.items = items
        self.filename = filename
        self.uf = uf

        if len(emitter_cnpj) != 14:
            raise ValueError("CNPJ deve ter 14 caracteres.")
        if len(ie) != 9:
            raise ValueError("IE deve ter 9 caracteres.")