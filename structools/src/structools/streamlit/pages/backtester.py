import streamlit as st
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime as dt


from structools.backtest.backtester import Backtester
from structools.tools.date_tools import DateModel
from structools.products.autocalls import Autocall
from structools.products.basic_products import Underlying

def app():

    # Initilisation of the session state variables
    if "dict_bt_res" not in st.session_state:
        st.session_state.dict_bt_res = {}


    
    st.title("Backtester")
    st.write("Use this tool to backtester your products!")

    # Backtest parameters
    with st.container(border=True):

        st.header("Backtest Parameters")

        bt_name = st.text_input(label="Backtest name", 
                                value=f"{DateModel(date=dt.today()).to_str()}-Backtest_1")
        st.caption("Please use meaningful names.")

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
                
            if len(st.session_state.dict_prod.keys()) != 0:
                product=st.session_state.dict_prod[product]

        with col2:
            underlying = st.selectbox(label="Select an underlying",
                                      options=list(st.session_state.dict_undl.keys()))
            if len(list(st.session_state.dict_undl.keys())) == 0:
                st.warning("""
                            The list of products is empty!
                            Create your first underlying!
                            """)

            if len(st.session_state.dict_undl.keys()) != 0:
                underlying = st.session_state.dict_undl[underlying]
        

                
        with col3:
            bt_length = st.number_input(label="Backtest duration (years)",
                                        value=10,
                                        min_value=1,
                                        max_value=20,
                                        step=1)
            
        st.text(f"Correct type product: {isinstance(product, Autocall)}")
        st.text(f"Correct type underlying: {isinstance(underlying, Underlying)}")

        if st.button(label="Run Backtest"):
            
            # Changing the underlying
            product.set_parameter("underlying", underlying)

            # Creating the backtester
            backtester = Backtester.init_backtester(product=product,
                                                    backtest_length=bt_length,
                                                    investment_horizon=product.maturity
            )

            # Running the backtest
            begin_time = time.time()
            dict_res = backtester.backtest_autocall()
            end_time = time.time()
            exec_time = end_time - begin_time
            dict_res.update({"Execution time": exec_time})


            st.session_state.dict_bt_res.update({bt_name: dict_res})
            st.success("Backtest completed")


    if len(list(st.session_state.dict_bt_res.keys())) != 0:

        with st.container(border=True):

            st.header(f"Backtest results - {bt_name}")

            # Retrieve backtest results
            dict_res = st.session_state.dict_bt_res[bt_name]
            bt_prod = dict_res["Product"]   

            st.markdown('----')
            # General parameters of the backtest
            col1, col2, col3 = st.columns(3)

            with col1:
                st.text(f"Number of trajectories: {dict_res['Number of trajectories']}")
            
            with col2:
                st.text(f"First launching date: {dict_res['Data']['Dates'][0, 0]}")
            
            with col3:
                st.text(f"Last launching date: {dict_res['Data']['Dates'][-1, 0]}")
        
            
            st.markdown('----')
            # Plot the underlying track
            arr_dates = np.array([d.date() for d in dict_res["Underlying Track"].index])
            col1, col2 = st.columns(2)

            with col1:
                start_date = st.selectbox(label="Plot's start date",
                                        options=arr_dates)
                
            with col2:
                arr_poss_dates = arr_dates[np.searchsorted(arr_dates, start_date)+1:]
                end_date = st.selectbox(label="Plot's last date",
                                        options=arr_poss_dates,
                                        index=len(arr_poss_dates)-1)
            
            

            with_compo = st.toggle(label="Display components performance")
            fig_track = bt_prod.underlying.plot_track(start_date=DateModel(date=start_date),
                                     end_date=DateModel(date=end_date),
                                     df_perf=None,
                                     df_track=None,
                                     with_compo = with_compo
            )
            fig_track.update_layout(
                xaxis_title="Dates",
                yaxis_title="Performance",
                showlegend=True
            )

            st.subheader(f"Underlying performance from {start_date} to {end_date}")
            st.plotly_chart(fig_track)


            # Autocall Probabilities
            st.subheader("Autocall Probabilities Distribution")
            arr_ac_proba = dict_res["Recall Probabilities"]
            df_ac_proba = pd.DataFrame(
                index=["Autocall Proba"],
                columns=[f"Period {int(i)}" for i in arr_ac_proba[0, :]],
                data=[arr_ac_proba[1, :]]
            )
            df_ac_proba_disp = df_ac_proba.astype(float).mul(100).round(3).astype(str) + '%'
            st.table(df_ac_proba_disp)

            # Plotting Proba
            fig_proba = px.bar(df_ac_proba.loc["Autocall Proba"])
            fig_proba.update_layout(
                xaxis_title="Dates",
                yaxis_title="Autocall Probability",
                showlegend=True
            )
            st.plotly_chart(fig_proba)

            # IRR Statistics
            st.header("IRR Statistics")
            dict_irr = dict_res["IRR Stats"]
            df_irr = pd.DataFrame(
                index=["IRR"],
                columns=list(dict_irr.keys()),
                data=[dict_irr.values()]
            )

            df_irr = df_irr.astype(float).mul(100).round(3).astype(str) + '%'

            st.table(df_irr)






                
