import streamlit as st
from typing import List
from models.nfe import Nfe


def init_state():
    if "nfe_list" not in st.session_state:
        st.session_state.nfe_list = []
    if "is_processed" not in st.session_state:
        st.session_state.is_processed = False
    if "current_filename" not in st.session_state:
        st.session_state.current_filename = None


def set_nfe_data(nfe_list: List[Nfe], filename: str):
    st.session_state.nfe_list = nfe_list
    st.session_state.is_processed = True
    st.session_state.current_filename = filename


def get_nfe_data() -> List[Nfe]:
    return st.session_state.nfe_list


def clear_state():
    st.session_state.nfe_list = []
    st.session_state.is_processed = False
    st.session_state.current_filename = None
