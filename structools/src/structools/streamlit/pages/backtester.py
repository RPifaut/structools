import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go

from src.structools.backtest.backtester import Backtester

def app():
    st.title("Backtester")
    st.write("Use this tool to backtester your products!")

    # Backtest parameters
    with st.container(border=True):

        st.subheader("Backtest Parameters")
        st.text("Structure's features")
        col1, col2, col3 = st.columns(3)

        with col1:
            product = st.selectbox(label="Select a product to backtest",
                                   options = list(st.session_state.dict_prod.keys()))
            if len(list(st.session_state.dict_prod.keys())) == 0:
                st.warning("""
                            The list of products is empty!
                            Create your first underlying!
                            """)
        with col2:
            underlying = st.selectbox(label="Select an underlying",
                                      options=list(st.session_state.dict_undl.keys()))
            if len(list(st.session_state.dict_undl.keys())) == 0:
                st.warning("""
                            The list of products is empty!
                            Create your first underlying!
                            """)
                
        with col3:
            bt_length = st.number_input(label="Backtest duration (years)",
                                        value=10,
                                        min_value=1,
                                        max_value=20,
                                        step=1)

        if st.button(label="Run Backtest"):
            
            # Changing the underlying
            product.setattr("underlying", underlying)

            # Creating the backtester
            backtester = Backtester.init_backtester(product=product,
                                                    backtest_length=bt_length,
                                                    investment_horizon=product.maturity
            )

            # Running the backtest

                
