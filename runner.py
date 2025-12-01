from datetime import datetime, timezone
import requests
import json
import tweepy


# CONFIG: mismos valores que en app.py
SUPABASE_URL = "https://cmkmvcggrqgszjxktdjl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNta212Y2dncnFnc3pqeGt0ZGpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2MDc2ODIsImV4cCI6MjA4MDE4MzY4Mn0.GFBiWRG7INp10I8cg8XydLe8oyXCx7jvYiiKlyvfHf0"


TABLE_URL = f"{SUPABASE_URL}/rest/v1/scheduled_tweets"

def get_pending_tweets():
    now_utc = datetime.now(timezone.utc).isoformat()

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    params = {
        "select": "*",
        "status": "eq.pending",
        "run_at": f"lte.{now_utc}",
    }

    resp = requests.get(TABLE_URL, headers=headers, params=params)
    if not resp.ok:
        raise RuntimeError(f"Supabase error {resp.status_code}: {resp.text}")

    return resp.json()

def mark_status(tweet_id: str, status: str):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    url = f"{TABLE_URL}?id=eq.{tweet_id}"
    data = {"status": status}

    resp = requests.patch(url, headers=headers, data=json.dumps(data))
    if not resp.ok:
        print(f"Error updating status for {tweet_id}: {resp.status_code} {resp.text}")

def send_tweet(row: dict):
    # Tweepy Client (API v2)
    client = tweepy.Client(
        consumer_key=row["api_key"],
        consumer_secret=row["api_secret"],
        access_token=row["access_token"],
        access_token_secret=row["access_secret"],
    )

    resp = client.create_tweet(text=row["tweet_text"])
    print("X API v2 response:", resp)


def main():
    tweets = get_pending_tweets()
    if not tweets:
        print("No pending tweets.")
        return

    for row in tweets:
        tid = row["id"]
        try:
            print(f"Sending tweet {tid}")
            send_tweet(row)
            mark_status(tid, "sent")
            print("OK")
        except Exception as e:
            print(f"Error sending {tid}: {e}")
            mark_status(tid, "failed")

if __name__ == "__main__":
    main()
