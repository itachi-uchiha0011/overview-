import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()


def make_celery():
    broker = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/3")
    backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/4")
    celery = Celery("overview", broker=broker, backend=backend)
    celery.conf.timezone = "UTC"
    return celery


celery_app = make_celery()