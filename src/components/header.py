import streamlit as st


def render_header():
    st.title("📊 Calculadora de ICMS - NF-E")
    st.markdown("---")
    st.markdown("""
    ### Como usar:
    1. Faça upload de um arquivo ZIP contendo uma ou mais NF-Es (arquivos XML)
    2. Aguarde o processamento
    3. Selecione a NF-e que deseja visualizar
    4. Visualize e analise os dados de cada NF-e individualmente
    5. Baixe a planilha com os resultados dos cálculos de ICMS
    """)
