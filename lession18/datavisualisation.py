from streamlit import title

import pandas as pd
import streamlit as st
import plotly.express as px

data = pd.read_cvs("data.cvs")

st.title("Bestselling Books Analysis")
st.write("This app analyzes the Amazon top selling books from 2009 to 2022")

st.subheader("Summary statistics")

total_books = data.shape[0]
unique_titles = data['Name'].nunique()
avg_rating = data['User Rating'].mean()
avg_price = data['Price'].mean()

col1,col2,col3,col4=st.columns(4)
col1.metric("Total books", total_books)
col2.metric("Unique Titles",unique_titles)
col3.metric("Average rating", avg_rating)
col4.metric("Average price", avg_price)

st.subheader("Data set Preview")
st.write(data.head())

col1,col2 = st.columns(2)
with col1:
    st.subheader("Top 10 book titles")
    top_titles = data["Name"].value_counts.head(10)
    st.bar_chart(top_titles)
with col2:
    st.subheader("Top 10 book titles")
    top_titles = data["Author"].value_counts.head(10)
    st.bar_chart(top_titles)

st.subheader("Zhandrri")

fig = px.pie(data,names="Genre", title="Zhandrrent ma te preferume")
st.plotly_chart(fig)






