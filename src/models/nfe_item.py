from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class NFEItem: 
    cProd: str = ""
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
    antecipacao_total: Optional[Decimal] = None
    antecipacao_parcial: Optional[Decimal] = None

    def to_dict(self) -> dict: 
        return {
            'CPROD': self.cProd,
            'NCM/SH': self.ncm,
            'O/CST': self.o_cst,
            'RED_BASE_CAL': float(self.red_base_cal),
            'CFOP': self.cfop,
            'V TOTAL': float(self.v_total),
            'BC ICMS': float(self.bc_icms),
            'V ICMS': float(self.v_icms),
            'A ICMS': float(self.a_icms),
            'MVA-ST': float(self.mva_st),
            'CEST': self.cest,
            'MVA': float(self.mva_adjusted),
            'ANTECIPACAO_TOTAL': float(self.antecipacao_total) if self.antecipacao_total else 0.0,
            'ANTECIPACAO_PARCIAL': float(self.antecipacao_parcial) if self.antecipacao_parcial else 0.0
        }

    @classmethod
    def from_xml_data(cls, xml_data: dict) -> 'NFEItem': 
        return cls(
            cProd=xml_data.get('CPROD', ''),
            ncm=xml_data.get('NCM/SH', ''),
            o_cst=xml_data.get('O/CST', ''),
            red_base_cal=Decimal(str(xml_data.get('RED_BASE_CAL', '0'))),
            cfop=xml_data.get('CFOP', ''),
            v_total=Decimal(str(xml_data.get('V TOTAL', '0'))),
            bc_icms=Decimal(str(xml_data.get('BC ICMS', '0'))),
            v_icms=Decimal(str(xml_data.get('V ICMS', '0'))),
            a_icms=Decimal(str(xml_data.get('A ICMS', '0'))),
            mva_st=Decimal(str(xml_data.get('MVA-ST', '0'))),
            cest=xml_data.get('CEST', ''),
            mva_adjusted=Decimal(str(xml_data.get('MVA', '0')))
        )
