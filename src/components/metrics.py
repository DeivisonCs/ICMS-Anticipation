import streamlit as st
from typing import Dict


def render_statistics_cards(stats: Dict[str, float]):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Itens", stats["total_items"])
    with col2:
        st.metric("Valor Total", f"R$ {stats['total_value']:,.2f}")
    with col3:
        st.metric("ICMS Total", f"R$ {stats['total_icms']:,.2f}")
    with col4:
        st.metric("Antecipação", f"R$ {stats['antecipacao']:,.2f}")
