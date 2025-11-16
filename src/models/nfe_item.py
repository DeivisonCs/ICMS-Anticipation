from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class NFEItem: 
    cProd: str = ""
    uf_origin: str = ""
    ncm: str = ""
    o_cst: str = ""
    red_base_cal: Decimal = Decimal('0.0')
    cfop: str = ""
    v_total: Decimal = Decimal('0.0')
    bc_icms: Decimal = Decimal('0.0')
    v_icms: Decimal = Decimal('0.0')
    a_icms: Decimal = Decimal('0.0')
    mva_st: Decimal = Decimal('0.0')
    cest: str = ""
    mva_adjusted: Decimal = Decimal('0.0')
    frete: Decimal = Decimal('0.0')
    ipi: Decimal = Decimal('0.0')
    outros: Decimal = Decimal('0.0')
    seguro: Decimal = Decimal('0.0')
    antecipacao_total: Optional[Decimal] = None
    antecipacao_parcial: Optional[Decimal] = None

    def __init__(self, c_prod:str, uf_origin:str, ncm:str, o_cst:str, red_base_cal:Decimal, cfop:str, v_total:Decimal, bc_icms:Decimal, v_icms:Decimal, a_icms:Decimal, mva_st:Decimal, cest:str, mva_adjusted:Decimal, freight:Decimal, ipi:Decimal, others:Decimal, insurance:Decimal):
        self.cProd = c_prod
        self.ncm = ncm
        self.o_cst = o_cst
        self.red_base_cal = red_base_cal
        self.cfop = cfop
        self.v_total = v_total
        self.bc_icms = bc_icms
        self.v_icms = v_icms
        self.a_icms = a_icms
        self.mva_st = mva_st
        self.cest = cest
        self.mva_adjusted = mva_adjusted
        self.frete = freight
        self.ipi = ipi
        self.others = others
        self.seguro = insurance
        self.uf_origin = uf_origin

    def to_dict(self) -> dict:
        return {
            'CPROD': self.cProd,
            'NCM/SH': self.ncm,
            'UF': self.uf_origin,
            'O/CST': self.o_cst,
            'RED_BASE_CAL': Decimal(self.red_base_cal or '0.0'),
            'CFOP': self.cfop,
            'V TOTAL': Decimal(self.v_total or '0.0'),
            'BC ICMS': Decimal(self.bc_icms or '0.0'),
            'V ICMS': Decimal(self.v_icms or '0.0'),
            'A ICMS': Decimal(self.a_icms or '0.0'),
            'MVA-ST': Decimal(self.mva_st or '0.0'),
            'CEST': self.cest,
            'MVA': Decimal(self.mva_adjusted or '0.0'),
            'ANTECIPACAO_TOTAL': Decimal(self.antecipacao_total or '0.0') if self.antecipacao_total else 0.0,
            'ANTECIPACAO_PARCIAL': Decimal(self.antecipacao_parcial or '0.0') if self.antecipacao_parcial else 0.0,
            'FRETE': Decimal(self.frete or '0.0') if self.frete else 0.0,
            'IPI': Decimal(self.ipi or '0.0') if self.ipi else 0.0,
            'SEGURO': Decimal(self.seguro or '0.0') if self.seguro else 0.0,
            'OUTROS': Decimal(self.outros or '0.0') if self.outros else 0.0
        }

    @classmethod
    def from_xml_data(cls, xml_data: dict) -> 'NFEItem': 
        return cls(
            cProd=xml_data.get('CPROD', ''),
            ncm=xml_data.get('NCM/SH', ''),
            uf_origin=xml_data.get('UF', ''),
            o_cst=xml_data.get('O/CST', ''),
            red_base_cal=Decimal(str(xml_data.get('RED_BASE_CAL', '0'))),
            cfop=xml_data.get('CFOP', ''),
            v_total=Decimal(str(xml_data.get('V TOTAL', '0'))),
            bc_icms=Decimal(str(xml_data.get('BC ICMS', '0'))),
            v_icms=Decimal(str(xml_data.get('V ICMS', '0'))),
            a_icms=Decimal(str(xml_data.get('A ICMS', '0'))),
            mva_st=Decimal(str(xml_data.get('MVA-ST', '0'))),
            cest=xml_data.get('CEST', ''),
            mva_adjusted=Decimal(str(xml_data.get('MVA', '0'))),
            frete=Decimal(str(xml_data.get('FRETE', '0'))),
            ipi=Decimal(str(xml_data.get('IPI', '0'))),
            seguro=Decimal(str(xml_data.get('SEGURO', '0'))),
            outros=Decimal(str(xml_data.get('OUTROS', '0')))
        )