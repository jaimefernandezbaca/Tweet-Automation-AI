import streamlit as st
from datetime import datetime
import requests
import json

# CONFIG: pon aquí tus valores de Supabase
SUPABASE_URL = "https://cmkmvcggrqgszjxktdjl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNta212Y2dncnFnc3pqeGt0ZGpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2MDc2ODIsImV4cCI6MjA4MDE4MzY4Mn0.GFBiWRG7INp10I8cg8XydLe8oyXCx7jvYiiKlyvfHf0"


# Endpoint REST de la tabla
TABLE_URL = f"{SUPABASE_URL}/rest/v1/scheduled_tweets"

def insert_scheduled_tweet(data: dict):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    resp = requests.post(TABLE_URL, headers=headers, data=json.dumps(data))
    if not resp.ok:
        raise RuntimeError(f"Supabase error {resp.status_code}: {resp.text}")

st.title("Tweet Automation MVP (Supabase REST)")

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
        st.error("All fields are required")
    else:
        # combinamos fecha y hora
        run_at = datetime.combine(date, time)

        data = {
            "tweet_text": tweet,
            "run_at": run_at.isoformat(),  # timestamptz
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
