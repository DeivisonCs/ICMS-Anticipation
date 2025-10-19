from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict
from utils.helpers import safe_decimal_converter

@dataclass
class MvaValues:
    _4: Decimal = Decimal("0.0")
    _7: Decimal = Decimal("0.0")
    _12: Decimal = Decimal("0.0")
    original: Decimal = Decimal("0.0")

    @classmethod
    def from_dict(cls, data: dict) -> "MvaValues":
        return cls(
            _4=safe_decimal_converter(data.get("4", 0)),
            _7=safe_decimal_converter(data.get("7", 0)),
            _12=safe_decimal_converter(data.get("12", 0)),
            original=safe_decimal_converter(data.get("original", 0)),
        )

@dataclass
class TaxedItem:
    item: str = ""
    cest: str = ""
    descricao: str = ""
    ncm: Dict[str, MvaValues] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "TaxedItem":
        ncm_dict = {
            codigo: MvaValues.from_dict(value)
            for codigo, value in data.get("ncm", {}).items()
        }

        return cls(
            item=data.get("item", ""),
            cest=data.get("cest", ""),
            descricao=data.get("descrição", ""),
            ncm=ncm_dict,
        )