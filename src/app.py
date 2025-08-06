import streamlit as st
import pandas as pd
from typing import List, Dict

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
    3. Selecione a NF-e que deseja visualizar
    4. Visualize e analise os dados de cada NF-e individualmente
    5. Baixe a planilha com os resultados dos cálculos de ICMS
    """)


def render_file_uploader():
    uploaded_file = st.file_uploader(
        "Selecione o arquivo ZIP com as NF-Es",
        type=['zip'],
        help="O arquivo deve conter arquivos XML de NF-E"
    )
    return uploaded_file


def render_nfe_selector(nfe_list: List[Dict]):
     
    options = []
    for nfe in nfe_list:
        emitter = nfe.get('emitter_name', 'Desconhecido')
        number = nfe.get('nfe_number', 'S/N')
        date = nfe.get('emission_date', '')
        option_text = f"NF-e {number} - {emitter} - {date}"
        options.append((option_text, nfe['nfe_key']))
    
    # Add "All NFEs" option
    options.insert(0, ("Todas as NF-es", "all"))
    
    option_names = [opt[0] for opt in options]
    option_keys = [opt[1] for opt in options]
    
    selected_idx = st.selectbox(
        "Selecione a NF-e para visualizar:",
        range(len(option_names)),
        format_func=lambda i: option_names[i]
    )
    
    return option_keys[selected_idx]


def render_nfe_summary(nfe_list: List[Dict]):
     
    total_nfes = len(nfe_list)
    total_items = sum(len(nfe.get('items', [])) for nfe in nfe_list)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de NF-es", total_nfes)
    with col2:
        st.metric("Total de Itens", total_items)
    
    # Display a table with NF-e summary
    summary_data = []
    for nfe in nfe_list:
        items = nfe.get('items', [])
        # Fix: Handle empty strings before converting to float
        total_value = sum(float(item.get('V TOTAL', 0) or 0) for item in items)
        total_icms = sum(float(item.get('V ICMS', 0) or 0) for item in items)
        
        summary_data.append({
            'NF-e': nfe.get('nfe_number', 'S/N'),
            'Série': nfe.get('nfe_series', '-'),
            'Emitente': nfe.get('emitter_name', 'Desconhecido'),
            'Data': nfe.get('emission_date', '-'),
            'Total Itens': len(items),
            'Valor Total': f"R$ {total_value:,.2f}",
            'ICMS Total': f"R$ {total_icms:,.2f}"
        })
    
    st.subheader("Resumo das NF-es")
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)


def render_nfe_details(nfe: Dict):
     
    # Display NFE header
    st.subheader(f"NF-e {nfe.get('nfe_number', 'S/N')}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Emitente:** {nfe.get('emitter_name', 'Não informado')}")
    with col2:
        st.info(f"**CNPJ:** {nfe.get('emitter_cnpj', 'Não informado')}")
    with col3:
        st.info(f"**Data de Emissão:** {nfe.get('emission_date', 'Não informada')}")
    
    # Convert items to DataFrame and calculate taxes
    if not nfe.get('items', []):
        st.warning("Esta NF-e não possui itens ou não foi possível extraí-los.")
        return None
    
    df = pd.DataFrame(nfe.get('items', []))
    df = TaxCalculator.process_dataframe_taxes(df)
    
    # Display statistics
    render_statistics(df)
    
    # Display items
    st.subheader("Itens da NF-e")
    st.dataframe(df, use_container_width=True)
    
    return df


def render_statistics(df: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Itens", len(df))
    with col2:
        # Ensure we have numeric values
        total_value = df['V TOTAL'].replace('', 0).astype(float).sum()
        st.metric("Valor Total", f"R$ {total_value:,.2f}")
    with col3:
        # Ensure we have numeric values
        total_icms = df['V ICMS'].replace('', 0).astype(float).sum()
        st.metric("ICMS Total", f"R$ {total_icms:,.2f}")
    with col4:
        # Ensure we have numeric values
        antecipacao_total = df['ANTECIPACAO_TOTAL'].replace('', 0).astype(float).sum()
        antecipacao_parcial = df['ANTECIPACAO_PARCIAL'].replace('', 0).astype(float).sum()
        st.metric("Antecipação Total", f"R$ {(antecipacao_total + antecipacao_parcial):,.2f}")


def render_download_button(df: pd.DataFrame, filename="icms_calculado.xlsx"):
    excel_data = FileHandler.dataframe_to_excel(df)
    
    st.download_button(
        label="📥 Baixar Planilha Excel",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def combine_all_nfes(nfe_list: List[Dict]) -> pd.DataFrame:
     
    all_items = []
    
    for nfe in nfe_list:
        items = nfe.get('items', [])
        # Add NF-e info to each item
        for item in items:
            item_with_nfe = item.copy()
            item_with_nfe['NF-e'] = nfe.get('nfe_number', 'S/N')
            item_with_nfe['Emitente'] = nfe.get('emitter_name', 'Desconhecido')
            item_with_nfe['Data'] = nfe.get('emission_date', '-')
            all_items.append(item_with_nfe)
    
    if not all_items:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_items)
    df = TaxCalculator.process_dataframe_taxes(df)
    return df


def process_uploaded_file(uploaded_file) -> List[Dict]:
    # Validar arquivo
    if not FileHandler.validate_zip_file(uploaded_file):
        st.error("Arquivo ZIP inválido ou não contém arquivos XML.")
        return []
    
    # Processar arquivo ZIP
    with st.spinner('Processando NF-Es...'):
        nfe_list = XMLProcessor.process_zip_file(uploaded_file)
    
    if not nfe_list:
        st.error("Não foi possível extrair dados do arquivo.")
        return []
    
    return nfe_list


def main():
    configure_page()
    render_header()
    
    # Upload do arquivo
    uploaded_file = render_file_uploader()
    
    if uploaded_file is not None:
        st.success(f"Arquivo carregado: {uploaded_file.name}")
        
        # Processar arquivo
        nfe_list = process_uploaded_file(uploaded_file)
        
        if nfe_list:
            st.success(f"Processamento concluído! {len(nfe_list)} NF-es encontradas.")
            
            # Mostrar seletor de NF-e
            selected_nfe_key = render_nfe_selector(nfe_list)
            
            # Mostrar conteúdo com base na seleção
            if selected_nfe_key == "all":
                # Mostrar resumo de todas as NF-es
                render_nfe_summary(nfe_list)
                
                # Combinar todos os itens em um único DataFrame
                df_all = combine_all_nfes(nfe_list)
                
                if not df_all.empty:
                    render_statistics(df_all)
                    
                    st.subheader("Todos os Itens")
                    st.dataframe(df_all, use_container_width=True)
                    
                    # Download do arquivo completo
                    render_download_button(df_all, "todas_nfes_icms.xlsx")
            else:
                # Mostrar detalhes de uma NF-e específica
                selected_nfe = next((nfe for nfe in nfe_list if nfe['nfe_key'] == selected_nfe_key), None)
                if selected_nfe:
                    df = render_nfe_details(selected_nfe)
                    if df is not None:
                        # Download do arquivo individual
                        nfe_number = selected_nfe.get('nfe_number', 'nfe')
                        render_download_button(df, f"nfe_{nfe_number}_icms.xlsx")
        else:
            st.error("Não foi possível processar os dados do arquivo.")


if __name__ == "__main__":
    main()