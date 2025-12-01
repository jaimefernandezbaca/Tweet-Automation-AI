import streamlit as st
import json
from datetime import datetime

st.title("Tweet Automation MVP")

api_key = st.text_input("API Key")
api_secret = st.text_input("API Secret")
access_token = st.text_input("Access Token")
access_secret = st.text_input("Access Secret")

tweet = st.text_area("Tweet")
date = st.date_input("Fecha")
time = st.time_input("Hora")

if st.button("Programar tweet"):
    task = {
        "api_key": api_key,
        "api_secret": api_secret,
        "access_token": access_token,
        "access_secret": access_secret,
        "tweet": tweet,
        "run_at": f"{date} {time}"
    }

    with open("tasks.json", "w") as f:
        json.dump(task, f)

    st.success("Tweet programado")
