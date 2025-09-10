"""Celery worker for background tasks."""

import os
from celery import Celery
from agents_core.config.settings import settings

# Initialize Celery app with dynamic Redis configuration
app = Celery(
    'agent_worker',
    broker=settings.get_redis_url_for_celery(),
    backend=settings.get_redis_url_for_celery(),
    include=['workers.celery_worker.tasks']
)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'workers.celery_worker.tasks.*': {'queue': 'agent_tasks'},
    },
    task_default_queue='agent_tasks',
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=100,
)

if __name__ == '__main__':
    app.start()
