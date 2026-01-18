"""
Celery application configuration for Out_Reach_Agent notification system
"""
from celery import Celery
from config import get_celery_broker_url, get_celery_result_backend

# Initialize Celery app
celery_app = Celery(
    'webhook_receiver',
    broker=get_celery_broker_url(),
    backend=get_celery_result_backend(),
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
