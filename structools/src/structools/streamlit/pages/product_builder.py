import streamlit as st

def app():

    # Initialisation of the session_variables
    if "dict_prod" not in st.session_state:
        st.session_state.dict_prod={}



    st.title("Product Builder")
    st.write("Use this tool to create custom Autocallable products!")

    # General features
    with st.container(border=True):

        st.subheader("General features")

        col1, col2 = st.columns(2)

        with col1:

            prod_name = st.text_input(label="Enter the product's name:",
                                      value="Athena 10Y EUR SX5E")
            st.caption("Please use a meaningful name.")

            # Underlying selection
            undl = st.selectbox(label="Select underlying",
                                options=list(st.session_state.dict_undl.keys()))

        with col2:

            maturity = st.number_input(label="Choose maturity",
                                       min_value=1)
            
            currency = st.selectbox(label="Select currency")