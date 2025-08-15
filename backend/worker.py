# worker.py

from celery import Celery
from celery_config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from pipeline import run_full_pipeline

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery_app.task(name="run_full_pipeline")
def run_pipeline_task(youtube_url, brands, model, email, timestamp):
    print(f"📦 New task started: {youtube_url=} {brands=} {email=}")
    return run_full_pipeline(youtube_url, brands, model, email, timestamp)
