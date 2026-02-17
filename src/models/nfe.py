from dataclasses import dataclass
from typing import List
from decimal import Decimal
from models.nfe_item import NFEItem

@dataclass
class Nfe:
    key: str
    ie: str
    number: str
    series: str
    emitter_name: str
    emitter_cnpj: str
    emission_date: str
    emitter_uf: str
    filename: str
    freight: Decimal
    insurance: Decimal
    ipi: Decimal
    others: Decimal
    isSimple: bool
    isSimei: bool
    items: List[NFEItem]

    def __init__(self, key:str, ie:str, number:str, series:str, emitter_name:str, emitter_cnpj:str, emission_date:str, emitter_uf:str, freight:Decimal, insurance:Decimal, others:Decimal, filename:str, isSimple:bool, isSimei:bool, items:List[NFEItem], ipi:Decimal):
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
        self.freight = freight
        self.insurance = insurance
        self.ipi = ipi
        self.others = others
        self.isSimple = isSimple
        self.isSimei = isSimei

        if len(emitter_cnpj) != 14:
            raise ValueError("CNPJ deve ter 14 caracteres.")
        if len(ie) != 9:
            raise ValueError("IE deve ter 9 caracteres.")