import streamlit as st
from structools.streamlit.pages import underlying_builder, backtester


def app():

    # Initialisation of the parameters
    if "wof" not in st.session_state:
        st.session_state.wof = False
    if "bof" not in st.session_state:
        st.session_state.bof = False
    if "dict_undl" not in st.session_state:
        st.session_state.dict_undl={}
    if "dict_prod" not in st.session_state:
        st.session_state.dict_prod={}
    if "dict_bt_res" not in st.session_state:
        st.session_state.dict_bt_res = {}

    st.title("Welcome to Structools")
    st.text("An innovative platorm designed to help structurers make there life easier.")

    st.subheader("How does it work?")
    st.markdown('''
            
            Just follow those 3 simple steps:

            - Create your own underlyings using the Underlying Builder.
            - Then create your Autocallable product. It does not matter how far-fetched your structure is, just describe it, we will backtest it for you!
            - Head over to the backtester where you can chose the combination of product and underlying to backtest.
            - Let the magic do the rest!
            - Download your backtest results as excel file for further analysis!
                

            *Notes*
            - *Supported products to this date: Athena, Phoenix*
            - *Supported underlyings:*
                - *Baskets*
                    - *Custom weights*
                    - *Worst-Of (Equally weighted of the K worst performing assets among K < N components*
                    - *Best-Of (Equally weighted of the K best performing assets among K < N components*

                - *Indices*
                    - Generate indices with any standard rebalancing frequencies!
            
            ''')

    st.text("Please use the side bar on the left to navigate through the tool!")
    st.text("Happy backtesting!")

    st.markdown('''
            
            READ BEFORE USE:
            You may have to create several underlyings/products to make sure they are valid. Please make sure that:
            - The underlying type is True in the Product Builder.
            - Both the product and underlying types are True in the Backtester.

            If not, please select another one, or simply create a new underlying/product.
  
            ''')
