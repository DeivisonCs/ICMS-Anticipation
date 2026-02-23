from typing import List, Dict, Any
import pandas as pd
from models.nfe import Nfe
from services.tax_calculator import TaxCalculator
from utils.helpers import format_decimal_to_monetary


def group_nfes_by_ie(nfe_list: List[Nfe]) -> Dict[str, List[Nfe]]:
    grouped_nfes = {}
    for nfe in nfe_list:
        ie = nfe.ie or "Desconhecido"
        if ie not in grouped_nfes:
            grouped_nfes[ie] = []
        grouped_nfes[ie].append(nfe)
    return grouped_nfes


def generate_summary_data(nfes: List[Nfe]) -> List[Dict[str, Any]]:
    summary_data = []
    for nfe in nfes:
        items = nfe.items or []
        total_value = sum(float(item.v_total or 0) for item in items)
        total_icms = sum(float(item.v_icms or 0) for item in items)

        summary_data.append(
            {
                "NF-e": nfe.number or "S/N",
                "Série": nfe.series or "-",
                "Emitente": nfe.emitter_name or "Desconhecido",
                "UF": nfe.emitter_uf or "Desconhecido",
                "Data": nfe.emission_date or "-",
                "Total Itens": len(items),
                "Valor Total": f"R$ {total_value:,.2f}",
                "ICMS Total": f"R$ {total_icms:,.2f}",
            }
        )
    return summary_data


def get_combined_dataframe(nfe_list: List[Nfe]) -> pd.DataFrame:
    if not nfe_list:
        return pd.DataFrame()
    tax_calculator = TaxCalculator()
    result = tax_calculator.process_dataframe_taxes(nfe_list)
    return pd.DataFrame(result)


def calculate_dataframe_statistics(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {
            "total_items": 0,
            "total_value": 0.0,
            "total_icms": 0.0,
            "antecipacao": 0.0,
        }

    total_value = df["V TOTAL"].replace("", 0).astype(float).sum()
    total_icms = df["V ICMS"].replace("", 0).astype(float).sum()

    antecipacao_total = (
        df["ANTECIPACAO_TOTAL"].replace("", 0).astype(float).sum()
        if "ANTECIPACAO_TOTAL" in df
        else 0
    )
    antecipacao_parcial = (
        df["ANTECIPACAO_PARCIAL"].replace("", 0).astype(float).sum()
        if "ANTECIPACAO_PARCIAL" in df
        else 0
    )

    return {
        "total_items": len(df),
        "total_value": float(total_value),
        "total_icms": float(total_icms),
        "antecipacao": float(antecipacao_total + antecipacao_parcial),
    }


def format_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    if "MVA_ADJUSTED" in df_copy.columns:
        df_copy = df_copy.drop(["MVA_ADJUSTED"], axis=1)
    if "MVA-ST" in df_copy.columns:
        df_copy = df_copy.rename(columns={"MVA-ST": "MVA"})

    if not df_copy.empty and len(df_copy.columns) >= 2:
        df_copy.iloc[:, -2:] = df_copy.iloc[:, -2:].applymap(format_decimal_to_monetary)

    return df_copy


def extract_period_from_date(emission_date: str) -> str:
    if not emission_date:
        return ""
    parts = emission_date.split("/")
    if len(parts) == 3:
        return f"{parts[1]}/{parts[2]}"
    return ""
