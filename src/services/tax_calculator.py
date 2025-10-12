 
from dataclasses import asdict
from decimal import Decimal
from typing import List
import pandas as pd
from utils.helpers import safe_decimal_converter, convert_nfe_list_to_dataframe, format_ncm, add_dots_to_ncm_

from config.settings import (
    INTERNAL_TAX_RATE_BA,
    INTERSTATE_TAX_RATE,
    ANTECIPACAO_TOTAL_RATE,
    ANTECIPACAO_PARCIAL_RATE,
    EXEMPTED_CST_LIST,
    REDUCTION_CST_LIST,
    ALREADY_CHARGED_CST_LIST,
    TAXED_ITEMS
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

    def calculate_anticipation_taxes(self, products: List[NFEItem]) -> List[NFEItem]:
        for item in products:
            if not self.is_supplier_uf_taxed(item.uf_origin):
                continue

            if self.is_ncm_taxed(item.ncm):
                if not self.is_st_already_paid_by_cst(item.o_cst[1:]):
                    item.antecipacao_total = self.calculate_total_anticipation(item)

            else:
                item.antecipacao_parcial = item.bc_icms * ANTECIPACAO_PARCIAL_RATE

        return products

    def process_dataframe_taxes(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # Converter colunas numéricas
        numeric_columns = ['V TOTAL', 'BC ICMS', 'V ICMS', 'A ICMS', 'MVA-ST', 'RED_BASE_CAL']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        items = []
        for index, row in df.iterrows():
            cest = row['CEST']
            ncm = row['NCM/SH']
            mva_st = safe_decimal_converter(row['MVA-ST'])

            for item in TAXED_ITEMS:
                formated_ncm = add_dots_to_ncm_(ncm)
                if cest == item.cest.replace('.', '') and formated_ncm in list(item.ncm.keys()):
                    mva_st = item.ncm[formated_ncm].original

            nfe_item = NFEItem (
                cProd=row['CPROD'],
                uf_origin=row['UF'],
                ncm=ncm,
                o_cst=row['O/CST'],
                red_base_cal=safe_decimal_converter(row['RED_BASE_CAL']),
                cfop=row['CFOP'],
                v_total=safe_decimal_converter(row['V TOTAL']),
                bc_icms=safe_decimal_converter(row['BC ICMS']),
                v_icms=safe_decimal_converter(row['V ICMS']),
                a_icms=safe_decimal_converter(row['A ICMS']),
                mva_st=mva_st,
                mva_adjusted=TaxCalculator.calculate_adjusted_mva(mva_st),
                cest=cest,
                frete=safe_decimal_converter(row['FRETE']),
                ipi=safe_decimal_converter(row['IPI']),
                outros=safe_decimal_converter(row['OUTROS'])
            )
            items.append(nfe_item)

        items = self.calculate_anticipation_taxes(items)

        return convert_nfe_list_to_dataframe(items)

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

    def is_st_already_paid_by_cst(self, cst: str) -> bool:
        if cst in ALREADY_CHARGED_CST_LIST:
            return True

        return False

    def is_exempted_cst(self, cst: str) -> bool:
        if cst in EXEMPTED_CST_LIST:
            return True

        return False

    def is_supplier_uf_taxed(self, uf: str) -> bool:
        taxed_uf_list = ['BA']

        if uf.upper() in taxed_uf_list:
            return False

        return True

    def is_ncm_taxed(self, ncm) -> bool:
        if any(ncm in list(item.ncm.keys()) for item in TAXED_ITEMS):
            return True

        return False

    def calculate_total_anticipation(self, nfe: NFEItem) -> Decimal:
        bc_ant = nfe.v_total + nfe.frete + nfe.ipi + nfe.seguro + nfe.outros
        cred = nfe.bc_icms * INTERSTATE_TAX_RATE

        return ((bc_ant + nfe.mva_adjusted) * INTERNAL_TAX_RATE_BA) - cred