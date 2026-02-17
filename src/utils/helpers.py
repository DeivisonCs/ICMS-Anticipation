"""
Funções auxiliares e utilitárias
"""
from decimal import Decimal, getcontext
from typing import Union, List
from models.nfe_item import NFEItem
from dataclasses import asdict
import pandas as pd

# Configurar precisão decimal
getcontext().prec = 10


def safe_decimal_converter(value: Union[str, None]) -> Decimal:
    if value == '' or value is None:
        return Decimal('0.0')
    try:
        return round(Decimal(str(value)), 2)
    except Exception:
        return Decimal('0.0')


def format_currency(value: Union[Decimal, float]) -> str:
    return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def format_percentage(value: Union[Decimal, float]) -> str:
    return f"{float(value):.2f}%"


def validate_ncm(ncm: str) -> bool:
    if not ncm:
        return False

    # Remove pontos e espaços
    ncm_clean = ncm.replace('.', '').replace(' ', '')

    # NCM deve ter 8 dígitos
    return len(ncm_clean) == 8 and ncm_clean.isdigit()

def format_ncm(ncm: str) -> str:
    return ncm.replace('.', '').replace(' ', '')

def validate_cfop(cfop: str) -> bool:
    if not cfop:
        return False

    # Remove pontos e espaços
    cfop_clean = cfop.replace('.', '').replace(' ', '')

    # CFOP deve ter 4 dígitos
    return len(cfop_clean) == 4 and cfop_clean.isdigit()


def clean_numeric_string(value: str) -> str:
    if not value:
        return '0'

    # Remove caracteres não numéricos (mantém apenas dígitos, vírgula e ponto)
    cleaned = ''.join(c for c in value if c.isdigit() or c in ['.', ','])

    # Substitui vírgula por ponto (padrão decimal)
    cleaned = cleaned.replace(',', '.')

    return cleaned if cleaned else '0'


def convert_nfe_list_to_dataframe(items: List[NFEItem]):
    df_result = pd.DataFrame([asdict(item) for item in items])

    column_mapping = {
        "cProd": "CPROD",
        "uf_origin": "UF",
        "ncm": "NCM/SH",
        "o_cst": "O/CST",
        "red_base_cal": "RED_BASE_CAL",
        "cfop": "CFOP",
        "v_total": "V TOTAL",
        "bc_icms": "BC ICMS",
        "v_icms": "V ICMS",
        "a_icms": "A ICMS",
        "mva_st": "MVA-ST",
        "cest": "CEST",
        "mva_adjusted": "MVA_ADJUSTED",
        "antecipacao_total": "ANTECIPACAO_TOTAL",
        "antecipacao_parcial": "ANTECIPACAO_PARCIAL",
        "outros": "OUTROS"
    }

    return df_result.rename(columns=column_mapping)

def add_dots_to_ncm_(ncm:str) -> str:
    LENGTH_OF_FIRST_DOT = 4

    if len(ncm) <= LENGTH_OF_FIRST_DOT:
        return ncm

    result = ''

    if len(ncm) > LENGTH_OF_FIRST_DOT:
        result += ncm[:LENGTH_OF_FIRST_DOT] + '.'

    for index, value in enumerate(ncm[LENGTH_OF_FIRST_DOT:]):
        result += value

        if (index+1) % 2 == 0 and index+LENGTH_OF_FIRST_DOT+1 < len(ncm):
            result += '.'

    return result

def format_decimal_to_monetary(value) -> str:
    result = value

    if isinstance(value, Decimal):
        result = f"{value:.2f}"

    result = "R$ " + result
    return result.replace(".", ",")