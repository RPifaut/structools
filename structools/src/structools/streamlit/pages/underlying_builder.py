import streamlit as st

def app():

    st.title("Underlying Builder")
    st.write("Use this tool to create custom underlyings!")
    
    # Enter basket parameters
    st.markdown('-----')
    st.subheader("General Parameters of the Basket")

    col1, col2 = st.columns(2)
    with col1:
        basket_name = st.text_input("Enter basket name:", "Basket 1")
        
    with col2:
        N = st.number_input("Number of parameters", 1)

    st.markdown('-----')