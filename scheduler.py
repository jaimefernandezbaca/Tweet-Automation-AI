import json
import tweepy
from datetime import datetime

with open("tasks.json") as f:
    task = json.load(f)

run_at = datetime.strptime(task["run_at"], "%Y-%m-%d %H:%M:%S")
now = datetime.utcnow()

if now >= run_at:
    auth = tweepy.OAuth1UserHandler(
        task["api_key"],
        task["api_secret"],
        task["access_token"],
        task["access_secret"]
    )
    api = tweepy.API(auth)
    api.update_status(task["tweet"])
    print("Tweet enviado")
else:
    print("Aún no toca")
