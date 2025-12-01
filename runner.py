import os
import json
from datetime import datetime, timezone

import requests
import tweepy

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL o SUPABASE_KEY no están configuradas")

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
    # Tweepy Client → API v2 (esto es lo que te funciona con plan Free)
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
