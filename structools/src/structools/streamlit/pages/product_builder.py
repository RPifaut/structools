import streamlit as st
from datetime import datetime as dt
import numpy as np

from structools.products.autocalls import Underlying, Autocall, Athena, Phoenix, L_OBS_PUT
from structools.products.autocalls import L_CCY
from structools.tools.date_tools import L_FREQ, DICT_MATCH_FREQ, DateModel

L_PROD = ["Athena", "Phoenix"]

def app():

    # Initialisation of the session_variables
    if "dict_prod" not in st.session_state:
        st.session_state.dict_prod={}



    st.title("Product Builder")
    st.write("Use this tool to create custom Autocallable products!")

    # General features
    with st.container(border=True):

        st.subheader("General features")

        type_prod = st.selectbox(label="Select a product type",
                                 options=L_PROD)

        col1, col2 = st.columns(2)

        with col1:
            prod_name = st.text_input(label="Enter the product's name:",
                                      value="Athena 10Y EUR SX5E")
            st.caption("Please use a meaningful name.")

            if prod_name in st.session_state.dict_prod.keys():
                st.warning(f"The product named {prod_name} already exists!")
            else:
                st.success("Product name valid!")

        with col2:
            maturity = st.number_input(label="Choose maturity",
                                       min_value=10,
                                       max_value=12)
            

            
        col1, col2 = st.columns(2)

        with col1:
            # Underlying selection
            undl = st.selectbox(label="Select underlying",
                                options=list(st.session_state.dict_undl.keys()))
            if len(list(st.session_state.dict_undl.keys())) == 0:
                st.warning("""
                            The list of underlying is empty!
                            Create your first underlying!
                            """)
            if len(st.session_state.dict_undl.keys()) != 0:
                underlying = st.session_state.dict_undl[undl]
                st.text(f"Correct type: {isinstance(underlying, Underlying)}")

        with col2:
            currency = st.selectbox(label="Select currency", 
                        options=L_CCY)

    # Recall features
    with st.container(border=True):

        st.subheader("Autocall features")
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            first_trigger = st.number_input(label="Value of the first autocall trigger (%)", 
                                            value=100.0,
                                            min_value=0.0,
                                            step=5.0)
            
        with col2:
            recall_freq = st.selectbox(label="Select an observation frequency",
                                       options=L_FREQ,
                                       index=len(L_FREQ)-1)
            
        N_OBS = DICT_MATCH_FREQ[recall_freq] * maturity
            
        with col3:
            step_down = st.number_input(label="Step Down per period (%)",
                                        value=0.0,
                                        min_value=0.0,
                                        max_value=100/(N_OBS-1) if N_OBS != 1 else 1.00,
                                        step=0.5)
            st.caption(f"Max value: {np.round(100/(N_OBS-1), 3) if N_OBS != 1 else 100}% per period")
            
        with col4:
            start_recall = st.number_input(label="1st Autocall Period",
                                           value=1,
                                           min_value=1, 
                                           max_value=N_OBS)
            
    # Coupon Features
    with st.container(border=True):

        st.subheader("Coupon Features")

        col1, col2, col3 = st.columns(3)

        with col1:
            coupon = st.number_input(label="Enter annual coupon (%)",
                                     value=5.00,
                                     min_value=0.00,
                                     step=1.00)
            
        with col2: 
            if type_prod == "Athena":
                coupon_trigger = st.number_input(label="Coupon trigger (%)",
                                                 value=first_trigger,
                                                 min_value=first_trigger,
                                                 max_value=first_trigger)
            else:
                coupon_trigger = st.number_input(label="Coupon trigger (%)",
                                                 value=80.0,
                                                 min_value=0.0,
                                                 max_value=first_trigger,
                                                 step=5.0)
            st.caption("By default, equal to first trigger for Athena.")

        with col3:

            if type_prod == "Athena":
                is_memory = st.toggle("Memory effect", value=True)
            else:   
                is_memory = st.toggle("Memory effect", False)
            st.caption("Always set to True for Athena products.")

    # Upside participation features
    with st.container(border=True):

        st.subheader("Upside Participation Features")

        col1, col2, col3 = st.columns(3)

        with col1:
            call_strike = st.number_input(label="Call strike (%)",
                                          value=100.0, 
                                          min_value=0.0,
                                          step=1.00)     
            
        with col2:
            call_leverage = st.number_input(label="Call leverage (%)",
                                            value=100.0,
                                            min_value=0.0,
                                            step=1.0)
            
        with col3:
            call_cap = st.number_input(label="Capped Upside (%)",
                                       value=99999.0,
                                       min_value=0.0,
                                       step=1.0)
            st.caption("Cap = Maximum Payoff / Max Performance")


    # Downside protection features
    with st.container(border=True):

        st.subheader("Downside Protection Features")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:

            put_barrier_obs = st.selectbox(label="Barrier observation",
                                           options=L_OBS_PUT
                                           )
            st.caption("AMERICAN: Close-to-Close observation.")
            
        with col2:
            put_strike = st.number_input(label="Put strike (%)",
                                         value=100.0,
                                         min_value=0.0,
                                         step=5.0)
            
        with col3:
            put_barrier = st.number_input(label="Put barrier (%)",
                                          value=70.0, 
                                          min_value=0.0, 
                                          step=5.0)
            st.caption("Set to put_strike for vanilla/geared put")

        with col4:
            put_leverage = st.number_input(label="Put leverage (%)",
                                           value=100.0,
                                           min_value=0.0,
                                           step=5.0)
        
        with col5:
            kg = st.number_input(label="Capital guarantee (%)",
                                 value=0.0,
                                 min_value=0.0,
                                 step=10.0)
            st.caption("Expressed a percentage of the nominal amount.")
            
    st.markdown('-----')

    st.subheader("Product Validation")
    # Product validation and creation
    if st.button("Create product"):

        if type_prod == "Athena":

            product = Athena.from_params(
                strike_date=DateModel(date=dt.today()),
                underlying=st.session_state.dict_undl[undl],
                maturity=maturity,
                currency=currency,
                start_recall=start_recall,
                recall_freq=recall_freq, 
                first_trigger=first_trigger/100, 
                step_down=step_down/100,
                coupon=coupon/100, 
                start_coupon=1, 
                call_strike=call_strike/100,
                call_leverage=call_leverage/100,
                call_cap=call_cap/100,
                put_strike=put_strike/100,
                put_barrier=put_barrier/100,
                put_leverage=put_leverage/100,
                put_barrier_observ=put_barrier_obs,
                kg=kg/100,
            )

        else:

            product = Phoenix.from_params(
                strike_date = DateModel(date=dt.today()),
                underlying=st.session_state.dict_undl[undl],
                maturity=maturity,
                currency=currency,
                start_recall=start_recall,
                recall_freq=recall_freq, 
                first_trigger=first_trigger/100,
                step_down=step_down/100,
                coupon=coupon/100,
                coupon_trigger=coupon_trigger/100,
                start_coupon=1,
                is_memory=is_memory,
                call_strike=call_strike/100,
                call_leverage=call_leverage/100,
                call_cap=call_cap/100,
                put_strike=put_strike/100,
                put_barrier=put_barrier/100,
                put_leverage=put_leverage/100,
                put_barrier_observ=put_barrier_obs,
                kg=kg/100
            )

        st.text(isinstance(product, Autocall))
        st.session_state.dict_prod.update({prod_name : product})
        st.success("Product successfully created!")