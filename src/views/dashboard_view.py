import streamlit as st
from state.state_manager import get_nfe_data, set_nfe_data, clear_state
from core import nfe_logic
from components import header, inputs, metrics, outputs
from services.xml_processor import XMLProcessor
from services.file_handler import FileHandler


def handle_upload_event(uploaded_file):
    if uploaded_file is None:
        clear_state()
        return

    if st.session_state.current_filename != uploaded_file.name:
        if not FileHandler.validate_zip_file(uploaded_file):
            st.error("Arquivo ZIP inválido ou não contém arquivos XML.")
            clear_state()
            return

        with st.spinner("Processando NF-Es..."):
            nfe_list = XMLProcessor.process_zip_file(uploaded_file)

        if not nfe_list:
            st.error("Não foi possível extrair dados do arquivo.")
            clear_state()
            return

        set_nfe_data(nfe_list, uploaded_file.name)
        st.success(f"Processamento concluído! {len(nfe_list)} NF-es encontradas.")


def render_dashboard():
    header.render_header()

    uploaded_file = inputs.render_file_uploader()
    handle_upload_event(uploaded_file)

    if not st.session_state.is_processed:
        return

    nfe_list = get_nfe_data()
    grouped_nfes = nfe_logic.group_nfes_by_ie(nfe_list)

    ie_keys = ["all"] + list(grouped_nfes.keys())
    ie_names = ["Todas as Inscrições"] + [
        f"Inscrição Estadual: {ie}" for ie in grouped_nfes.keys()
    ]
    selected_ie = inputs.render_ie_selector(options=ie_keys, option_names=ie_names)

    if selected_ie == "all":
        for ie, nfes in grouped_nfes.items():
            summary_data = nfe_logic.generate_summary_data(nfes)
            total_items = sum(len(n.items or []) for n in nfes)
            outputs.render_nfe_summary_table(ie, summary_data, len(nfes), total_items)

        df_all = nfe_logic.get_combined_dataframe(nfe_list)
        if not df_all.empty:
            stats = nfe_logic.calculate_dataframe_statistics(df_all)
            metrics.render_statistics_cards(stats)

            df_to_show = nfe_logic.format_dataframe_for_display(df_all)
            outputs.render_detailed_dataframe(df_to_show, "Todos os Itens")
        else:
            st.warning("Nenhum item encontrado.")

    else:
        filtered_nfes = grouped_nfes[selected_ie]
        summary_data = nfe_logic.generate_summary_data(filtered_nfes)
        total_items = sum(len(n.items or []) for n in filtered_nfes)

        outputs.render_nfe_summary_table(
            selected_ie, summary_data, len(filtered_nfes), total_items
        )

        df_filtered = nfe_logic.get_combined_dataframe(filtered_nfes)
        if not df_filtered.empty:
            stats = nfe_logic.calculate_dataframe_statistics(df_filtered)
            metrics.render_statistics_cards(stats)

            outputs.render_detailed_dataframe(
                df_filtered, "Itens da Inscrição Estadual Selecionada"
            )


#            TODO Implementar botão de dataframe para Excel (mo preguiça de fazer isso funcionar agora).
#            emission_date = filtered_nfes[0].emission_date or ""


#            period = nfe_logic.extract_period_from_date(emission_date)
#            emitter_name = filtered_nfes[0].emitter_name or ""
#            filename = f"inscricao_{selected_ie}_icms.xlsx"


#            outputs.render_download_button(
#                df_filtered, filename, emitter_name, period, selected_ie
#            )
