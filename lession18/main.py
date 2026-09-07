import streamlit as st

st.title("Hello")
st.button("Click me")
if st.button("hello"):
    st.write("button clicked")
if st.button("button3"):
    st.success("succes")