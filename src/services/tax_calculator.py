from decimal import Decimal, ROUND_HALF_UP
from typing import List
import pandas as pd
from utils.helpers import safe_decimal_converter, convert_nfe_list_to_dataframe, add_dots_to_ncm_

from models.nfe import Nfe

from config.settings import (
    INTERNAL_TAX_RATE_BA,
    INTERSTATE_TAX_RATE,
    ANTECIPACAO_PARCIAL_RATE,
    EXEMPTED_CST_LIST,
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

    def calculate_anticipation_taxes(self, nfe:Nfe, products: List[NFEItem]) -> List[NFEItem]:
        for item in products:
            item.antecipacao_total = Decimal("0.0")
            item.antecipacao_parcial = Decimal("0.0")

            if not self.is_supplier_uf_taxed(nfe.emitter_uf):
                continue

            if self.is_ncm_taxed(item.ncm):
                if not self.is_st_already_paid_by_cst(item.o_cst):
                    item.antecipacao_total = self.calculate_total_anticipation(nfe, item)

            else:
                if nfe.isSimple:
                    item.antecipacao_parcial = self.calculate_partial_anticipation_inside(nfe, item)
                else:
                    item.antecipacao_parcial = self.calculate_partial_anticipation_inside(nfe, item)

        return products

    def _get_cred_icms(self, nfe: Nfe, item: NFEItem) -> Decimal:
        if nfe.isSimple:
            return item.bc_icms * INTERSTATE_TAX_RATE
        else:
            return item.v_icms

    def process_dataframe_taxes(self, nfe_list: List[Nfe]) -> pd.DataFrame:
        if not nfe_list:
            return nfe_list

        calculated_items:List[NFEItem] = []

        for nfe in nfe_list:
            items = []

            for item in nfe.items:
                nfe_item = NFEItem (
                    c_prod=item.cProd,
                    ncm=item.ncm,
                    o_cst=item.o_cst,
                    red_base_cal=safe_decimal_converter(item.red_base_cal),
                    cfop=item.cfop,
                    v_total=safe_decimal_converter(item.v_total),
                    bc_icms=safe_decimal_converter(item.bc_icms),
                    v_icms=safe_decimal_converter(item.v_icms),
                    a_icms=safe_decimal_converter(item.a_icms),
                    mva_st=safe_decimal_converter(item.mva_st),
                    mva_adjusted=safe_decimal_converter(item.mva_adjusted),
                    cest=item.cest
                )

                items.append(nfe_item)

            calculated_items.extend(self.calculate_anticipation_taxes(nfe, items))

        return convert_nfe_list_to_dataframe(calculated_items)

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
        for item in TAXED_ITEMS:
            ncms_values = item.ncm.keys()
            if ncm in ncms_values:
                return True

            for ncm_value in ncms_values:
                ncm_value_start = ncm_value.split('.')[0]
                if ncm.startswith(ncm_value_start):
                    return True

        return False

    def calculate_total_anticipation(self, nfe:Nfe, item: NFEItem) -> Decimal:
        bc_ant = item.v_total + nfe.freight + nfe.ipi + nfe.insurance + nfe.others
        cred_icms = self._get_cred_icms(nfe, item)

        mva = item.mva_st
        if item.mva_adjusted:
            mva = item.mva_adjusted

        result: Decimal = ((bc_ant + mva) * INTERNAL_TAX_RATE_BA) - cred_icms
        return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_partial_anticipation_inside(self, nfe:Nfe, item: NFEItem) -> Decimal:
        bc_ant = item.v_total + nfe.freight + nfe.ipi + nfe.insurance + nfe.others
        result: Decimal = bc_ant * (INTERNAL_TAX_RATE_BA - INTERSTATE_TAX_RATE)

        return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_partial_anticipation_outside(self, nfe:Nfe, item: NFEItem) -> Decimal:
        bc_ant = item.v_total + nfe.freight + nfe.ipi + nfe.insurance + nfe.others
        cred_icms = self._get_cred_icms(nfe, item)

        result: Decimal = (bc_ant * INTERNAL_TAX_RATE_BA) - cred_icms

        return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)