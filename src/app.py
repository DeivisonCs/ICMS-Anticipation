import streamlit as st
import pandas as pd
from typing import List, Dict

from config.settings import STREAMLIT_CONFIG
from services.xml_processor import XMLProcessor
from services.tax_calculator import TaxCalculator
from services.file_handler import FileHandler
from models.nfe import Nfe


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


def render_nfe_selector(nfe_list: List[Nfe]):
    # Agrupar NFES por Inscrição Estadual
    grouped_nfes = {}
    for nfe in nfe_list:
        ie = nfe.ie or 'Desconhecido'

        if ie not in grouped_nfes:
            grouped_nfes[ie] = []
        grouped_nfes[ie].append(nfe)

    # Criar opções para o seletor
    options = [("Todas as Inscrições", "all")]
    for ie in grouped_nfes.keys():
        options.append((f"Inscrição Estadual: {ie}", ie))

    option_names = [opt[0] for opt in options]
    option_keys = [opt[1] for opt in options]

    selected_idx = st.selectbox(
        "Selecione a Inscrição Estadual para visualizar:",
        range(len(option_names)),
        format_func=lambda i: option_names[i]
    )

    return option_keys[selected_idx]


def render_nfe_summary(nfe_list: List[Nfe]):
    # Agrupar NFEs por Inscrição Estadual
    grouped_nfes = {}
    for nfe in nfe_list:
        ie = nfe.ie or 'Desconhecido'
 
        if ie not in grouped_nfes:
            grouped_nfes[ie] = []
        grouped_nfes[ie].append(nfe)

    for ie, nfes in grouped_nfes.items():
        st.subheader(f"Inscrição Estadual: {ie}")

        total_nfes = len(nfes)
        total_items = sum(len(nfe.items or []) for nfe in nfes)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de NF-es", total_nfes)
        with col2:
            st.metric("Total de Itens", total_items)

        summary_data = []
        for nfe in nfes:
            items = nfe.items or []
            total_value = sum(float(item.v_total or 0) for item in items)
            total_icms = sum(float(item.v_icms or 0) for item in items)

            summary_data.append({
                'NF-e': nfe.number or 'S/N',
                'Série': nfe.series or '-',
                'Emitente': nfe.emitter_name or 'Desconhecido',
                'UF': nfe.emitter_uf or 'Desconhecido',
                'Data': nfe.emission_date or '-',
                'Total Itens': len(items),
                'Valor Total': f"R$ {total_value:,.2f}",
                'ICMS Total': f"R$ {total_icms:,.2f}"
            })

        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

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


def render_download_button(df: pd.DataFrame, filename="icms_calculado.xlsx", emitter_name=None, period=None, ie=None, show_button=True):
    if not show_button:
        return

    excel_data = FileHandler.dataframe_to_excel(df, emitter_name, period, ie)

    st.download_button(
        label="📥 Baixar Planilha Excel",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def combine_all_nfes(nfe_list: List[Nfe]) -> pd.DataFrame:
    tax_calculator = TaxCalculator()

    if not nfe_list:
        return pd.DataFrame()

    result = tax_calculator.process_dataframe_taxes(nfe_list)
    return pd.DataFrame(result)


def process_uploaded_file(uploaded_file) -> List[Dict]:
    # Validar arquivo
    if not FileHandler.validate_zip_file(uploaded_file):
        st.error("Arquivo ZIP inválido ou não contém arquivos XML.")
        return []

    # Processar arquivo ZIP
    with st.spinner('Processando NF-Es...'):
        nfe_list:List[Nfe] = XMLProcessor.process_zip_file(uploaded_file)

    if not nfe_list:
        st.error("Não foi possível extrair dados do arquivo.")
        return []

    return nfe_list


def main():
    configure_page()
    render_header()

    # Upload do arquivo
    uploaded_file = render_file_uploader()

    selected_ie = None
    df_filtered = pd.DataFrame()
    filtered_nfes = []

    if uploaded_file is not None:
        nfe_list:List[Nfe] = process_uploaded_file(uploaded_file)

        if nfe_list:
            st.success(f"Processamento concluído! {len(nfe_list)} NF-es encontradas.")
            selected_ie = render_nfe_selector(nfe_list)

            if selected_ie == "all":
                # Mostrar resumo de todas as NF-es
                render_nfe_summary(nfe_list)

                # Combinar todos os itens em um único DataFrame
                df_all = combine_all_nfes(nfe_list)

                if not df_all.empty:
                    render_statistics(df_all)
                    df_to_show = df_all.drop(["MVA_ADJUSTED"], axis=1)
                    df_to_show = df_to_show.rename(columns={"MVA-ST":"MVA"})

                    st.subheader("Todos os Itens")
                    st.dataframe(df_to_show, use_container_width=True)
                    # Não mostrar botão de download para "Todas as Inscrições"

                else:
                    st.warning("Nenhum item encontrado para download.")
            else:
                # Filtrar NF-es pela inscrição estadual selecionada
                filtered_nfes = [nfe for nfe in nfe_list if nfe.ie or 'Desconhecido' == selected_ie]

                # Mostrar resumo das NF-es filtradas
                render_nfe_summary(filtered_nfes)

                if filtered_nfes:
                    # Combinar todos os itens das NF-es filtradas em um único DataFrame
                    df_filtered = combine_all_nfes(filtered_nfes)

                    if not df_filtered.empty:
                        render_statistics(df_filtered)

                        st.subheader("Itens da Inscrição Estadual Selecionada")
                        st.dataframe(df_filtered, use_container_width=True)

                        # Download do arquivo filtrado somente quando uma inscrição específica for selecionada
                        # Extrair mês e ano da data no formato DD/MM/YYYY
                        emission_date = filtered_nfes[0].get('emission_date', '')
                        period = ''
                        if emission_date:
                            # Se a data está no formato DD/MM/YYYY, extraímos MM/YYYY
                            parts = emission_date.split('/')
                            if len(parts) == 3:
                                period = f"{parts[1]}/{parts[2]}"  # MM/YYYY

                        render_download_button(df_filtered, f"inscricao_{selected_ie}_icms.xlsx", 
                                              emitter_name=filtered_nfes[0].get('emitter_name', ''), 
                                              period=period, 
                                              ie=selected_ie)
                else:
                    st.warning("Nenhuma NF-e encontrada para a inscrição estadual selecionada.")

        else:
            st.error("Não foi possível processar os dados do arquivo.")


if __name__ == "__main__":
    main()