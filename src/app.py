 
import streamlit as st
import pandas as pd
from typing import List

from config.settings import STREAMLIT_CONFIG
from services.xml_processor import XMLProcessor
from services.tax_calculator import TaxCalculator
from services.file_handler import FileHandler
from models.nfe_item import NFEItem


def configure_page(): 
    st.set_page_config(**STREAMLIT_CONFIG)


def render_header(): 
    st.title("📊 Calculadora de ICMS - NF-E")
    st.markdown("---")
    
    st.markdown("""
    ### Como usar:
    1. Faça upload de um arquivo ZIP contendo uma ou mais NF-Es (arquivos XML)
    2. Aguarde o processamento
    3. Visualize os dados processados
    4. Baixe a planilha com os resultados dos cálculos de ICMS
    """)


def render_file_uploader():
     
    uploaded_file = st.file_uploader(
        "Selecione o arquivo ZIP com as NF-Es",
        type=['zip'],
        help="O arquivo deve conter arquivos XML de NF-E"
    )
    return uploaded_file


def render_statistics(df: pd.DataFrame):
     
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Itens", len(df))
    with col2:
        st.metric("Valor Total", f"R$ {df['V TOTAL'].sum():,.2f}")
    with col3:
        st.metric("ICMS Total", f"R$ {df['V ICMS'].sum():,.2f}")
    with col4:
        st.metric("Base Cálculo Total", f"R$ {df['BC ICMS'].sum():,.2f}")


def render_data_preview(df: pd.DataFrame):
     
    st.subheader("Preview dos Dados")
    st.dataframe(df.head(10), use_container_width=True)


def render_download_button(df: pd.DataFrame):
     
    excel_data = FileHandler.dataframe_to_excel(df)
    
    st.download_button(
        label="📥 Baixar Planilha Excel",
        data=excel_data,
        file_name="icms_calculado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def render_full_data_option(df: pd.DataFrame):
     
    if st.checkbox("Mostrar todos os dados"):
        st.subheader("Dados Completos")
        st.dataframe(df, use_container_width=True)


def process_uploaded_file(uploaded_file) -> pd.DataFrame:
     
    # Validar arquivo
    if not FileHandler.validate_zip_file(uploaded_file):
        st.error("Arquivo ZIP inválido ou não contém arquivos XML.")
        return pd.DataFrame()
    
    # Processar arquivo ZIP
    with st.spinner('Processando NF-Es...'):
        raw_data = XMLProcessor.process_zip_file(uploaded_file)
    
    if not raw_data:
        st.error("Não foi possível extrair dados do arquivo.")
        return pd.DataFrame()
    
    # Converter para DataFrame e calcular impostos
    df = pd.DataFrame(raw_data)
    df = TaxCalculator.process_dataframe_taxes(df)
    
    return df


def main():
     
    configure_page()
    render_header()
    
    # Upload do arquivo
    uploaded_file = render_file_uploader()
    
    if uploaded_file is not None:
        st.success(f"Arquivo carregado: {uploaded_file.name}")
        
        # Processar arquivo
        df = process_uploaded_file(uploaded_file)
        
        if not df.empty:
            st.success(f"Processamento concluído! {len(df)} itens encontrados.")
            
            # Renderizar componentes da interface
            render_statistics(df)
            render_data_preview(df)
            render_download_button(df)
            render_full_data_option(df)
        else:
            st.error("Não foi possível processar os dados do arquivo.")


if __name__ == "__main__":
    main()
