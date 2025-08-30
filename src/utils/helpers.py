"""
Funções auxiliares e utilitárias
"""
from decimal import Decimal, getcontext
from typing import Union

# Configurar precisão decimal
getcontext().prec = 10


def safe_decimal_converter(value: Union[str, None]) -> Decimal:
    if value == '' or value is None:
        return Decimal('0.0')
    try:
        return Decimal(str(value))
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
