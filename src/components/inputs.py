import streamlit as st
from typing import List


def render_file_uploader():
    return st.file_uploader(
        "Selecione o arquivo ZIP com as NF-Es",
        type=["zip"],
        help="O arquivo deve conter arquivos XML de NF-E",
    )


def render_ie_selector(options: List[str], option_names: List[str]) -> str:
    selected_idx = st.selectbox(
        "Selecione a Inscrição Estadual para visualizar:",
        range(len(option_names)),
        format_func=lambda i: option_names[i],
    )
    return options[selected_idx]
