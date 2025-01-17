import streamlit as st
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)

from structools.products.basic_products import Underlying, Basket, Index
from structools.tools.date_tools import L_FREQ

def app():



    # Begining of the page
    st.title("Underlying Builder")
    st.write("Use this tool to create custom underlyings!")
    

    with st.container(border=True):
        # Underlying General Parameters
        st.subheader("General Parameters of the Basket")

        undl_type = st.selectbox(
            label="Select Underlying Type",
            options=["Basket", "Index"]
        )

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Enter basket name:", "Basket 1")
            
            # Validation of the basket name
            if name in st.session_state.dict_undl.keys():
                st.warning(f"The underlying named {name} already exists!")
            else:
                st.success("Input name valid!")

        with col2:
            N = st.number_input("Number of components", 1)


        st.markdown('----')

        
        # If the underlying is a Basket
        if undl_type == "Basket":

            col1, col2 = st.columns(2)
            with col1:
                worst = st.toggle(label="Worst-Of",
                        key="wof")
                
                best = st.toggle(label="Best-Of",
                        key="bof")
            with col2:
                NOF = st.number_input("Number of components to observe for the WoF/BoF", 1)
                if NOF > N:
                    st.warning("""The number of observed components cannot be greater than the 
                            number of underlying's components!""")
        
        # The underlying is an Index
        else:
            
            rebal_freq = st.selectbox("Rebalancing Frequency",
                                      options=L_FREQ)
            st.caption("A: Annual, S: Semi-Annual, Q: Quarterly, M: Monthly, W: Weekly")




    with st.container(border=True):
        # Composition
        st.subheader("Components Selection")
        st.text("Please enter the tickers of the components")

        # Editable DataFrame
        df_compo = pd.DataFrame(
            index = [i+1 for i in range(N)],
            columns=["Tickers", "Weights"]
        )
        edited_df = st.data_editor(df_compo, use_container_width=True)
        st.caption("Please make sure you enter valid YahooFinance tickers! URL: https://fr.finance.yahoo.com")

    # Underlying validation
    st.markdown('-----')
    st.subheader("Underlying Validation")
    if st.button("Create my underlying"):
        
        # Generating the product
        if undl_type == "Basket":
            undl = Basket.from_params(size=1_000_000,
                                        name=name,
                                        N=NOF,
                                        worst=worst,
                                        best=best,
                                        compo=list(edited_df["Tickers"].astype(str).values),
                                        weights=edited_df["Weights"].astype(float).values
            )
            st.session_state.dict_undl.update({name: undl})

        elif undl_type == "Index":
            undl = Index.from_params(size=1_000_000,
                                     name=name,
                                     rebal_freq=rebal_freq,
                                     compo=list(edited_df["Tickers"].astype(str).values), 
                                     weights=edited_df["Weights"].astype(float).values)
            st.session_state.dict_undl.update({name: undl})
        
        
        st.success(f"Underlying {name} successfully created!")