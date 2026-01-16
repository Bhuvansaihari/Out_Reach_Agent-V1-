"""
Celery application configuration for Out_Reach_Agent notification system
"""
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery app
celery_app = Celery(
    'webhook_receiver',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    include=['webhook_receiver.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
    result_expires=7200,  # Task results expire after 2 hours
)

if __name__ == '__main__':
    celery_app.start()
