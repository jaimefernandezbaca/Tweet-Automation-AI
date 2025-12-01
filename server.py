from fastapi import FastAPI
from runner import main as run_scheduler

app = FastAPI()


@app.get("/run")
def run():
    """
    Endpoint que ejecuta el scheduler.
    EasyCron o cualquier cron externo puede llamar aquí.
    """
    run_scheduler()
    return {"status": "ok"}
