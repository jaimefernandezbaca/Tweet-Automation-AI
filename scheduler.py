import os, json
from datetime import datetime
import tweepy

TASKS_FILE = "tasks.json"

# 1. Si no existe tasks.json, no hacemos nada
if not os.path.exists(TASKS_FILE):
    print("tasks.json missing — nothing to do.")
    raise SystemExit(0)

# 2. Cargar JSON
with open(TASKS_FILE) as f:
    try:
        task = json.load(f)
    except:
        print("Invalid JSON — nothing to do.")
        raise SystemExit(0)

# 3. Si está vacío o falta run_at, no hacemos nada
if not task or "run_at" not in task:
    print("No scheduled task.")
    raise SystemExit(0)

# 4. Validar fecha
try:
    run_at = datetime.strptime(task["run_at"], "%Y-%m-%d %H:%M:%S")
except:
    print(f"Invalid run_at format: {task['run_at']}")
    raise SystemExit(0)

now = datetime.utcnow()

# 5. Si aún no toca, salimos
if now < run_at:
    print(f"Not time yet. run_at={run_at}, now={now}")
    raise SystemExit(0)

# 6. Ejecutar tweet
auth = tweepy.OAuth1UserHandler(
    task["api_key"],
    task["api_secret"],
    task["access_token"],
    task["access_secret"],
)

api = tweepy.API(auth)
api.update_status(task["tweet"])
print("Tweet enviado.")
