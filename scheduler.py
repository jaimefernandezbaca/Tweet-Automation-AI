import os
import json
from datetime import datetime
import tweepy

TASKS_FILE = "tasks.json"

if not os.path.exists(TASKS_FILE):
    print("No tasks.json found. Nothing to do.")
    raise SystemExit(0)

with open(TASKS_FILE) as f:
    try:
        task = json.load(f)
    except json.JSONDecodeError:
        print("tasks.json is not valid JSON. Nothing to do.")
        raise SystemExit(0)

if not task:
    print("tasks.json is empty. Nothing to do.")
    raise SystemExit(0)

run_at = datetime.strptime(task["run_at"], "%Y-%m-%d %H:%M:%S")
now = datetime.utcnow()

if now < run_at:
    print(f"Not time yet. run_at={run_at}, now={now}")
    raise SystemExit(0)

auth = tweepy.OAuth1UserHandler(
    task["api_key"],
    task["api_secret"],
    task["access_token"],
    task["access_secret"],
)
api = tweepy.API(auth)
api.update_status(task["tweet"])
print("Tweet enviado")
