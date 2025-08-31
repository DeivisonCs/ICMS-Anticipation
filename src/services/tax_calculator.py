 
from decimal import Decimal
from typing import List
import pandas as pd

from config.settings import (
    INTERNAL_TAX_RATE_BA,
    INTERSTATE_TAX_RATE,
    ANTECIPACAO_TOTAL_RATE,
    ANTECIPACAO_PARCIAL_RATE,
    EXEMPTED_CST_LIST,
    REDUCTION_CST_LIST,
    ALREADY_CHARGED_CST_LIST
)
from models.nfe_item import NFEItem

class TaxCalculator: 

    @staticmethod
    def calculate_adjusted_mva(mva_st: Decimal) -> Decimal:

        if mva_st == Decimal('0'):
            return Decimal('0')

        a_step = (1 + (mva_st / 100)) * (1 - INTERNAL_TAX_RATE_BA)
        b_step = a_step / (1 - INTERSTATE_TAX_RATE)
        return round((b_step - 1) * 100, 2)

    @staticmethod
    def calculate_anticipation_taxes(nfe_item: NFEItem) -> NFEItem: 
        # Antecipação total (% do valor total)
        nfe_item.antecipacao_total = nfe_item.v_total * ANTECIPACAO_TOTAL_RATE

        # Antecipação parcial (% da base de cálculo)
        nfe_item.antecipacao_parcial = nfe_item.bc_icms * ANTECIPACAO_PARCIAL_RATE

        return nfe_item

    @staticmethod
    def process_dataframe_taxes(df: pd.DataFrame) -> pd.DataFrame: 
        if df.empty:
            return df

        # Converter colunas numéricas
        numeric_columns = ['V TOTAL', 'BC ICMS', 'V ICMS', 'A ICMS', 'MVA-ST', 'RED_BASE_CAL']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Calcular antecipações
        df['ANTECIPACAO_TOTAL'] = df['V TOTAL'] * float(ANTECIPACAO_TOTAL_RATE)
        df['ANTECIPACAO_PARCIAL'] = df['BC ICMS'] * float(ANTECIPACAO_PARCIAL_RATE)

        return df

    @staticmethod
    def calculate_summary_statistics(items: List[NFEItem]) -> dict:

        if not items:
            return {
                'total_items': 0,
                'total_value': Decimal('0'),
                'total_icms': Decimal('0'),
                'total_bc_icms': Decimal('0'),
                'total_anticipation': Decimal('0')
            }

        total_value = sum(item.v_total for item in items)
        total_icms = sum(item.v_icms for item in items)
        total_bc_icms = sum(item.bc_icms for item in items)
        total_anticipation = sum(
            (item.antecipacao_total or Decimal('0')) + 
            (item.antecipacao_parcial or Decimal('0')) 
            for item in items
        )

        return {
            'total_items': len(items),
            'total_value': total_value,
            'total_icms': total_icms,
            'total_bc_icms': total_bc_icms,
            'total_anticipation': total_anticipation
        }