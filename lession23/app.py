import streamlit as st
import pandas as pd
import requests

st.title("Person management App")
st.header("Create a Developer")
dev_experience = st.number_input("Experience (years)", min_value=0, max_value=50, step=0)

if st.button("Create Developer"):
    dev_data = {"name":dev_name, "experience":dev_experience}
    response = requests.post("http://localhost:8000/developers", json=dev_data)
    st.json(response.json())

st.header("Create a Project")
proj_title = st.text_input("Project Title")
proj_desc = st.text_area("Project Description")
proj_langs = st.text_input("Languages Used (comma-separated)")
lead_dev_name = st.text_input("LeadDeveloper Name")
lead_dev_exp = st.number_input("Developer Experience (years)", min_value=0, max_value=50, step=0)

if st.button("Create Project"):
    lead_dev_data = {"name": dev_name, "experience": dev_experience}
    proj_data= {
        "title": proj_title,
        "description": proj_desc,
        "language": proj_langs.split(","),
        "lead_developer": lead_dev_data
    }
    response = requests.post("http://localhost:8000/projects", json=proj_data)
    st.json(response.json())





    