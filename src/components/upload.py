import streamlit as st


def render_file_uploader():
    return st.file_uploader(
        "Selecione o arquivo ZIP com as NF-Es",
        type=["zip"],
        help="O arquivo deve conter arquivos XML de NF-E",
    )
