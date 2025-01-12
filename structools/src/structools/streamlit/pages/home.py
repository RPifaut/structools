import streamlit as st
from src.structools.streamlit.pages import underlying_builder, backtester


def app():

    st.title("Welcome to Structools")
    st.text("An innovative platorm designed to help structurers make there life easier.")

    st.text("Please use the side bar on the left to navigate through the tool!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create my underlying"):
            st.session_state.page="underlying_builder"
    
    with col2:
        if st.button("Run my backtest"):
            st.session_state.page="backtester"

        