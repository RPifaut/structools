import streamlit as st
from structools.streamlit.pages import home, underlying_builder, product_builder, backtester


def run_app():


    st.set_page_config(
        page_title="Structools",
        layout="wide"
    )

    # Sidebar configuration
    st.sidebar.title("Structools")
    st.sidebar.header("Navigation:")
    page = st.sidebar.radio("Go to", ["Home", "Underlying Builder", "Product Builder", "Backtester"])

    # Render selected page
    if page == "Home":
        home.app()

    elif page == "Underlying Builder":
        underlying_builder.app()  

    elif page == "Product Builder":
        product_builder.app()

    elif page == "Backtester":
        backtester.app()  
