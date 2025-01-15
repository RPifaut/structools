import streamlit as st
from structools.streamlit.pages import page_2, page_3
import pandas as pd

def say_hello(name):
    print(f"Hello {name}")


def display_name(name : str):
    st.write(f"Hello: {name}")


def run_app():

    st.title("Streamlit App")
    st.write("This is a Streamlit app module")

    df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    })

    st.table(df)

    x = st.slider('x') 
    st.write(x, 'squared is', x * x)
    
    name = st.text_input("Your name", "name")

    if st.button("Say Hello"):
        if name:
            display_name(name)
        else:
            st.warning("Please enter your name")

    df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
        })

    option = st.selectbox(
        'Which number do you like best?',
        df['first column'])
    
    st.write(f"You selected {option}")

    # Add a selectbox to the sidebar:
    add_selectbox = st.sidebar.selectbox(
        'How would you like to be contacted?',
        ('Email', 'Home phone', 'Mobile phone')
    )

    st.sidebar.write(f"Your selection: {add_selectbox}")

    # Add a slider to the sidebar:
    add_slider = st.sidebar.slider(
        'Select a range of values',
        0.0, 100.0, (25.0, 75.0)
    )

    left_column, right_column = st.columns(2)


    # You can use a column just like st.sidebar:
    left_column.button('Press me!')

    # Or even better, call Streamlit functions inside a "with" block:
    with right_column:
        chosen = st.radio(
            'Sorting hat',
            ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
        st.write(f"You are in {chosen} house!")



if __name__ == "__main__":

    run_app()