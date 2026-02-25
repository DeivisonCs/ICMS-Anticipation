import streamlit as st
import pandas as pd
from services.file_handler import FileHandler


def render_nfe_summary_table(
    ie: str, summary_data: list, total_nfes: int, total_items: int
):
    st.subheader(f"Inscrição Estadual: {ie}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de NF-es", total_nfes)
    with col2:
        st.metric("Total de Itens", total_items)

    st.dataframe(pd.DataFrame(summary_data), width="stretch")


def render_detailed_dataframe(df: pd.DataFrame, title: str):
    st.subheader(title)
    st.dataframe(df, width="stretch")


def render_download_button(
    df: pd.DataFrame, filename: str, emitter_name: str, period: str, ie: str
):
    excel_data = FileHandler.dataframe_to_excel(df, emitter_name, period, ie)
    st.download_button(
        label="📥 Baixar Planilha Excel",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
