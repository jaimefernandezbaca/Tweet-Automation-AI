import os
import json
from datetime import datetime
import requests
import streamlit as st

# Config Supabase desde variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

TABLE_URL = f"{SUPABASE_URL}/rest/v1/scheduled_tweets" if SUPABASE_URL else None


def insert_scheduled_tweet(data: dict):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL o SUPABASE_KEY no están configuradas")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    resp = requests.post(TABLE_URL, headers=headers, data=json.dumps(data))
    if not resp.ok:
        raise RuntimeError(f"Supabase error {resp.status_code}: {resp.text}")


st.title("Tweet Automation MVP")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Configura SUPABASE_URL y SUPABASE_KEY como variables de entorno antes de usar la app.")
else:
    with st.form("tweet_form"):
        st.subheader("Twitter API credentials")
        api_key = st.text_input("API Key")
        api_secret = st.text_input("API Secret")
        access_token = st.text_input("Access Token")
        access_secret = st.text_input("Access Secret")

        st.subheader("Tweet")
        tweet = st.text_area("Tweet text")

        st.subheader("Schedule")
        date = st.date_input("Date")
        time = st.time_input("Time")

        submitted = st.form_submit_button("Schedule tweet")

    if submitted:
        if not all([api_key, api_secret, access_token, access_secret, tweet]):
            st.error("All fields are required.")
        else:
            run_at = datetime.combine(date, time)

            data = {
                "tweet_text": tweet,
                "run_at": run_at.isoformat(),  # timestamptz en Supabase
                "api_key": api_key,
                "api_secret": api_secret,
                "access_token": access_token,
                "access_secret": access_secret,
                "status": "pending"
            }

            try:
                insert_scheduled_tweet(data)
                st.success(f"Tweet scheduled for {run_at}")
            except Exception as e:
                st.error(f"Error saving tweet: {e}")
