import streamlit as st
st.sidebar.header("hello")
st.sidebar.write("this is the sidebar")

tab1, tab2, tab3 = st.tabs(["tab1","tab2","tab3"])
with tab1:
    st.header("content of tab 1")
    st.write("This is the content of tab 2")