import streamlit as st
from state.state_manager import init_state
from views.dashboard_view import render_dashboard


def configure_page():
    st.set_page_config(
        page_title="Calculadora ICMS - NF-E",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto",
    )


def main():
    configure_page()
    init_state()
    render_dashboard()


if __name__ == "__main__":
    main()
