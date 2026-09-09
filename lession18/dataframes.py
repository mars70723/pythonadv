#import pimport pandas as pd
import streamlit as st


st.header("Displaying data frames")

data = pd.DataFrame({
    'Name':["Resa","Andi","Marsi"],
    'Age':['20','17','16']
})


st.dataframe(data)